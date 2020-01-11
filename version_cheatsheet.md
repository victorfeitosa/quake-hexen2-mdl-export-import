Blender 2.80 add-on update cheat sheet
??? = not verified or not correct in many cases, but may work
*** = verified to work in most or all cases

???  alpha needed
-mat.diffuse_color = (red_v, grn_v, blu_v)  # viewport color
+mat.diffuse_color = (red_v, grn_v, blu_v, alpha_v)  # viewport color

???  viewnumpad
-col.operator("view3d.viewnumpad", text="View Camera", icon='CAMERA_DATA').type = 'CAMERA'
+col.operator("view3d.view_camera", text="View Camera", icon='CAMERA_DATA')

???  viewnumpad > view_axis
-bpy.ops.view3d.viewnumpad(type='BOTTOM')
+bpy.ops.view3d.view_axis(type='BOTTOM')

???  get_rna
-properties = op.get_rna().bl_rna.properties.items()
+properties = op.get_rna_type().properties.items()

???  viewport_shade > shading.type
-pie.prop(context.space_data, "viewport_shade", expand=True)
+pie.prop(context.space_data.shading, "type", expand=True)
-if context.space_data.viewport_shade == 'RENDERED':
+if context.space_data.shading.type == 'RENDERED':

???  TOOLS > UI (Tools panel > N panel)
-bl_region_type = "TOOLS"
+bl_region_type = "UI"

???  View
-bl_region_type = 'View'
-bl_category = 'Tools'
+bl_region_type = 'UI'
+bl_category = 'View'
otherwise...
RuntimeError: Error: Registering panel class: 'view3d.blah' has category 'View'

???  Lamp > Light
-"OUTPUT_LAMP"
-"ShaderNodeOutputLamp"
+"OUTPUT_LIGHT"
+"ShaderNodeOutputLight"

???  lamps > lights
-bpy.data.lamps
+bpy.data.lights

***  select > select_set (only changed for objects, not verts/edges/faces)
-obj.select = False
+obj.select_set(False)
otherwise...
AttributeError: 'Object' object has no attribute 'select'
possible regex:
find: (\.select\s*=\s*)(True|False)
repl: .select_set\(\2\)

***  select > select_get (only changed for objects, not verts/edges/faces)
-if o.select:
+if o.select_get():
-if not obj.select:
+if not obj.select_get():
-if o.select is True:
+if o.select_get() is True:
possible regex:
find: (\.select)(\s*)(is|==)(\s*)(True|False)
repl: .select_get\(\)(\2)(\3)(\4)(\5)

???  backdrop_x / backdrop_y > backdrop_offset[0] / backdrop_offset[1]
-context.space_data.backdrop_x = 0
-context.space_data.backdrop_y = 0
+context.space_data.backdrop_offset[0] = 0
+context.space_data.backdrop_offset[1] = 0

???  ops.delete context (int > string)
-bmesh.ops.delete(bm, geom=edges, context=1)
-bmesh.ops.delete(bm, geom=edges, context=2)
-bmesh.ops.delete(bm, geom=edges, context=3)
+bmesh.ops.delete(bm, geom=edges, context="VERTS")
+bmesh.ops.delete(bm, geom=edges, context="EDGES")
+bmesh.ops.delete(bm, geom=edges, context="FACES")
otherwise...
TypeError: delete: keyword "context" expected a string, not int

???  tessface > loop_triangles
-bmesh.update_edit_mesh(object.data, tessface=True, destructive=True)
+bmesh.update_edit_mesh(object.data, loop_triangles=True, destructive=True)

???  to_mesh
 ob = bpy.context.active_object
 depsgraph = bpy.context.evaluated_depsgraph_get()
-mesh = ob.evaluated_get(depsgraph).to_mesh()
+ob_eval = ob.evaluated_get(depsgraph)
+mesh = ob_eval.to_mesh()

???  to_mesh (2)
 obj = bpy.context.active_object
-mesh = obj.to_mesh(context.scene, True, 'PREVIEW')
+depsgraph = context.evaluated_depsgraph_get()
+mesh = obj.evaluated_get(depsgraph).to_mesh()

???  meshes.remove
-bpy.data.meshes.remove(mesh)
+ob_eval.to_mesh_clear()

???  active
-plane = context.scene.objects.active
+plane = context.active_object

???  active (2)
-bpy.context.scene.objects.active = obj
+bpy.context.view_layer.objects.active = obj
otherwise...
AttributeError: bpy_prop_collection: attribute "active" not found
#bpy.context.view_layer.objects.active = bpy.data.objects['Light'] ??
#bpy.context.view_layer.objects.active = None ??
#bpy.context.active_object ?

???  object_bases
-context.scene.object_bases
+obj = context.view_layer.objects.active  ???

