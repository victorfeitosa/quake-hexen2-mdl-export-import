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
import importlib
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Matrix

from .constants import MDLEffects, MDLSyncType
from .mdl import MDL
from .qfplist import pldata


def make_verts(mdl, framenum, subframenum=0):
    '''
    Create vertices for the specified frame. If frame type is truthy,
    the current frame is a group of frames and will load the frame
    group instead of the single frame.
    '''

    frame = mdl.frames[framenum]
    if frame.type:
        frame = frame.frames[subframenum]
    verts = []
    s = Vector([v for v in mdl.scale]) * mdl.scale_factor
    o = Vector([v for v in mdl.scale_origin]) * mdl.scale_factor
    m = Matrix((
        (s.x, 0, 0, o.x),
        (0, s.y, 0, o.y),
        (0, 0, s.z, o.z),
        (0, 0, 0, 1)
    ))
    for v in frame.verts:
        verts.append(m @ Vector(v.r))
    return verts


def make_faces(mdl):
    '''
    Create the faces according to the mdl description, referencing
    the verts created.
    This also creates the uv coords for the faces
    '''
    faces = []
    uvs = []
    for tri in mdl.tris:
        # list of vertices in a tri
        tv = list(tri.verts)
        sts = []  # UV coords
        if mdl.version < 50:
            for v in tri.verts:
                # UV vertex
                stv = mdl.stverts[v]
                s = stv.s
                t = stv.t
                if stv.onseam and not tri.facesfront:
                    s += mdl.skinwidth / 2
                # quake textures are top to bottom, but blender images
                # are bottom to top
                sts.append((
                    s * 1.0 / mdl.skinwidth,
                    1 - t * 1.0 / mdl.skinheight,
                ))
        else:
            for v in tri.stverts:
                # UV vertex from a mdl v50
                stv = mdl.stverts[v]
                s, t = (stv.s, stv.t)
                if stv.onseam and not tri.facesfront:
                    s += mdl.skinwidth / 2
                sts.append((
                    s * 1.0 / mdl.skinwidth,
                    1 - t * 1.0 / mdl.skinheight,
                ))

        # blender's and quake's vertex order seem to be opposed
        tv.reverse()
        sts.reverse()
        # annoyingly, blender can't have 0 in the final vertex, so rotate the
        # face vertices and uvs
        if not tv[2]:
            tv = [tv[2]] + tv[:2]
            sts = [sts[2]] + sts[:2]
        faces.append(tv)
        uvs.append(sts)
    return faces, uvs


def load_skins(mdl, palette):
    '''
    Loads the texture pixel of the MDL model
    '''
    def load_skin(skin, name):
        skin.name = name
        img = bpy.data.images.new(name, mdl.skinwidth, mdl.skinheight)
        mdl.images.append(img)
        p = [0.0] * mdl.skinwidth * mdl.skinheight * 4
        d = skin.pixels
        for j in range(mdl.skinheight):
            for k in range(mdl.skinwidth):
                c = palette[d[j * mdl.skinwidth + k]]
                # quake textures are top to bottom, but blender images
                # are bottom to top
                ln = ((mdl.skinheight - 1 - j) * mdl.skinwidth + k) * 4
                p[ln + 0] = c[0] / 255.0  # Red
                p[ln + 1] = c[1] / 255.0  # Green
                p[ln + 2] = c[2] / 255.0  # Blue
                p[ln + 3] = 1.0           # Alpha

        img.pixels[:] = p[:]
        img.pack()
        img.use_fake_user = True

    mdl.images = []
    for i, skin in enumerate(mdl.skins):
        if skin.type:
            for j, subskin in enumerate(skin.skins):
                load_skin(subskin, "%s_%d_%d" % (mdl.name, i, j))
        else:
            load_skin(skin, "%s_%d" % (mdl.name, i))


def setup_skins(mdl, uvs, palette):
    '''
    Setup skin slots and materials and sets UV coordinates in
    the loaded texture
    '''
    load_skins(mdl, palette)
    img = mdl.images[0]   # use the first skin for now
    mdl.mesh.uv_layers.new(name=mdl.name)
    uvloop = mdl.mesh.uv_layers[0]

    # UV Loading=============
    for i, _ in enumerate(uvs):
        poly = mdl.mesh.polygons[i]
        mdl_uv = uvs[i]
        for j, k in enumerate(poly.loop_indices):
            uvloop.data[k].uv = mdl_uv[j]

    # Material and texture loading=======
    mat = bpy.data.materials.new(mdl.name)
    mat.use_nodes = True

    mat_out = mat.node_tree.nodes['Material Output']
    emi = mat.node_tree.nodes.new('ShaderNodeEmission')
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'

    mat.node_tree.links.new(emi.inputs['Color'], tex.outputs['Color'])
    mat.node_tree.links.new(mat_out.inputs['Surface'], emi.outputs['Emission'])

    # Remove old BSDF node
    bsdf = mat.node_tree.nodes['Principled BSDF']
    mat.node_tree.nodes.remove(bsdf)

    mdl.mesh.materials.append(mat)


