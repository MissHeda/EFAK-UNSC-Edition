"""Minimal uncompressed PBO writer: make_pbo.py <src dir> <out.pbo> <prefix>"""
import hashlib, os, struct, sys, time
src, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
files = []
for root, _, names in os.walk(src):
    for n in sorted(names):
        full = os.path.join(root, n)
        files.append((os.path.relpath(full, src).replace("/", "\\"), open(full, "rb").read()))
h = bytearray(b"\0" + struct.pack("<5I", 0x56657273, 0, 0, 0, 0))
h += b"prefix\0" + prefix.encode() + b"\0\0"
for name, data in files:
    h += name.encode() + b"\0" + struct.pack("<5I", 0, len(data), 0, int(time.time()), len(data))
h += b"\0" + struct.pack("<5I", 0, 0, 0, 0, 0)
body = bytes(h) + b"".join(d for _, d in files)
open(out, "wb").write(body + b"\0" + hashlib.sha1(body).digest())
print("pbo", out, len(files), "files")
