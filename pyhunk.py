#!/usr/bin/env python3
import struct
import sys
import os
import string

# http://amiga-dev.wikidot.com/file-format:hunk#toc0
HUNK_HEADER =        0x03F3
HUNK_UNIT =          0x03E7
HUNK_CODE =          0x03E9
HUNK_DATA =          0x03EA
HUNK_BSS =           0x03EB
HUNK_RELOC32 =       0x03EC
HUNK_DREL32 =        0x03F7
HUNK_SYMBOL =        0x03F0
HUNK_END =           0x03F2
HUNK_DEBUG =         0x03F1

def read32(fp):
    raw = fp.read(4)
    if len(raw) < 4:
        print("read32 reached EOF unexpectedly")
        fp.close()
        sys.exit(2)
    return struct.unpack(">L",raw)[0]


def read16(fp):
    raw = fp.read(2)
    if len(raw) < 2:
        print("read16 reached EOF unexpectedly")
        fp.close()
        sys.exit(2)
    return struct.unpack(">L",raw)[0]


def readData(numdata, fp):
    fp.seek(numdata, os.SEEK_CUR)


def blockhunk(fp):
    sz = read32(fp)
    # TODO: format it nicely
    print("Size in long words = " + str(sz))
    readData(sz * 4, fp)

def bsshunk(fp):
    print("Allocable memory = " + str(read32(fp)))
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
        print("Number of Offsets = " + str(numoffs))
        numhunks = read16(fp)
        print("Numbers of hunk = "+ str(numhunks))
        readData(numoffs * 2, fp)

def symbolhunk(fp):
    printable_chars = set(bytes(string.printable, 'ascii'))
    strsz = 0
    while ((strsz := read32(fp)) != 0):
        strsz+=1
        for i in range(0, strsz):
            sym = fp.read(4)
            for ch in sym:
                # TODO: here be dragons
                if ch in printable_chars:
                    print(chr(ch), end = '')
    print()
    return 0


def debughunk(fp):
    # does the bare minimum
    length = read32(fp)
    _ = read32(fp)
    debugType = read32(fp)
    readData((length * 4) - 8, fp)

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
    elif (tp == HUNK_DEBUG):
        print("HUNK_DEBUG (0x%X)" % tp)
        return debughunk(fp)
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

    try:
        fp = open(sys.argv[1], "rb")
    except FileNotFoundError:
        print("%s - file not found" % sys.argv[1])
        sys.exit(2)
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
        print("Incorrect Hunk Magic Cookie\nExpected: 0x%X Found 0x%X" %( HUNK_HEADER, magic))
        fp.close()
        sys.exit(1)

    if (string != 0):
        print("HEADER STRING IS NOT NULL: 0x%X"% string)
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
