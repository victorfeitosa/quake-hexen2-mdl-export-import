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
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty, CollectionProperty
import bpy

bl_info = {
    "name": "Quake and Hexen II MDL format",
    "author": "Bill Currie, Victor Feitosa",
    "blender": (2, 80, 0),
    "version": (0, 9, 4),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export Quake and HexenII MDL files (version 6 mdl files)",
    "warning": "alpha version",
    "wiki_url": "",
    "tracker_url": "",
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

PALETTES = (
    ('QUAKE', "Quake palette", "Import/Export to Quake"),
    ('HEXEN2', "Hexen II palette", "Import/Export to Hexen II"),
)


class QFMDLEffects(bpy.types.PropertyGroup):
    # Quake effects
    rocket: BoolProperty(
        name="EF_ROCKET",
        description="Leave a rocket trail",
    )
    grenade: BoolProperty(
        name="EF_GRENADE",
        description="Leave a grenade trail",
    )
    gib: BoolProperty(
        name="EF_GIB",
        description="Leave a trail of blood",
    )
    rotate: BoolProperty(
        name="EF_ROTATE",
        description="Rotates model like an pickup",
    )
    tracer: BoolProperty(
        name="EF_TRACER",
        description="Green split trail",
    )
    zombie_gib: BoolProperty(
        name="EF_ZOMGIB",
        description="Leave a smaller blood trail",
    )
    tracer2: BoolProperty(
        name="EF_TRACER2",
        description="Orange split trail",
    )
    tracer3: BoolProperty(
        name="EF_TRACER3",
        description="Purple split trail",
    )

    # Hexen II effects
    fireball: BoolProperty(
        name="EF_FIREBALL",
        description="Yellow transparent fireball trail",
    )
    ice: BoolProperty(
        name="EF_ICE",
        description="Blue white ice trail with gravity",
    )
    mipmap: BoolProperty(
        name="EF_MIP_MAP",
        description="Model has mip maps",
    )
    spit: BoolProperty(
        name="EF_SPIT",
        description="Black transparent trail with negative light",
    )
    transp: BoolProperty(
        name="EF_TRANSPARENT",
        description="Transparent sprite",
    )
    spell: BoolProperty(
        name="EF_SPELL",
        description="Vertical spray of particles",
    )
    solid: BoolProperty(
        name="EF_HOLEY",
        description="Solid model with black color",
    )
    trans: BoolProperty(
        name="EF_SPECIAL_TRANS",
        description="Model with alpha channel",
    )
    billboard: BoolProperty(
        name="EF_FACE_VIEW",
        description="Model is always facing the camera",
    )
    vorpal: BoolProperty(
        name="EF_VORP_MISSILE",
        description="Leaves trail at top and bottom of model",
    )
    setstaff: BoolProperty(
        name="EF_SET_STAFF",
        description="Trail that bobs left and right",
    )
    magicmis: BoolProperty(
        name="EF_MAGICMISSILE",
        description="Blue white particles with gravity",
    )
    boneshard: BoolProperty(
        name="EF_BONESHARD",
        description="Brown particles with gravity",
    )
    scarab: BoolProperty(
        name="EF_SCARAB",
        description="White transparent particles with little gravity",
    )
    acidball: BoolProperty(
        name="EF_ACIDBALL",
        description="Green drippy acid particles",
    )
    bloodshot: BoolProperty(
        name="EF_BLOODSHOT",
        description="Blood rain shot trail",
    )
    farmipmap: BoolProperty(
        name="EF_MIP_MAP_FAR",
        description="Model has mip maps for far distances",
    )


class QFMDLSettings(bpy.types.PropertyGroup):
    eyeposition: FloatVectorProperty(
        name="Eye Position",
        description="View possion relative to object origin",
    )
    synctype: EnumProperty(
        items=SYNCTYPE,
        name="Sync Type",
        description="Add random time offset for automatic animations",
    )
    script: StringProperty(
        name="Script",
        description="Script for animating frames and skins",
    )
    xform: BoolProperty(
        name="Auto transform",
        description="Auto-apply location/rotation/scale when exporting",
        default=True,
    )
    md16: BoolProperty(
        name="16-bit",
        description="16 bit vertex coordinates: QuakeForge only",
    )
    effects: PointerProperty(
        name="MDL Effects",
        type=QFMDLEffects,
    )


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
        default="QUAKE",
    )

    export_scale: FloatProperty(
        name="Scale factor",
        description="Import model scale factor (usually 5)",
        default=10,
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
                and context.active_object.data is bpy.types.Mesh)

    def execute(self, context):
        from . import export_mdl
        keywords = self.as_keywords(ignore=("check_existing", "filter_glob"))

        try:
            return export_mdl.export_mdl(self, context, **keywords)
        except IndexError:
            self.report(
                {"WARNING"}, "Error converting MDL vertices. Do you have any unapplied topology modifiers?")
            return {'CANCELLED'}
        return export_result


class MDL_PT_Panel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_label = 'Quake MDL'

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        layout.prop(obj.qfmdl, "eyeposition")
        layout.prop(obj.qfmdl, "synctype")
        layout.prop(obj.qfmdl, "script")
        layout.prop(obj.qfmdl, "xform")
        layout.prop(obj.qfmdl, "md16")

        layout.label(text="Quake effects")

        effects = obj.qfmdl.effects
        # NOTE: Quake effects
        grid = layout.grid_flow(columns=2)
        grid.prop(effects, "rocket")
        grid.prop(effects, "grenade")
        grid.prop(effects, "gib")
        grid.prop(effects, "rotate")
        grid.prop(effects, "tracer")
        grid.prop(effects, "zombie_gib")
        grid.prop(effects, "tracer2")
        grid.prop(effects, "tracer3")
        # NOTE: Hexen II effects
        layout.label(text="Hexen II effects")
        grid = layout.grid_flow(columns=2)
        grid.prop(effects, "fireball")
        grid.prop(effects, "ice")
        grid.prop(effects, "mipmap")
        grid.prop(effects, "spit")
        grid.prop(effects, "transp")
        grid.prop(effects, "spell")
        grid.prop(effects, "solid")
        grid.prop(effects, "trans")
        grid.prop(effects, "billboard")
        grid.prop(effects, "vorpal")
        grid.prop(effects, "setstaff")
        grid.prop(effects, "magicmis")
        grid.prop(effects, "boneshard")
        grid.prop(effects, "scarab")
        grid.prop(effects, "acidball")
        grid.prop(effects, "bloodshot")
        grid.prop(effects, "farmipmap")


def menu_func_import(self, context):
    self.layout.operator(ImportMDL6.bl_idname,
                         text="Quake / HexenII MDL (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(ExportMDL6.bl_idname,
                         text="Quake / HexenII MDL (.mdl)")


classes = (QFMDLEffects, QFMDLSettings, ImportMDL6, ExportMDL6, MDL_PT_Panel)


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
