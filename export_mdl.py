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

import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

from .utils import getPaletteFromName
from .qfplist import pldata, PListError
from .qnorm import map_normal
from .mdl import MDL
from .constants import MDLEffects, MDLSyncType


def check_faces(mesh):
    # Check that all faces are tris because mdl does not support anything else.
    # Because the diagonal on which a quad is split can make a big difference,
    # quad to tri conversion will not be done automatically.
    faces_ok = True
    save_select = []
    for f in mesh.polygons:
        save_select.append(f.select)
        f.select = False
        if len(f.vertices) > 3:
            f.select = True
            faces_ok = False
    if not faces_ok:
        mesh.update()
        return False
    # reset selection to what it was before the check.
    for f, s in map(lambda x, y: (x, y), mesh.polygons, save_select):
        f.select = s
    mesh.update()
    return True


def convert_image(image, palette):
    size = image.size
    skin = MDL.Skin()
    skin.type = 0
    skin.pixels = bytearray(size[0] * size[1])  # preallocate
    cache = {}
    pixels = image.pixels[:]
    for y in range(size[1]):
        for x in range(size[0]):
            outind = y * size[0] + x
            # quake textures are top to bottom, but blender images
            # are bottom to top
            inind = ((size[1] - 1 - y) * size[0] + x) * 4
            rgb = pixels[inind: inind + 3]  # ignore alpha
            rgb = tuple(map(lambda x: int(x * 255 + 0.5), rgb))
            if rgb not in cache:
                best = (3*256*256, -1)
                for i, p in enumerate(palette):
                    if i > 255:     # should never happen
                        break
                    r = 0
                    for x in map(lambda a, b: (a - b) ** 2, rgb, p):
                        r += x
                    if r < best[0]:
                        best = (r, i)
                cache[rgb] = best[1]
            skin.pixels[outind] = cache[rgb]
    return skin


def null_skin(size):
    skin = MDL.Skin()
    skin.type = 0
    skin.pixels = bytearray(size[0] * size[1])  # black skin
    return skin


def active_uv(mesh):
    for uvt in mesh.uv_layers:
        if uvt.active:
            return uvt
    return None


def make_skin(mdl, mesh, palette):
    mdl.skinwidth, mdl.skinheight = (4, 4)
    skin = null_skin((mdl.skinwidth, mdl.skinheight))

    materials = bpy.context.object.data.materials

    if len(materials) > 0:
        for mat in materials:
            allTextureNodes = list(
                filter(lambda node: node.type == "TEX_IMAGE",
                       mat.node_tree.nodes))
            if len(allTextureNodes) > 1:  # === skingroup
                skingroup = MDL.Skin()
                skingroup.type = 1
                skingroup.skins = []
                skingroup.times = []
                sortedNodes = list(allTextureNodes)
                sortedNodes.sort(key=lambda x: x.location[1], reverse=True)
                for node in sortedNodes:
                    if node.type == "TEX_IMAGE":
                        image = node.image
                        mdl.skinwidth, mdl.skinheight = image.size
                        skin = convert_image(image, palette)
                        skingroup.skins.append(skin)
                        # hardcoded at the moment
                        skingroup.times.append(0.1)
                mdl.skins.append(skingroup)
            elif len(allTextureNodes) == 1:  # === single skin
                for node in allTextureNodes:
                    if node.type == "TEX_IMAGE":
                        image = node.image
                        if (image.size[0] > 0 and image.size[1] > 0):
                            mdl.skinwidth, mdl.skinheight = (4, 4)
                            skin = convert_image(image, palette)
                        mdl.skins.append(skin)
            else:
                # add empty skin - no texture nodes
                mdl.skins.append(skin)
    else:
        # add empty skin - no materials
        mdl.skins.append(skin)