???   keymaps: name, space_type, region_type (keyword)
-def keymap(self, name="Window", space_type='EMPTY', region_type='WINDOW'):
+def keymap(self, name_="Window", space_type_='EMPTY', region_type_='WINDOW'):
     self.km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
-        name, space_type, region_type)
+        name=name_, space_type=space_type_, region_type=region_type_)
otherwise...
TypeError: KeyMaps.new(): required parameter "space_type" to be a keyword argument!

???  frame_set subframe (keyword)
-context.scene.frame_set(int(frame[1]), frame[0])
+context.scene.frame_set(int(frame[1]), subframe=frame[0])

???  prop text (keyword)
-row.prop(self, "filter_auto_focus", "", icon='VIEWZOOM')
+row.prop(self, "filter_auto_focus", text="", icon='VIEWZOOM')

???  label text (keyword)
-row.label(context.object.name)
+row.label(text=context.object.name)
-box.label("From curve")
+box.label(text="From curve")

***  label text
-col.label("Sharpness")
+col.label(text="Sharpness")
otherwise...
TypeError: UILayout.label(): required parameter "text" to be a keyword argument!

???  popup_menu title (keyword)
-context.window_manager.popup_menu(self.menu, "Icon Viewer")
+context.window_manager.popup_menu(self.menu, title="Icon Viewer")

???  operator text (keyword)
-row.operator(IV_OT_panel_menu_call.bl_idname, "", icon='COLLAPSEMENU')
+row.operator(IV_OT_panel_menu_call.bl_idname, text="", icon='COLLAPSEMENU')

***  operator text (keyword)
-row.operator("wm.url_open", "Google", icon='SOLO_ON'
-            ).url = "https://www.google.com"
+row.operator("wm.url_open", text="Google", icon='SOLO_ON'
+            ).url = "https://www.google.com"

***  prop text (keyword)
-row.prop(self, "ctrl", "Ctrl", toggle=True)
+row.prop(self, "ctrl", text="Ctrl", toggle=True)

***  prop text (keyword)
-col.prop(self.overlay, "alignment", "")
+col.prop(self.overlay, "alignment", text="")

???  show_x_ray > show_in_front
-col.prop(context.active_object, 'show_x_ray', toggle=False, text='X Ray')
+col.prop(context.active_object, 'show_in_front', toggle=False, text='X Ray')

???  hide > hide_viewport
-bpy.context.object.hide
+bpy.context.object.hide_viewport

???  Group > Collection
-bpy.types.Group()
+bpy.types.Collection()

???  groups > collections
-bpy.data.groups
+bpy.data.collections

???  dupli_group > instance_collection
-context.active_object.dupli_group
+context.active_object.instance_collection

???  link
-scene.objects.link(newCurve)
+coll = context.view_layer.active_layer_collection.collection
+coll.objects.link(newCurve)

???  link
-bpy.context.scene.objects.link(newCurve)
+bpy.context.collection.objects.link(newCurve)
otherwise...
AttributeError: 'bpy_prop_collection' object has no attribute 'link'

???  unlink
-bpy.context.scene.objects.unlink(obj)
+bpy.context.collection.objects.unlink(obj)

???  draw_type > display_type
-bpy.context.object.data.draw_type = 'BBONE'
+bpy.context.object.data.display_type = 'BBONE'

???  draw_size > display_size
-bpy.data.cameras[cam_data_name].draw_size = 1.0
+bpy.data.cameras[cam_data_name].display_size = 1.0

???  uv_textures name
-me.uv_textures.new("Leaves")
+me.uv_layers.new(name="Leaves")

???  transform_apply location rotation scale
-bpy.ops.object.transform_apply(rotation=True, scale=True)
+bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

???  ops _add layers
-bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, 
-    location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), layers=current_layers)
+bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, 
+    location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))

???  view_align
 bpy.ops.curve.primitive_nurbs_path_add(
-  view_align=False, enter_editmode=False, location=(0, 0, 0)
+  align='WORLD', enter_editmode=False, location=(0, 0, 0)
 )

???  mesh.primitive: radius > size
-bpy.ops.mesh.primitive_ico_sphere_add(size=0.2)
+bpy.ops.mesh.primitive_ico_sphere_add(radius=0.4)

???  space_data transform_orientation
-orientation = bpy.context.space_data.transform_orientation
-custom = bpy.context.space_data.current_orientation
-bpy.context.space_data.transform_orientation = 'GLOBAL'
+orient_slot = bpy.context.scene.transform_orientation_slots[0]
+custom = orient_slot.custom_orientation
+bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
otherwise...
AttributeError: 'SpaceView3D' object has no attribute 'transform_orientation'

???  show_manipulator > show_gizmo
-bpy.context.space_data.show_manipulator = False
+bpy.context.space_data.show_gizmo = True
otherwise...
AttributeError: 'SpaceView3D' object has no attribute 'show_manipulator'

