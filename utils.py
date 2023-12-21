import importlib
from struct import unpack, pack


def getPaletteFromName(palette_name):
    palette_module_name = "..{0}pal".format(palette_name.lower())
    palette = importlib.import_module(palette_module_name, __name__).palette
    return palette


# File reading and writing utils
# Reading
def read_byte(self, count=1):
    size = 1 * count
    data = self.file.read(size)
    data = unpack("<%dB" % count, data)
    if count == 1:
        return data[0]
    return data


def read_int(self, count=1):
    size = 4 * count
    data = self.file.read(size)
    data = unpack("<%di" % count, data)
    if count == 1:
        return data[0]
    return data


def read_ushort(self, count=1):
    size = 2 * count
    data = self.file.read(size)
    data = unpack("<%dH" % count, data)
    if count == 1:
        return data[0]
    return data


def read_float(self, count=1):
    size = 4 * count
    data = self.file.read(size)
    data = unpack("<%df" % count, data)
    if count == 1:
        return data[0]
    return data


def read_bytes(self, size):
    return self.file.read(size)


def read_string(self, size):
    data = self.file.read(size)
    s = ""
    for c in data:
        s = s + chr(c)
    return s


# Writing
def write_byte(self, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    self.file.write(pack(("<%dB" % len(data)), *data))


def write_int(self, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    self.file.write(pack(("<%di" % len(data)), *data))


def write_float(self, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    self.file.write(pack(("<%df" % len(data)), *data))


def write_bytes(self, data, size=-1):
    if size == -1:
        size = len(data)
    self.file.write(data[:size])
    if size > len(data):
        self.file.write(bytes(size - len(data)))


def write_string(self, data, size=-1):
    data = data.encode()
    self.write_bytes(data, size)
