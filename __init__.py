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

from bpy_extras.io_utils import ExportHelper, ImportHelper, path_reference_mode, axis_conversion
from bpy.props import FloatVectorProperty, PointerProperty
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
import bpy

bl_info = {
    "name": "Quake and Hexen II MDL format",
    "author": "Bill Currie, Victor Feitosa",
    "blender": (2, 80, 0),
    "version": (0, 9, 0),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export Quake and HexenII MDL files (version 6 mdl files)",
    "warning": "not even alpha",
    "wiki_url": "",
    "tracker_url": "",
    # "support": "UNOFFICIAL",
    "category": "Import-Export"}

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    import imp
    if "import_mdl" in locals():
        imp.reload(import_mdl)
    if "export_mdl" in locals():
        imp.reload(export_mdl)


SYNCTYPE = (
    ('ST_SYNC', "Syncronized", "Automatic animations are all together"),
    ('ST_RAND', "Random", "Automatic animations have random offsets"),
)

EFFECTS_TYPE = ("quake", "hexen")
EFFECTS = {
    "hexen": (
        ('EF_NONE', "None", "No effects"),
        ('EF_ROCKET', "Rocket", "Leave a rocket trail"),
        ('EF_GRENADE', "Grenade", "Leave a grenade trail"),
        ('EF_GIB', "Gib", "Leave a trail of blood"),
        ('EF_ROTATE', "Rotate", "Rotate bonus item"),
        ('EF_TRACER', "Tracer", "Green split trail"),
        ('EF_ZOMGIB', "Zombie Gib", "Leave a smaller blood trail"),
        ('EF_TRACER2', "Tracer 2", "Orange split trail + rotate"),
        ('EF_TRACER3', "Tracer 3", "Purple split trail"),
        
    ),
}

PALETTES = (
    ('QUAKE', "Quake palette", "Import/Export to Quake"),
    ('HEXEN2', "Hexen II palette", "Import/Export to Hexen II"),
)


class QFMDLSettings(bpy.types.PropertyGroup):
    eyeposition: FloatVectorProperty(
        name="Eye Position",
        description="View possion relative to object origin")
    synctype: EnumProperty(
        items=SYNCTYPE,
        name="Sync Type",
        description="Add random time offset for automatic animations")
    rotate: BoolProperty(
        name="Rotate",
        description="Rotate automatically (for pickup items)")
    script: StringProperty(
        name="Script",
        description="Script for animating frames and skins")
    xform: BoolProperty(
        name="Auto transform",
        description="Auto-apply location/rotation/scale when exporting",
        default=True)
    md16: BoolProperty(
        name="16-bit",
        description="16 bit vertex coordinates: QuakeForge only")
    
    # Quake effects
    fx_rocket: BoolProperty(name="Rocket", description="Leave a rocket trail")
    fx_grenade: BoolProperty(name="Grenade", description="Leave a grenade trail")
    fx_gib: BoolProperty(name="Gib", description="Leave a trail of blood")
    fx_tracer: BoolProperty(name="Tracer", description="Green split trail")
    fx_zombie_gib: BoolProperty(name="Zombie Gib", description="Leave a smaller blood trail")
    fx_tracer2: BoolProperty(name="Tracer 2", description="Orange split trail + rotate")
    fx_tracer3: BoolProperty(name="Tracer 3", description="Purple split trail")
    
    # Hexen II effects
    fx_fireball: BoolProperty(name="Fireball", description="Yellow transparent fireball trail")
    fx_ice: BoolProperty(name="Ice", description="Blue white ice trail with gravity")
    fx_mipmap: BoolProperty(name="Mip map", description="Model has mip maps")
    fx_spit: BoolProperty(name="Spit", description="Black transparent trail with negative light")
    fx_transp: BoolProperty(name="Transparency", description="Transparent sprite")
    fx_spell: BoolProperty(name="Spell", description="Vertical spray of particles")
    fx_solid: BoolProperty(name="Solid", description="Solid model with black color")
    fx_trans: BoolProperty(name="Translucency", description="Model with alpha channel")
    fx_billboard: BoolProperty(name="Billboard", description="Model is always facing the camera")
    fx_vorpal: BoolProperty(name="Vorpal Missile", description="Leaves trail at top and bottom of model")
    fx_setstaff: BoolProperty(name="Set's Staff", description="Trail that bobs left and right")
    fx_magicmis: BoolProperty(name="Magic missile", description="Blue white particles with gravity")
    fx_boneshard: BoolProperty(name="Bone shard", description="Brown particles with gravity")
    fx_scarab: BoolProperty(name="Scarab", description="White transparent particles with little gravity")
    fx_acidball: BoolProperty(name="Acid ball", description="Green drippy acid particles")
    fx_bloodshot: BoolProperty(name="Blood shot", description="Blood rain shot trail")
    fx_farmipmap: BoolProperty(name="Far mipmap", description="Model has mip maps for far")