def make_shape_key(mdl, framenum, subframenum=0):
    '''
    Construct a shape key for the particular frame or subframe in
    the Blender model
    '''
    frame = mdl.frames[framenum]
    name = "%s_%d" % (mdl.name, framenum)
    if frame.type:
        frame = frame.frames[subframenum]
        name = "%s_%d_%d" % (mdl.name, framenum, subframenum)
    if frame.name:
        name = frame.name
    else:
        frame.name = name
    frame.key = mdl.obj.shape_key_add(name=name)
    frame.key.value = 0.0
    mdl.keys.append(frame.key)
    s = Vector([v for v in mdl.scale]) * mdl.scale_factor
    o = Vector([v for v in mdl.scale_origin]) * mdl.scale_factor
    m = Matrix(((s.x,  0,  0, o.x),
                (0, s.y,  0, o.y),
                (0,  0, s.z, o.z),
                (0,  0,  0,  1)))
    for i, v in enumerate(frame.verts):
        frame.key.data[i].co = m @ Vector(v.r)


def build_shape_keys(mdl):
    '''
    Build all the shape keys of a MDL frames into the Blender model
    '''
    mdl.keys = []
    mdl.obj.shape_key_add(name="Basis")
    mdl.mesh.shape_keys.name = mdl.name
    mdl.obj.active_shape_key_index = 0
    for i, frame in enumerate(mdl.frames):
        frame = mdl.frames[i]
        if frame.type:
            for j in range(len(frame.frames)):
                make_shape_key(mdl=mdl, framenum=i,
                               subframenum=j)
        else:
            make_shape_key(mdl=mdl, framenum=i)


def set_keys(act, data):
    '''
    Set keyframe of animation
    '''
    for d in data:
        key, co = d
        dp = """key_blocks["%s"].value""" % key.name
        fc = act.fcurves.new(data_path=dp)
        fc.keyframe_points.add(len(co))
        for i in range(len(co)):
            fc.keyframe_points[i].co = co[i]
            fc.keyframe_points[i].interpolation = 'LINEAR'


def build_actions(mdl):
    '''
    Build animation actions
    '''
    sk = mdl.mesh.shape_keys
    ad = sk.animation_data_create()
    track = ad.nla_tracks.new()
    track.name = mdl.name
    start_frame = 1
    for frame in mdl.frames:
        act = bpy.data.actions.new(frame.name)
        data = []
        other_keys = mdl.keys[:]
        if frame.type:
            for j, subframe in enumerate(frame.frames):
                subframe.frameno = start_frame + j
                co = []
                if j > 1:
                    co.append((1.0, 0.0))
                if j > 0:
                    co.append((j * 1.0, 0.0))
                co.append(((j + 1) * 1.0, 1.0))
                if j < len(frame.frames) - 2:
                    co.append(((j + 2) * 1.0, 0.0))
                if j < len(frame.frames) - 1:
                    co.append((len(frame.frames) * 1.0, 0.0))
                data.append((subframe.key, co))
                if subframe.key in other_keys:
                    del (other_keys[other_keys.index(subframe.key)])
            co = [(1.0, 0.0), (len(frame.frames) * 1.0, 0.0)]
            for k in other_keys:
                data.append((k, co))
        else:
            subframe.frameno = start_frame + j
            data.append((frame.key, [(1.0, 1.0)]))
            if frame.key in other_keys:
                del (other_keys[other_keys.index(frame.key)])
            co = [(1.0, 0.0)]
            for k in other_keys:
                data.append((k, co))
        set_keys(act, data)
        track.strips.new(act.name, start_frame, act)
        start_frame += int(act.frame_range[1])


def merge_frames(mdl):
    def get_base(name):
        i = 0
        while i < len(name) and name[i] not in "0123456789":
            i += 1
        return name[:i]

    i = 0
    while i < len(mdl.frames):
        if mdl.frames[i].type:
            i += 1
            continue
        base = get_base(mdl.frames[i].name)
        j = i + 1
        while j < len(mdl.frames):
            if mdl.frames[j].type:
                break
            if get_base(mdl.frames[j].name) != base:
                break
            j += 1
        f = MDL.Frame()
        f.name = base
        f.type = 1
        f.frames = mdl.frames[i:j]
        mdl.frames[i:j] = [f]
        i += 1


