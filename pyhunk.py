#!/usr/bin/env python3
import struct
import sys
import os
import string

HUNK_HEADER =        0x3F3
HUNK_UNIT =          0x3E7
HUNK_CODE =          0x3E9
HUNK_DATA =          0x3EA
HUNK_BSS =           0x3EB
HUNK_RELOC32 =       0x3EC
HUNK_DREL32 =        0x3F7
HUNK_SYMBOL =        0x3F0
HUNK_END =           0x3F2

def read32(fp):
    raw = fp.read(4)
    # add checks for EOF
    return struct.unpack(">L",raw)[0]


def read16(fp):
    raw = fp.read(2)
    # add checks for EOF
    return struct.unpack(">L",raw)[0]


def readData(numdata, fp):
    fp.seek(numdata, os.SEEK_CUR)


def blockhunk(fp):
    sz = read32(fp)
    # TODO: format it nicely
    print("Size in long words = " + str(sz))
    readData(sz * 4, fp)

def bsshunk(fp):
    print("Allocable memory = " + read32(fp))
    return 0

def reloc32hunk(fp):
    while(1):
        numoffs = read32(fp)
        if numoffs == 0:
            return 0
        print("Number of Offsets = " + str(numoffs))
        numhunks = read32(fp)
        print("Numbers of hunk = " + str(numhunks))
        readData(numoffs * 4, fp)

def reloc16hunk(fp):
    while(1):
        numoffs = read16(fp)
        if numoffs == 0:
            if (fp.tell % 4 != 0):
                read16(fp)
                return 0
        print("Number of Offsets = " + numoffs)
        numhunks = read16(fp)
        print("Numbers of hunk = "+ numhunks)
        readData(numoffs * 2, fp)

def symbolhunk(fp):
    strsz = 0
    while ((strsz := read32(fp)) != 0):
        strsz+=1
        for i in range(0, strsz):
            fp.read(0,ch0,1)
            fp.read(0,ch1,1)
            fp.read(0,ch2,1)
            fp.read(0,ch3,1)
            if (isprint(ch0)):
                print("%c"% ch0)
            else:
                print(" ");
            if (isprint(ch1)):
                print("%c"% ch1)
            else:
                print(" ");
            if (isprint(ch2)):
                print("%c"% ch2)
            else:
                print(" ");
            if (isprint(ch3)):
                print("%c"% ch3)
            else:
                print(" ");
        print("\n")
    return 0

def hunkformat(tp, lwsize, fp):
    print("Position = %d" % (fp.tell() - 4))
    if (tp == 0):
        print("Null Hunk")
        fp.close()
        sys.exit(2)
    elif (tp == HUNK_CODE):
        print("HUNK_CODE (0x%X)"% tp)
        return blockhunk(fp)
    elif (tp == HUNK_DATA):
        print("HUNK_DATA (0x%X)"% tp)
        return blockhunk(fp);
    elif (tp == HUNK_BSS):
        print("HUNK_BSS (0x%X)"% tp)
        return bsshunk(fp);
    elif (tp == HUNK_RELOC32):
        print("HUNK_RELOC32 (0x%X)"% tp)
        return reloc32hunk(fp)
    elif (tp == HUNK_SYMBOL):
        print("HUNK_SYMBOL (0x%X)"% tp)
        return symbolhunk(fp)
    elif (tp == HUNK_DREL32):
        print("HUNK_DREL32 (0x%X)"% tp)
        return reloc16hunk(fp)
    elif (tp == HUNK_END):
        print("HUNK_END (0x%X)" % tp)
        return 1;
    else:
        print("UNKNOWN HUNK TYPE (0x%X)" % tp)
        fp.close()
        sys.exit(2)
    return 0

hunksize = []

def main():
    print("\nPyHunk v0.1 (c) 2021 Athanasios Kostopoulos")
    if len(sys.argv) != 2:
        print("Usage: %s file\n"% sys.argv[0])
        sys.exit(1);

    fp = open(sys.argv[1], "rb");
    # TODO: error handling
    fp.seek(0, os.SEEK_END)
    fsize = fp.tell()
    fp.seek(0, os.SEEK_SET)

    magic = read32(fp)
    string = read32(fp)

    if (magic == HUNK_UNIT):
        print("HUNK_UNIT FOUND")
        fp.close()
        sys.exit(2)

    if (magic != HUNK_HEADER ):
        print("Incorrect Hunk Magic Cookie\nExpected: %X Found %X" %( HUNK_HEADER, magic))
        fp.close()
        sys.exit(1)

    if (string != 0):
        print("HEADER STRING IS NOT NULL: %X"% string)
        fp.close()
        sys.exit(2);

    print("-------------------------------------------")
    print("HUNK HEADER :")
    print("-------------------------------------------")

    print("File size = %ld bytes"% fsize)

    numhunks = read32(fp)

    print("Number of hunks = %d"% numhunks);

    print("Number of first hunk = %d"% read32(fp))
    print("Number of last hunk = %d"% read32(fp))

    for i in range(0, numhunks):
        hunksize.append(read32(fp))
        print("Size of %d hunk = %lu"% (i, hunksize[i]))

    print("-------------------------------------------")

    i = 0;

    print("HUNK NUMBER %d :"% i)
    print("-------------------------------------------")

    while (i < numhunks):
        hunktype = read32(fp)
        if (hunkformat(hunktype, hunksize[i], fp)):
            i+=1
            print("-------------------------------------------")
            print("HUNK NUMBER %d :" % i)

        print("-------------------------------------------")

    print("Happy end at file position = %ld\n"% fp.tell())
    fp.close()


if __name__ == "__main__":
    main()