class ImportMDL6(bpy.types.Operator, ImportHelper):
    '''Load a Quake MDL File'''
    bl_idname = "import_mesh.quake_mdl_v6"
    bl_label = "Import MDL"

    filename_ext = ".mdl"
    filter_glob: StringProperty(default="*.mdl", options={'HIDDEN'})

    palette: EnumProperty(
        items=PALETTES,
        name="MDL Palette",
        description="Game color palette",
        default="QUAKE"
    )

    import_scale: FloatProperty(
        name="Scale factor",
        description="Import model scale factor (usually 0.5)",
        default=0.1
    )

    def execute(self, context):
        from . import import_mdl
        keywords = self.as_keywords(ignore=("filter_glob",))
        return import_mdl.import_mdl(self, context, **keywords)


class ExportMDL6(bpy.types.Operator, ExportHelper):
    '''Save a Quake MDL File'''

    bl_idname = "export_mesh.quake_mdl_v6"
    bl_label = "Export MDL"

    filename_ext = ".mdl"
    filter_glob: StringProperty(default="*.mdl", options={'HIDDEN'})

    palette: EnumProperty(
        items=PALETTES,
        name="MDL Palette",
        description="Game color palette",
        default="QUAKE"
    )

    export_scale: FloatProperty(
        name="Scale factor",
        description="Import model scale factor (usually 5)",
        default=10
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object != None
                and type(context.active_object.data) == bpy.types.Mesh)

    def execute(self, context):
        from . import export_mdl
        keywords = self.as_keywords(ignore=("check_existing", "filter_glob"))
        return export_mdl.export_mdl(self, context, **keywords)


class MDL_PT_Panel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_label = 'QF MDL'
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        
        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        layout.prop(obj.qfmdl, "eyeposition")
        layout.prop(obj.qfmdl, "synctype")
        layout.prop(obj.qfmdl, "rotate")
        layout.prop(obj.qfmdl, "effects")
        layout.prop(obj.qfmdl, "script")
        layout.prop(obj.qfmdl, "xform")
        layout.prop(obj.qfmdl, "md16")
        
        layout.label(text="Quake effects")
        grid = layout.grid_flow(columns=2)
        grid.prop(obj.qfmdl, "fx_rocket")
        grid.prop(obj.qfmdl, "fx_grenade")
        grid.prop(obj.qfmdl, "fx_gib")
        grid.prop(obj.qfmdl, "fx_tracer")
        grid.prop(obj.qfmdl, "fx_zombie_gib")
        grid.prop(obj.qfmdl, "fx_tracer2")
        grid.prop(obj.qfmdl, "fx_tracer3")
        
        layout.label(text="Hexen II effects")
        grid = layout.grid_flow(columns=2)
        grid.prop(obj.qfmdl, "fx_fireball")
        grid.prop(obj.qfmdl, "fx_ice")
        grid.prop(obj.qfmdl, "fx_mipmap")
        grid.prop(obj.qfmdl, "fx_spit")
        grid.prop(obj.qfmdl, "fx_transp")
        grid.prop(obj.qfmdl, "fx_spell")
        grid.prop(obj.qfmdl, "fx_solid")
        grid.prop(obj.qfmdl, "fx_trans")
        grid.prop(obj.qfmdl, "fx_billboard")
        grid.prop(obj.qfmdl, "fx_vorpal")
        grid.prop(obj.qfmdl, "fx_setstaff")
        grid.prop(obj.qfmdl, "fx_magicmis")
        grid.prop(obj.qfmdl, "fx_boneshard")
        grid.prop(obj.qfmdl, "fx_scarab")
        grid.prop(obj.qfmdl, "fx_acidball")
        grid.prop(obj.qfmdl, "fx_bloodshot")
        grid.prop(obj.qfmdl, "fx_farmipmap")


def menu_func_import(self, context):
    self.layout.operator(ImportMDL6.bl_idname,
                         text="Quake / HexenII MDL (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(ExportMDL6.bl_idname,
                         text="Quake / HexenII MDL (.mdl)")


classes = (QFMDLSettings, ImportMDL6, ExportMDL6, MDL_PT_Panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.qfmdl = PointerProperty(type=QFMDLSettings)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
