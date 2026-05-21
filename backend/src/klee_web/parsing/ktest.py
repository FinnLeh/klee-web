# ===-- ktest.py ----------------------------------------------------------===##
#
#                      The KLEE Symbolic Virtual Machine
#
#  This file is distributed under the University of Illinois Open Source
#  License. See LICENSE.TXT for details.
#
# ===----------------------------------------------------------------------===##
#
# Vendored from KLEE 3.2: tools/ktest-tool/ktest-tool, trimmed to the parser
# pieces we need (header check, version handling, object enumeration). CLI
# (main, argparse), pretty-printer (__format__) and extract() removed.
#
# ===----------------------------------------------------------------------===##

import struct


version_no = 3


class KTestError(Exception):
    pass


class KTest:
    @staticmethod
    def fromfile(path):
        with open(path, "rb") as f:
            hdr = f.read(5)
            if len(hdr) != 5 or (hdr != b"KTEST" and hdr != b"BOUT\n"):
                raise KTestError("unrecognized file")
            (version,) = struct.unpack(">i", f.read(4))
            if version > version_no:
                raise KTestError("unrecognized version")
            (numArgs,) = struct.unpack(">i", f.read(4))
            args = []
            for _ in range(numArgs):
                (size,) = struct.unpack(">i", f.read(4))
                args.append(f.read(size).decode("ascii"))

            if version >= 2:
                (symArgvs,) = struct.unpack(">i", f.read(4))
                (symArgvLen,) = struct.unpack(">i", f.read(4))
            else:
                symArgvs = 0
                symArgvLen = 0

            (numObjects,) = struct.unpack(">i", f.read(4))
            objects = []
            for _ in range(numObjects):
                (size,) = struct.unpack(">i", f.read(4))
                name = f.read(size).decode("utf-8")
                (size,) = struct.unpack(">i", f.read(4))
                data = f.read(size)
                objects.append((name, data))

        return KTest(version, path, args, symArgvs, symArgvLen, objects)

    def __init__(self, version, path, args, symArgvs, symArgvLen, objects):
        self.version = version
        self.path = path
        self.symArgvs = symArgvs
        self.symArgvLen = symArgvLen
        self.args = args
        self.objects = objects