def build_tris(mesh):
    # mdl files have a 1:1 relationship between stverts and 3d verts.
    # a bit sucky, but it does allow faces to take less memory
    #
    # modelgen's algorithm for generating UVs is very efficient in that no
    # vertices are duplicated (thanks to the onseam flag), but it can result
    # in fairly nasty UV layouts, and worse: the artist has no control over
    # the layout. However, there seems to be nothing in the mdl format
    # preventing the use of duplicate 3d vertices to allow complete freedom
    # of the UV layout.
    uvfaces = mesh.uv_layers.active.data
    stverts = []
    tris = []
    vertmap = []    # map mdl vert num to blender vert num (for 3d verts)
    vuvdict = {}
    for face in mesh.polygons:
        fv = list(face.vertices)
        uv = uvfaces[face.loop_start:face.loop_start + face.loop_total]
        uv = list(map(lambda a: a.uv, uv))
        face_tris = []
        for i in range(1, len(fv) - 1):
            # blender's and quake's vertex order are opposed
            face_tris.append([(fv[0], tuple(uv[0])),
                              (fv[i + 1], tuple(uv[i + 1])),
                              (fv[i], tuple(uv[i]))])
        for ft in face_tris:
            tv = []
            for vuv in ft:
                if vuv not in vuvdict:
                    vuvdict[vuv] = len(stverts)
                    vertmap.append(vuv[0])
                    stverts.append(vuv[1])
                tv.append(vuvdict[vuv])
            tris.append(MDL.Tri(tv))
    return tris, stverts, vertmap


def convert_stverts(mdl, stverts):
    for i, st in enumerate(stverts):
        s, t = st
        # quake textures are top to bottom, but blender images
        # are bottom to top
        s = round(s * (mdl.skinwidth - 1) + 0.5)
        t = round((1 - t) * (mdl.skinheight - 1) + 0.5)
        # ensure st is within the skin
        s = ((s % mdl.skinwidth) + mdl.skinwidth) % mdl.skinwidth
        t = ((t % mdl.skinheight) + mdl.skinheight) % mdl.skinheight

        stverts[i] = MDL.STVert((s, t))


def make_frame(mesh, vertmap, findex):
    frame = MDL.Frame()
    frame.name = "frame" + str(findex)

    if bpy.context.object.data.shape_keys:
        shape_keys_amount = len(bpy.context.object.data.shape_keys.key_blocks)
        if shape_keys_amount > findex:
            frame.name = bpy.context.object.data.shape_keys.key_blocks[round(
                findex)].name

    for v in vertmap:
        mv = mesh.vertices[v]
        vert = MDL.Vert(tuple(mv.co), map_normal(mv.normal))
        frame.add_vert(vert)
    return frame


def scale_verts(mdl):
    tf = MDL.Frame()
    for f in mdl.frames:
        tf.add_frame(f, 0.0)    # let the frame class do the dirty work for us
    size = Vector(tf.maxs) - Vector(tf.mins)
    rsqr = tuple(map(lambda a, b: max(abs(a), abs(b)) ** 2, tf.mins, tf.maxs))
    mdl.boundingradius = (rsqr[0] + rsqr[1] + rsqr[2]) ** 0.5
    mdl.scale_origin = tf.mins
    mdl.scale = tuple(map(lambda x: x / 255.0, size))
    for f in mdl.frames:
        f.scale(mdl)


def calc_average_area(mdl):
    frame = mdl.frames[0]
    if frame.type:
        frame = frame.frames[0]
    totalarea = 0.0
    for tri in mdl.tris:
        verts = tuple(map(lambda i: frame.verts[i], tri.verts))
        a = Vector(verts[0].r) - Vector(verts[1].r)
        b = Vector(verts[2].r) - Vector(verts[1].r)
        c = a.cross(b)
        totalarea += (c @ c) ** 0.5 / 2.0
    return totalarea / len(mdl.tris)


def parse_effects(fx_group):
    effects = fx_group.__annotations__.keys()
    flags = 0
    for i, v in enumerate(effects):
        fx = getattr(fx_group, v)
        if fx:
            flags += MDLEffects[v].value
    return flags


def get_properties(operator, mdl, obj, export_scale):
    mdl.eyeposition = tuple(
        map(lambda v: v*export_scale, obj.qfmdl.eyeposition))
    mdl.synctype = MDLSyncType[obj.qfmdl.synctype].value
    mdl.flags = parse_effects(obj.qfmdl.effects)
    if obj.qfmdl.md16:
        mdl.ident = "MD16"
    return True