???  translate proportional (str) > use_proportional_edit (bool)
-bpy.ops.transform.translate(proportional='DISABLED')
+bpy.ops.transform.translate(use_proportional_edit=False)

???  constraint_orientation > orient_type
-bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=axis, constraint_orientation='GLOBAL')
+bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=axis, orient_type='GLOBAL')

***  user_preferences > preferences
-addons = bpy.context.user_preferences.addons
+addons = bpy.context.preferences.addons

???  user_preferences
-bpy.context.user_preferences.system.use_weight_color_range
+bpy.context.preferences.view.use_weight_color_range
"input.active_keyconfig", "keymap.active_keyconfig"
"input.show_ui_keyconfig", "keymap.show_ui_keyconfig"
"system.author", "filepaths.author"
"system.color_picker_type", "view.color_picker_type"
"system.font_path_ui", "view.font_path_ui"
"system.font_path_ui_mono", "view.font_path_ui_mono"
"system.language", "view.language"
"system.text_hinting", "view.text_hinting"
"system.use_international_fonts", "view.use_international_fonts"
"system.use_scripts_auto_execute", "filepaths.use_scripts_auto_execute"
"system.use_tabs_as_spaces", "filepaths.use_tabs_as_spaces"
"system.use_text_antialiasing", "view.use_text_antialiasing"
"system.use_translate_interface", "view.use_translate_interface"
"system.use_translate_new_dataname", "view.use_translate_new_dataname"
"system.use_translate_tooltips", "view.use_translate_tooltips"
"system.use_weight_color_range", "view.use_weight_color_range"
"system.weight_color_range", "view.weight_color_range"
"view.use_auto_perspective", "input.use_auto_perspective"
"view.use_camera_lock_parent", "input.use_camera_lock_parent"
"view.use_cursor_lock_adjust", "input.use_cursor_lock_adjust"
"view.use_mouse_depth_cursor", "input.use_mouse_depth_cursor"
"view.use_mouse_depth_navigate", "input.use_mouse_depth_navigate"
"view.use_quit_dialog", "view.use_save_prompt"
"view.use_rotate_around_active", "input.use_rotate_around_active"
"view.use_zoom_to_mouse", "input.use_zoom_to_mouse"

???  wm.addon_enable > preferences.addon_enable
-bpy.ops.wm.addon_enable(module=module)
+bpy.ops.preferences.addon_enable(module=module)

???  wm.addon_userpref_show > preferences.addon_show
-layout.operator("wm.addon_userpref_show",
+layout.operator("preferences.addon_show",

???  select_mouse
-mouse_right = context.user_preferences.inputs.select_mouse
+wm = context.window_manager
+keyconfig = wm.keyconfigs.active
+mouse_right = getattr(keyconfig.preferences, "select_mouse", "LEFT")

***  split: percentage > factor
-split = row.split(percentage=0.10, align=True)
+split = row.split(factor=0.10, align=True)

***  row: align (keyword)
-row = col.row(True)
+row = col.row(align=True)
otherwise...
TypeError: UILayout.row(): required parameter "align" to be a keyword argument!

***  scene_update_pre > depsgraph_update_pre
-bpy.app.handlers.scene_update_pre
+bpy.app.handlers.depsgraph_update_pre

***  scene_update_post > depsgraph_update_post
-bpy.app.handlers.scene_update_post.append(check_drivers)
+bpy.app.handlers.depsgraph_update_post.append(check_drivers)

???  scene.update > view_layer.update
-bpy.context.scene.update()
+bpy.context.view_layer.update()

???  use_occlude_geometry > shading.show_xray
-space_data.use_occlude_geometry
+space_data.shading.show_xray
otherwise...
AttributeError: 'SpaceView3D' object has no attribute 'use_occlude_geometry'

???  Matrix Multiplication: * > @
-normal = rotation * mathutils.Vector((0.0, 0.0, 1.0))
+normal = rotation @ mathutils.Vector((0.0, 0.0, 1.0))

???  viewport_shade > space_data.shading
-self.snap_face = context.space_data.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'}
-self.sctx.set_snap_mode(True, True, self.snap_face)
+shading = context.space_data.shading
+self.snap_face = not (snap_edge_and_vert and
+                     (shading.show_xray or shading.type == 'WIREFRAME'))

***  Property (annotations, class def only, not in methods)
-b_prop = bpy.props.BoolProperty(name="Prop Name", default=True)
+b_prop: bpy.props.BoolProperty(name="Prop Name", default=True)
"BoolProperty", "BoolVectorProperty", "CollectionProperty", 
"EnumProperty", "FloatProperty", "FloatVectorProperty",
"IntProperty", "IntVectorProperty",
"PointerProperty", "StringProperty"
otherwise...
Warning: class FOO_OT_bar contains a properties which should be an annotation!
make annotation: FOO_OT_bar.the_int_prop

???  .order
-for k in cls.order:
     if k.startswith(some_str):
-        func, data = getattr(cls, k)
+for k in cls.__annotations__:
     if k.startswith(some_str):
+        func, data = cls.__annotations__[k]
otherwise...
AttributeError: type object 'FOO_OT_bar' has no attribute 'the_int_prop'

???  event_timer_add: time_step (keyword)
-self.timer = wm.event_timer_add(0.05, bpy.context.window)
+self.timer = wm.event_timer_add(time_step=0.05, window=bpy.context.window)

???  frame_set: subframe (keyword)
-context.scene.frame_set(10, 0.25)
+context.scene.frame_set(10, subframe=0.25)

???  INFO_MT_ > TOPBAR_MT_
-box.menu("INFO_MT_file_import", icon='IMPORT')
+box.menu("TOPBAR_MT_file_import", icon='IMPORT')

???  _specials > _context_menu
-scene = context.scene.mat_specials
+scene = context.scene.mat_context_menu
-bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_func)
+bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_func)