def write_text(mdl):
    '''
    Creates text animation and configuration file for the imported model
    '''
    header = """
    /*  This script represents the animation data within the model file. It
        is generated automatically on import, and is optional when exporting.
        If no script is used when exporting, frames will be exported one per
        blender frame from frame 1 to the current frame (inclusive), and only
        one skin will be exported.

        The fundamental format of the script is documented at
        http://quakeforge.net/doxygen/property-list.html

        The expected layout is a top-level dictionary with two expected
        entries:
            frames  array of frame entries. If missing, frames will be handled
                    as if there were no script.
            skins   array of skin entries. If missing, skins will be handled
                    as if there were no script.

        A frame entry is a dictionary with the following fields:
            name    The name of the frame to be written to the mdl file. In a
                    frame group, this will form the base for sub-frame names
                    (name + relative frame number: eg, frame1) if the
                    sub-frame does not have a name field. (string)
            frameno The blender frame to use for the captured animation. In a
                    frame group, this will be used as the base frame for any
                    sub-frames that do not specify a frame. While fractional
                    frames are supported, YMMV. (string:float)
            frames  Array of frame entries. If present, the current frame
                    entry is a frame group, and the frame entries specify
                    sub-frames. (array of dictionary)
                    NOTE: only top-level frames may be frame groups
            intervals   Array of frame end times for frame groups. No meaning
                    in blender, but the quake engine uses them for client-side
                    animations. Times must be ascending, but any step > 0 is
                    valid. Ignored for single frames. If not present in a
                    frame group, the sub-frames of the group will be written
                    as single frames (in order to undo the auto-group feature
                    of the importer). Excess times will be ignored, missing
                    times will be generated at 0.1
                    second intervals.
                    (array of string:float).

        A skin entry is a dictionary with the following fields:
            name    The name of the blender image to be used as the skin.
                    Ignored for skin groups (animated skins). (string)
            skins   Array of skin entries. If present, the current skin
                    entry is a skin group (animated skin), and the skin
                    entries specify sub-skin. (array of dictionary)
                    NOTE: only top-level skins may be skins groups
            intervals   Array of skin end times for skin groups. No meaning
                    in blender, but the quake engine uses them for client-side
                    animations. Times must be ascending, but any step > 0 is
                    valid. Ignored for single skins. If not present in a
                    skin group, it will be generated using 0.1 second
                    intervals. Excess times will be ignored, missing times
                    will be generated at 0.1 second intervals.
                    (array of string:float).
    */
    """
    d = {'frames': [], 'skins': []}
    for f in mdl.frames:
        d['frames'].append(f.info())
    for s in mdl.skins:
        d['skins'].append(s.info())
    pl = pldata()
    string = header + pl.write(d)

    txt = bpy.data.texts.new(mdl.name)
    txt.from_string(string)
    mdl.text = txt


def parse_flags(fx_group, flags):
    effects = fx_group.__annotations__.items()
    for i, (key, v) in enumerate(effects):
        setattr(fx_group, key,
                (flags & MDLEffects[v.keywords['name']].value > 0))


def set_properties(mdl):
    mdl.obj.qfmdl.eyeposition = tuple(
        map(lambda v: v*mdl.scale_factor, mdl.eyeposition))
    try:
        mdl.obj.qfmdl.synctype = MDLSyncType(mdl.synctype).name
    except IndexError:
        mdl.obj.qfmdl.synctype = 'ST_SYNC'

    parse_flags(mdl.obj.qfmdl.effects, mdl.flags)
    mdl.obj.qfmdl.script = mdl.text.name  # FIXME really want the text object
    mdl.obj.qfmdl.md16 = (mdl.ident == "MD16")


def import_mdl(operator, context, filepath, palette, import_scale):
    bpy.context.preferences.edit.use_global_undo = False

    palette_module_name = "..{0}pal".format(palette.lower())
    palette = importlib.import_module(palette_module_name, __name__).palette

    for obj in bpy.context.scene.objects:
        obj.select_set(False)

    mdl = MDL()
    if not mdl.read(filepath):
        operator.report({'ERROR'},
                        "Unrecognized format: %s %d" % (mdl.ident, mdl.version))
        return {'CANCELLED'}
    faces, uvs = make_faces(mdl)
    verts = make_verts(mdl, 0)
    mdl.mesh = bpy.data.meshes.new(mdl.name)
    mdl.mesh.from_pydata(verts, [], faces)
    mdl.obj = bpy.data.objects.new(mdl.name, mdl.mesh)
    coll = context.view_layer.active_layer_collection.collection
    coll.objects.link(mdl.obj)
    bpy.context.view_layer.objects.active = mdl.obj
    mdl.obj.select_set(True)
    setup_skins(mdl, uvs, palette)
    mdl.scale_factor = import_scale
    if len(mdl.frames) > 1 or mdl.frames[0].type:
        build_shape_keys(mdl)
        merge_frames(mdl)
        build_actions(mdl)
    write_text(mdl)
    set_properties(mdl)

    mdl.mesh.update()

    bpy.context.preferences.edit.use_global_undo = True
    return {'FINISHED'}