def process_skin(mdl, skin, palette, ingroup=False):
    if 'skins' in skin:
        if ingroup:
            raise ValueError("nested skin group")
        intervals = ['0.0']
        if 'intervals' in skin:
            intervals += list(skin['intervals'])
        intervals = list(map(lambda x: float(x), intervals))
        while len(intervals) < len(skin['skins']):
            intervals.append(intervals[-1] + 0.1)
        sk = MDL.Skin()
        sk.type = 1
        sk.times = intervals[1:len(skin['skins']) + 1]
        sk.skins = []
        for s in skin['skins']:
            sk.skins.append(process_skin(mdl, s, palette, ingroup=True))
        return sk
    else:
        # FIXME error handling
        name = skin['name']
        image = bpy.data.images[name]
        if hasattr(mdl, 'skinwidth'):
            if (mdl.skinwidth != image.size[0]
                    or mdl.skinheight != image.size[1]):
                raise ValueError("%s: different skin size (%d %d) (%d %d)"
                                 % (name, mdl.skinwidth, mdl.skinheight,
                                    int(image.size[0]), int(image.size[1])))
        else:
            mdl.skinwidth, mdl.skinheight = image.size
        sk = convert_image(image, palette)
        return sk


def process_frame(mdl, scene, frame, vertmap, ingroup=False,
                  frameno=None, name='frame'):
    if frameno is None:
        frameno = scene.frame_current + scene.frame_subframe
    if 'frameno' in frame:
        frameno = float(frame['frameno'])
    if 'name' in frame:
        name = frame['name']
    if 'frames' in frame:
        if ingroup:
            raise ValueError("nested frames group")
        intervals = ['0.0']
        if 'intervals' in frame:
            intervals += list(frame['intervals'])
        intervals = list(map(lambda x: float(x), intervals))
        while len(intervals) < len(frame['frames']) + 1:
            intervals.append(intervals[-1] + 0.1)
        fr = MDL.Frame()
        for i, f in enumerate(frame['frames']):
            fr.add_frame(process_frame(mdl, scene, f, vertmap, True,
                                       frameno + i, name + str(i + 1)),
                         intervals[i + 1])
        if 'intervals' in frame:
            return fr
        mdl.frames += fr.frames[:-1]
        return fr.frames[-1]
    scene.frame_set(int(frameno), subframe=(frameno - int(frameno)))
    mesh = mdl.obj.to_mesh(preserve_all_data_layers=True)  # wysiwyg?
    if mdl.obj.qfmdl.xform:
        mesh.transform(mdl.obj.matrix_world)
    fr = make_frame(mesh, vertmap, frameno)
    fr.name = name
    return fr


def export_mdl(operator, context, filepath, palette, export_scale):
    obj = context.active_object
    obj.update_from_editmode()
    depsgraph = context.evaluated_depsgraph_get()
    ob_eval = obj.evaluated_get(depsgraph)
    objname = ob_eval.name_full
    bpy.ops.transform.resize(value=(export_scale, export_scale, export_scale))

    palette = getPaletteFromName(palette)

    # if not check_faces(mesh):
    #    operator.report({'ERROR'},
    #                    "Mesh has faces with more than 3 vertices.")
    #    return {'CANCELLED'}
    mdl = MDL(obj.name)
    mdl.obj = obj
    if not get_properties(operator, mdl, obj, export_scale):
        return {'CANCELLED'}
    bpy.context.active_object.name = objname
    mesh = bpy.context.active_object.to_mesh()
    mdl.tris, mdl.stverts, vertmap = build_tris(mesh)
    if not mdl.skins or (mdl.skinwidth):
        make_skin(mdl, mesh, palette)
    if not mdl.frames:
        start_frame = context.scene.frame_start
        end_frame = context.scene.frame_end + 1
        for fnum in range(start_frame, end_frame):
            context.scene.frame_set(fnum)
            obj.update_from_editmode()
            depsgraph = context.evaluated_depsgraph_get()
            ob_eval = obj.evaluated_get(depsgraph)
            mesh = ob_eval.to_mesh()
            if mdl.obj.qfmdl.xform:
                mesh.transform(mdl.obj.matrix_world)
            eframe = make_frame(mesh, vertmap, fnum)
            mdl.frames.append(eframe)
    convert_stverts(mdl, mdl.stverts)
    mdl.size = calc_average_area(mdl)
    scale_verts(mdl)
    mdl.write(filepath)
    bpy.ops.transform.resize(
        value=(1/export_scale, 1/export_scale, 1/export_scale))

    return {'FINISHED'}