???  tweak_threshold > drag_threshold
-tt = context.preferences.inputs.tweak_threshold
+tt = context.preferences.inputs.drag_threshold
otherwise...
rna_uiItemR: property not found: PreferencesInput.tweak_threshold

???  cursor_location > cursor.location
-endvertex = bpy.context.scene.cursor_location
+endvertex = bpy.context.scene.cursor.location

???  snap_element (str) > snap_elements (set)
-bpy.context.tool_settings.snap_element = 'VERTEX'
+bpy.context.tool_settings.snap_elements = {'VERTEX'}
otherwise...
AttributeError: 'ToolSettings' object has no attribute 'snap_element'

???  pivot_point
-pivot = bpy.context.space_data.pivot_point
+pivot = bpy.context.tool_settings.transform_pivot_point
otherwise...
AttributeError: 'SpaceView3D' object has no attribute 'pivot_point'

???  proportional_edit
 ts = context.tool_settings
-ts.proportional_edit = 'ENABLED'
+ts.use_proportional_edit = True

???  resetting header_text_set
-bpy.context.area.header_text_set(text='')
+bpy.context.area.header_text_set(None)

???  register_module > register_class
-bpy.utils.register_module(__name__)
+for cls in classes:
+    bpy.utils.register_class(cls)

???  icon
-row.label(text="Use Properties panel", icon='CURSOR')
+row.label(text="Use Properties panel", icon='PIVOT_CURSOR')
"BUTS", "PROPERTIES"
"CURSOR", "PIVOT_CURSOR"
"FULLSCREEN", "WINDOW"
"IMAGE_COL", "IMAGE"
"IPO", "GRAPH"
"LAMP", "LIGHT"
"LAMP_AREA", "LIGHT_AREA"
"LAMP_DATA", "LIGHT_DATA"
"LAMP_HEMI", "LIGHT_HEMI"
"LAMP_POINT", "LIGHT_POINT"
"LAMP_SPOT", "LIGHT_SPOT"
"LAMP_SUN", "LIGHT_SUN"
"LINK",  #  (maybe use DOT, LAYER_ACTIVE or LAYER_USED)
"LINK_AREA", "LINKED"
"OOPS", "OUTLINER"
"ORTHO", "XRAY"
"OUTLINER_DATA_LAMP", "OUTLINER_DATA_LIGHT"
"OUTLINER_OB_LAMP", "OUTLINER_OB_LIGHT"
"PLUG", "PLUGIN"
"ROTACTIVE", "PIVOT_ACTIVE"
"ROTATECENTER", "PIVOT_MEDIAN"
"ROTATECOLLECTION", "PIVOT_INDIVIDUAL"
"SCRIPTWIN", "PREFERENCES"
"SMOOTH", "SHADING_RENDERED"
"SOLID", "SHADING_SOLID"
"WIRE", "SHADING_WIRE"

"ALIGN", ??
"BBOX", ??
"BORDER_LASSO", ??
"BORDER_RECT", ??
"DOTSDOWN", ??
"DOTSUP", ??
"EDIT", ??
"GAME", ??
"GO_LEFT", ??
"INLINK", ??
"MANIPUL", ??
"MAN_ROT", ??
"MAN_SCALE", ??
"MAN_TRANS", ??
"OOPS", ??
"OPEN_RECENT", ??
"ORTHO", ??
"RADIO", ??
"RECOVER_AUTO", ??
"RENDER_REGION", ??
"ROTACTIVE", ??
"ROTATE", ??
"SAVE_AS", ??
"SAVE_COPY", ??
"SNAP_SURFACE", ??
"SPACE2", ??
"TEMPERATURE", ??