import importlib
from struct import unpack, pack


def getPaletteFromName(palette_name):
    palette_module_name = "..{0}pal".format(palette_name.lower())
    palette = importlib.import_module(palette_module_name, __name__).palette
    return palette


# File reading and writing utils
# Reading
def read_byte(file, count=1):
    size = 1 * count
    data = file.read(size)
    data = unpack("<%dB" % count, data)
    if count == 1:
        return data[0]
    return data


def read_int(file, count=1):
    size = 4 * count
    data = file.read(size)
    data = unpack("<%di" % count, data)
    if count == 1:
        return data[0]
    return data


def read_ushort(file, count=1):
    size = 2 * count
    data = file.read(size)
    data = unpack("<%dH" % count, data)
    if count == 1:
        return data[0]
    return data


def read_float(file, count=1):
    size = 4 * count
    data = file.read(size)
    data = unpack("<%df" % count, data)
    if count == 1:
        return data[0]
    return data


def read_bytestring(file, size):
    return file.read(size)


def read_string(file, size):
    data = file.read(size)
    s = ""
    for c in data:
        s = s + chr(c)
    return s


# Writing
def write_byte(file, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    file.write(pack(("<%dB" % len(data)), *data))


def write_int(file, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    file.write(pack(("<%di" % len(data)), *data))


def write_float(file, data):
    if not hasattr(data, "__len__"):
        data = (data,)
    file.write(pack(("<%df" % len(data)), *data))


def write_bytestring(file, data, size=-1):
    if size == -1:
        size = len(data)
    file.write(data[:size])
    if size > len(data):
        file.write(bytes(size - len(data)))


def write_string(file, data, size=-1):
    data = data.encode()
    write_bytestring(file, data, size)
