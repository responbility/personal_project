import struct
p = 'assets/ratking.png'
with open(p,'rb') as f:
    b = f.read()
# PNG IHDR chunk is at bytes 16..23 (big endian)
w, h = struct.unpack('>II', b[16:24])
print(w, h)

