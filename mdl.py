# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from struct import unpack, pack
from .constants import MDLEffects, MDLSyncType
from .utils import read_byte, read_bytestring, read_float, read_int, read_string, read_ushort, write_byte, write_bytestring, write_float, write_int, write_string


class MDL:
    class Skin:
        def __init__(self):
            self.name = ''

        def info(self):
            info = {}
            if self.type:
                if self.times:
                    info['intervals'] = list(map(lambda t: str(t), self.times))
                info['skins'] = []
                for s in self.skins:
                    info['skins'].append(s.info())
            if self.name:
                info['name'] = self.name
            return info

        def read(self, mdl, sub=0):
            self.width, self.height = mdl.skinwidth, mdl.skinheight
            if sub:
                self.type = 0
                self.read_pixels(mdl)
                return self
            self.type = read_int(mdl.file)
            if self.type:
                # skin group
                num = read_int(mdl.file)
                self.times = read_float(mdl.file, num)
                self.skins = []
                for _ in range(num):
                    self.skins.append(MDL.Skin().read(mdl, 1))
                    num -= 1
                return self
            self.read_pixels(mdl)
            return self

        def write(self, mdl, sub=0):
            if not sub:
                write_int(mdl.file, self.type)
                if self.type:
                    write_int(mdl.file, len(self.skins))
                    write_float(mdl.file, self.times)
                    for subskin in self.skins:
                        subskin.write(mdl, 1)
                    return
            write_bytestring(mdl.file, self.pixels)

        def read_pixels(self, mdl):
            size = self.width * self.height
            self.pixels = read_bytestring(mdl.file, size)

    class STVert:
        def __init__(self, st=None, onseam=False):
            if not st:
                st = (0, 0)
            self.onseam = onseam
            self.s, self.t = st
            pass

        def read(self, mdl):
            self.onseam = read_int(mdl.file)
            self.s, self.t = read_int(mdl.file, 2)
            return self

        def write(self, mdl):
            write_int(mdl.file, self.onseam)
            write_int(mdl.file, (self.s, self.t))

    class Tri:
        def __init__(self, verts=None, facesfront=True):
            if not verts:
                verts = (0, 0, 0)
            self.facesfront = facesfront
            self.verts = verts

        def read(self, mdl):
            self.facesfront = read_int(mdl.file)
            self.verts = read_int(mdl.file, 3)
            return self

        def write(self, mdl):
            write_int(mdl.file, self.facesfront)
            write_int(mdl.file, self.verts)

    class NTri:
        def __init__(self, verts=None, facesfront=True, stverts=None):
            if not verts:
                verts = (0, 0, 0)
            if not stverts:
                stverts = (0, 0, 0)

            self.facesfront = facesfront
            self.verts = verts
            self.stverts = stverts

        def read(self, mdl):
            self.facesfront = read_int(mdl.file)
            self.verts = read_ushort(mdl.file, 3)
            self.stverts = read_ushort(mdl.file, 3)
            return self

        def write(self, mdl):
            write_int(mdl.file, self.facesfront)
            write_int(mdl.file, self.verts)

    class Frame:
        def __init__(self):
            self.type = 0
            self.name = ""
            self.mins = [0, 0, 0]
            self.maxs = [0, 0, 0]
            self.verts = []
            self.frames = []
            self.times = []

        def info(self):
            info = {}
            if self.type:
                if self.times:
                    info['intervals'] = list(map(lambda t: str(t), self.times))
                info['frames'] = []
                for f in self.frames:
                    info['frames'].append(f.info())
            if hasattr(self, 'frameno'):
                info['frameno'] = str(self.frameno)
            if self.name:
                info['name'] = self.name
            return info

        def add_vert(self, vert):
            self.verts.append(vert)
            for i, v in enumerate(vert.r):
                self.mins[i] = min(self.mins[i], v)
                self.maxs[i] = max(self.maxs[i], v)

        def add_frame(self, frame, time):
            self.type = 1
            self.frames.append(frame)
            self.times.append(time)
            for i in range(3):
                self.mins[i] = min(self.mins[i], frame.mins[i])
                self.maxs[i] = max(self.maxs[i], frame.maxs[i])

        def scale(self, mdl):
            self.mins = tuple(map(lambda x, s, t: int((x - t) / s),
                                  self.mins, mdl.scale, mdl.scale_origin))
            self.maxs = tuple(map(lambda x, s, t: int((x - t) / s),
                                  self.maxs, mdl.scale, mdl.scale_origin))
            if self.type:
                for subframe in self.frames:
                    subframe.scale(mdl)
            else:
                for vert in self.verts:
                    vert.scale(mdl)

        def read(self, mdl, numverts, sub=0):
            if sub:
                self.type = 0
            else:
                self.type = read_int(mdl.file)
            if self.type:
                num = read_int(mdl.file)
                self.read_bounds(mdl)
                self.times = read_float(mdl.file, num)
                self.frames = []
                for _ in range(num):
                    self.frames.append(MDL.Frame().read(mdl, numverts, 1))
                return self
            self.read_bounds(mdl)
            self.read_name(mdl)
            self.read_verts(mdl, numverts)
            return self

        def write(self, mdl, sub=0):
            if not sub:
                write_int(mdl.file, self.type)
                if self.type:
                    write_int(mdl.file, len(self.frames))
                    self.write_bounds(mdl)
                    write_float(mdl.file, self.times)
                    for frame in self.frames:
                        frame.write(mdl, 1)
                    return
            self.write_bounds(mdl)
            self.write_name(mdl)
            self.write_verts(mdl)

        def read_name(self, mdl):
            if mdl.version >= 6:
                name = read_string(mdl.file, 16)
            else:
                name = ""
            if "\0" in name:
                name = name[:name.index("\0")]
            self.name = name

        def write_name(self, mdl):
            if mdl.version >= 6:
                write_string(mdl.file, self.name, 16)

        def read_bounds(self, mdl):
            self.mins = read_byte(mdl.file, 4)[:3]  # discard normal index
            self.maxs = read_byte(mdl.file, 4)[:3]  # discard normal index

        def write_bounds(self, mdl):
            write_byte(mdl.file, self.mins + (0,))
            write_byte(mdl.file, self.maxs + (0,))

        def read_verts(self, mdl, num):
            self.verts = []
            for i in range(num):
                self.verts.append(MDL.Vert().read(mdl))
            if mdl.ident == 'MD16':
                for i in range(num):
                    v = MDL.Vert().read(mdl)
                    r = tuple(map(lambda a, b: a + b / 256.0,
                                  self.verts[i].r, v.r))
                    self.verts[i].r = r

        def write_verts(self, mdl):
            for vert in self.verts:
                vert.write(mdl, True)
            if mdl.ident == 'MD16':
                for vert in self.verts:
                    vert.write(mdl, False)

    class Vert:
        def __init__(self, r=None, ni=0):
            if not r:
                r = (0, 0, 0)
            self.r = r
            self.ni = ni
            pass

        def read(self, mdl):
            self.r = read_byte(mdl.file, 3)
            self.ni = read_byte(mdl.file)
            return self

        def write(self, mdl, high=True):
            if mdl.ident == 'MD16' and not high:
                r = tuple(map(lambda a: int(a * 256) & 255, self.r))
            else:
                r = tuple(map(lambda a: int(a) & 255, self.r))
            write_byte(mdl.file, r)
            write_byte(mdl.file, self.ni)

        def scale(self, mdl):
            self.r = tuple(map(lambda x, s, t: (x - t) / s,
                               self.r, mdl.scale, mdl.scale_origin))

    def __init__(self, name="mdl", md16=False):
        self.name = name
        self.ident = md16 and "MD16" or "IDPO"
        self.version = 6  # write only version 6 (nothing usable uses 3)
        self.scale = (1.0, 1.0, 1.0)  # FIXME
        self.scale_origin = (0.0, 0.0, 0.0)  # FIXME
        self.boundingradius = 1.0  # FIXME
        self.eyeposition = (0.0, 0.0, 0.0)  # FIXME
        self.synctype = MDLSyncType["ST_SYNC"].value
        self.flags = 0
        self.size = 0
        self.skins = []
        self.numverts = 0
        self.stverts = []
        self.tris = []
        self.frames = []

    def read(self, filepath):
        # Reading MDL file header
        self.file = open(filepath, "rb")
        self.name = filepath.split('/')[-1]
        self.name = self.name.split('.')[0]
        self.ident = read_string(self.file, 4)
        self.version = read_int(self.file)
        if self.ident not in ["IDPO", "MD16", "RAPO"] or self.version not in [3, 6, 50]:
            return None
        self.scale = read_float(self.file, 3)
        self.scale_origin = read_float(self.file, 3)
        self.boundingradius = read_float(self.file)
        self.eyeposition = read_float(self.file, 3)
        numskins = read_int(self.file)
        self.skinwidth, self.skinheight = read_int(self.file, 2)
        numverts, numtris, numframes = read_int(self.file, 3)
        self.synctype = read_int(self.file)
        if self.version >= 6:
            self.flags = read_int(self.file)
            self.size = read_float(self.file)

        if self.version == 6:
            self.num_st_verts = numverts
        if self.version == 50:
            self.num_st_verts = read_int(self.file)

        # read in the skin data
        self.skins = []
        for _ in range(numskins):
            self.skins.append(MDL.Skin().read(self))

        # read in the st verts (uv map)
        self.stverts = []
        for _ in range(self.num_st_verts):
            self.stverts.append(MDL.STVert().read(self))
        # read in the tris
        self.tris = []
        if (self.version < 50):
            for _ in range(numtris):
                self.tris.append(MDL.Tri().read(self))
        else:
            for _ in range(numtris):
                self.tris.append(MDL.NTri().read(self))
        # read in the frames
        self.frames = []
        for _ in range(numframes):
            self.frames.append(MDL.Frame().read(self, numverts))
        return self

    def write(self, filepath):
        self.file = open(filepath, "wb")
        write_string(self.file, self.ident, 4)
        write_int(self.file, self.version)
        write_float(self.file, self.scale)
        write_float(self.file, self.scale_origin)
        write_float(self.file, self.boundingradius)
        write_float(self.file, self.eyeposition)
        write_int(self.file, len(self.skins))
        write_int(self.file, self.skinwidth)
        write_int(self.file, self.skinheight)
        write_int(self.file, self.numverts)
        write_int(self.file, len(self.tris))
        write_int(self.file, len(self.frames))
        write_int(self.file, self.synctype)
        if self.version >= 6:
            write_int(self.file, self.flags)
            write_float(self.file, self.size)
        # write out the skin data
        for skin in self.skins:
            skin.write(self)
        # write out the st verts (uv map)
        for stvert in self.stverts:
            stvert.write(self)
        # write out the tris
        for tri in self.tris:
            tri.write(self)
        # write out the frames
        for frame in self.frames:
            frame.write(self)
