# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "ICity",
    "author" : "ICity", 
    "description" : "一款可以生成3D城市道路建筑景观的blender插件",
    "blender" : (4, 0, 1),
    "version" : (1, 0, 3),
    "location" : "",
    "warning" : "Beta version!",
    "doc_url": "https://shop204936337.taobao.com/", 
    "tracker_url": "https://shop204936337.taobao.com/", 
    "category" : "3D View" 
}


import bpy
import bpy.utils.previews
import os
from bpy.app.handlers import persistent

try:
    from .smart_city import asset_extension, ecology_extension, traffic_extension, pedestrian_extension, template_extension
except ImportError:
    from smart_city import asset_extension, ecology_extension, traffic_extension, pedestrian_extension, template_extension


addon_keymaps = {}
_icons = None
all_assets = {'sna_l': [], }
append = {'sna_asset_type_cat': [], 'sna_city_assets_filtered': [], 'sna_asset_type_cat_2': [], 'sna_all_assets': [], 'sna_theme_filtered': [], 'sna_landscape_filtered': [], 'sna_all_materials': [], 'sna_materials_theme_filtered': [], 'sna_road_materials_filtered': [], 'sna_road_assets_filtered': [], }
hide_assets = {'sna_show_all_v_procedural': False, 'sna_show_all_r_procedural': False, 'sna_show_props_v_procedural': False, 'sna_show_props_r_procedural': False, 'sna_show_all_v_park': False, 'sna_show_all_r_park': False, 'sna_show_grass_v_park': False, 'sna_show_grass_r_park': False, 'sna_show_trees_v_park': False, 'sna_show_trees_r_park': False, }
materials_variables = {'sna_all_materials_enum': [], 'sna_all_materials': [], 'sna_road_materials_filtered_': [], }
variables = {'sna_street_asset_browser': [], 'sna_street_asset': [], 'sna_building_presets': [], 'sna_building_presets_browser': [], 'sna_landscape_browser': [], 'sna_edit_city': False, 'sna_road_materials': [], 'sna_road_materials_browser': [], 'sna_procedural_building_browser': [], 'sna_procedural_building': [], 'sna_landscape_list': [], 'sna_theme': [], 'sna_park_browser': [], 'sna_park_list': [], 'sna_attributes': [], 'sna_sidewalk_curb_mat': [], 'sna_sidewalk_mat': [], }
append_vars_AA8BD = {}


def get_blend_contents(path, data_type):
    if os.path.exists(path):
        with bpy.data.libraries.load(path) as (data_from, data_to):
            return getattr(data_from, data_type)
    return []


def sna_remove_last_path_5D152_A1BA7(String):
    return String.replace('\\' + String.split('\\')[int(len(String.split('\\')) - 1.0)], '')


def sna_remove_last_path_5D152_215A6(String):
    return String.replace('\\' + String.split('\\')[int(len(String.split('\\')) - 1.0)], '')


_item_map = dict()


def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]


def sna_update_sna_city_space_type_append_A7B1C(self, context):
    sna_updated_prop = self.sna_city_space_type_append
    bpy.ops.sna.filter_city_assets_ea982('INVOKE_DEFAULT', )


append_vars_48E33 = {}


def sna_filter_list__4A11C_48E33(List):
    append['sna_city_assets_filtered'] = []
    for i_B4720 in range(len(append['sna_theme_filtered'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_theme_filtered'][i_B4720][0]:
                append['sna_city_assets_filtered'].append(append['sna_theme_filtered'][i_B4720])
    return append['sna_city_assets_filtered']


append_vars_B2349 = {}


def sna_filter_list__4A11C_B2349(List):
    append['sna_landscape_filtered'] = []
    for i_B4720 in range(len(append['sna_theme_filtered'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_theme_filtered'][i_B4720][0]:
                append['sna_landscape_filtered'].append(append['sna_theme_filtered'][i_B4720])
    return append['sna_landscape_filtered']


def sna_update_sna_street_asset_type_append_FC104(self, context):
    sna_updated_prop = self.sna_street_asset_type_append
    bpy.ops.sna.filter_road_bc600('INVOKE_DEFAULT', )


append_vars_F9AC6 = {}


def sna_filter_list__4A11C_F9AC6(List):
    append['sna_road_assets_filtered'] = []
    for i_B4720 in range(len(append['sna_theme_filtered'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_theme_filtered'][i_B4720][0]:
                append['sna_road_assets_filtered'].append(append['sna_theme_filtered'][i_B4720])
    return append['sna_road_assets_filtered']


append_vars_F30E5 = {}


def sna_filter_list__4A11C_F30E5(List):
    append['sna_road_materials_filtered'] = []
    for i_B4720 in range(len(append['sna_all_assets'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_all_assets'][i_B4720][0]:
                append['sna_road_materials_filtered'].append(append['sna_all_assets'][i_B4720])
    return append['sna_road_materials_filtered']


def sna_update_sna_city_building_presets_type_append_A77BA(self, context):
    sna_updated_prop = self.sna_city_building_presets_type_append
    bpy.ops.sna.filter_city_assets_ea982('INVOKE_DEFAULT', )


def sna_update_sna_road_materials_type_append_CB7F1(self, context):
    sna_updated_prop = self.sna_road_materials_type_append
    bpy.ops.sna.filter_road_bc600('INVOKE_DEFAULT', )


append_vars_503EF = {}


def sna_filter_list__4A11C_503EF(List):
    append['sna_theme_filtered'] = []
    for i_B4720 in range(len(append['sna_all_assets'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_all_assets'][i_B4720][0]:
                append['sna_theme_filtered'].append(append['sna_all_assets'][i_B4720])
    return append['sna_theme_filtered']


append_vars_1E8BF = {}


def sna_filter_list__4A11C_1E8BF(List):
    append['sna_materials_theme_filtered'] = []
    for i_B4720 in range(len(append['sna_all_materials'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_all_materials'][i_B4720][0]:
                append['sna_materials_theme_filtered'].append(append['sna_all_materials'][i_B4720])
    return append['sna_materials_theme_filtered']


def sna_update_sna_theme_88C83(self, context):
    sna_updated_prop = self.sna_theme
    bpy.ops.sna.filter_theme_31d4c('INVOKE_DEFAULT', )
    bpy.ops.sna.filter_road_bc600('INVOKE_DEFAULT', )
    bpy.ops.sna.filter_city_assets_ea982('INVOKE_DEFAULT', )


hide_assets_vars_E8BEE = {}


def sna_hide_assets_viewport_92CB5_E8BEE(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_all_r_park'] = not hide_assets['sna_show_all_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_all_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


hide_assets_vars_982E5 = {}


def sna_hide_assets_viewport_92CB5_982E5(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_grass_r_park'] = not hide_assets['sna_show_grass_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_grass_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


hide_assets_vars_1E48D = {}


def sna_hide_assets_viewport_92CB5_1E48D(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_grass_v_park'] = not hide_assets['sna_show_grass_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_grass_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


hide_assets_vars_E138F = {}


def sna_hide_assets_viewport_92CB5_E138F(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_trees_r_park'] = not hide_assets['sna_show_trees_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_trees_r_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


hide_assets_vars_8DFD5 = {}


def sna_hide_assets_viewport_92CB5_8DFD5(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_trees_v_park'] = not hide_assets['sna_show_trees_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_trees_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


hide_assets_vars_3361F = {}


def sna_hide_assets_viewport_92CB5_3361F(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_all_v_park'] = not hide_assets['sna_show_all_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_all_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'OBJECT', 'DATA'}, )
    return


def sna_update_sna_proxy_mode_0EBCB(self, context):
    sna_updated_prop = self.sna_proxy_mode
    if property_exists("bpy.data.node_groups['Hide viewport input'].nodes['Proxy buildings'].inputs[0].default_value", globals(), locals()):
        bpy.data.node_groups['Hide viewport input'].nodes['Proxy buildings'].inputs[0].default_value = sna_updated_prop
    bpy.data.node_groups['ICity Proxy'].nodes['Light'].inputs[0].default_value = sna_updated_prop


visual_scripting_editor_vars_867FF = {}


def sna_generate_icon_list_from_collection_6BD3F_867FF(Collection):
    materials_variables['sna_all_materials'] = []
    for i_037A6 in range(len(Collection)):
        materials_variables['sna_all_materials'].append(Collection[i_037A6].name)
    materials_variables['sna_all_materials'] = sorted(materials_variables['sna_all_materials'], reverse=False)
    return materials_variables['sna_all_materials']


def sna_update_sna_road_materials_type__75061(self, context):
    sna_updated_prop = self.sna_road_materials_type_
    bpy.ops.sna.material_filter_f04c3('INVOKE_DEFAULT', )
    bpy.ops.sna.road_materials_filter_6a3ec('INVOKE_DEFAULT', )


append_vars_71E86 = {}


def sna_filter_list__4A11C_71E86(List):
    materials_variables['sna_road_materials_filtered_'] = []
    for i_B4720 in range(len(materials_variables['sna_all_materials_enum'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in materials_variables['sna_all_materials_enum'][i_B4720][0]:
                materials_variables['sna_road_materials_filtered_'].append(materials_variables['sna_all_materials_enum'][i_B4720])
    return materials_variables['sna_road_materials_filtered_']


visual_scripting_editor_vars_5001C = {}


def sna_set_active_attribute_572EC_5001C(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_A11A7 = {}


def sna_set_active_attribute_572EC_A11A7(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_30DFB = {}


def sna_set_active_attribute_572EC_30DFB(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_1DA63 = {}


def sna_set_active_attribute_572EC_1DA63(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_E3814 = {}


def sna_set_active_attribute_572EC_E3814(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_5FBBE = {}


def sna_set_active_attribute_572EC_5FBBE(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_0978B = {}


def sna_set_active_attribute_572EC_0978B(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_813E4 = {}


def sna_set_active_attribute_572EC_813E4(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_4CC88 = {}


def sna_set_active_attribute_572EC_4CC88(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_FD2DC = {}


def sna_set_active_attribute_572EC_FD2DC(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_2F07A = {}


def sna_set_active_attribute_572EC_2F07A(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_92991 = {}


def sna_set_active_attribute_572EC_92991(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_41053 = {}


def sna_set_active_attribute_572EC_41053(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_0DB67 = {}


def sna_set_active_attribute_572EC_0DB67(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_6A49A = {}


def sna_store_atrributes_list_D7786_6A49A():
    variables['sna_attributes'] = []
    for i_0900E in range(len(bpy.context.active_object.data.attributes)):
        variables['sna_attributes'].append(bpy.context.active_object.data.attributes[i_0900E].name)
    variables['sna_attributes'] = variables['sna_attributes']
    return variables['sna_attributes']


visual_scripting_editor_vars_AE34F = {}


def sna_set_active_attribute_572EC_AE34F(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_BBC9A = {}


def sna_set_active_attribute_572EC_BBC9A(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_7B5C3 = {}


def sna_set_active_attribute_572EC_7B5C3(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_81051 = {}


def sna_set_active_attribute_572EC_81051(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_5CC3C = {}


def sna_set_active_attribute_572EC_5CC3C(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_997D9 = {}


def sna_set_active_attribute_572EC_997D9(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


def sna_move_to_collection_A3C17_7B15A(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


def sna_move_to_collection_A3C17_97000(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


def sna_move_to_collection_A3C17_D6B3F(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


def sna_move_to_collection_A3C17_D47A1(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


def sna_move_to_collection_A3C17_575C9(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


visual_scripting_editor_vars_62FA0 = {}


def sna_set_active_attribute_572EC_62FA0(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


visual_scripting_editor_vars_42E3D = {}


def sna_set_active_attribute_572EC_42E3D(Name):
    bpy.context.active_object.data.attributes.active_index = variables['sna_attributes'].index(bpy.context.active_object.data.attributes[Name].name)
    return


def sna_update_sna_street_asset_type_append_F3D9F(self, context):
    sna_updated_prop = self.sna_street_asset_type_append
    listed_enum_0_83b17 = sna_sidewalk_mat_C9E1B()
    result_0_08a09, path_1_08a09, output_2_08a09, filtered_3_08a09 = sna_street_assets_lists_1588D()


def sna_update_sna_city_space_type_F658C(self, context):
    sna_updated_prop = self.sna_city_space_type
    bpy.ops.sna.filter_presets_fb5a4()
    bpy.ops.sna.park_filter_5a7a2()
    bpy.ops.sna.procedural_building_filter_05bed()
    bpy.ops.sna.landscape_filter_0bf89()


def sna_update_sna_street_asset_type_BF136(self, context):
    sna_updated_prop = self.sna_street_asset_type
    bpy.ops.sna.filter_street_assets_c5c0e('INVOKE_DEFAULT', )
    bpy.ops.sna.material_filter_f04c3()
    bpy.ops.sna.road_materials_filter_6a3ec()


visual_scripting_editor_vars_EAC41 = {}


def sna_generate_icon_list_from_collection_6BD3F_EAC41(Collection):
    variables['sna_procedural_building'] = []
    for i_037A6 in range(len(Collection)):
        variables['sna_procedural_building'].append(Collection[i_037A6].name)
    variables['sna_procedural_building'] = sorted(variables['sna_procedural_building'], reverse=False)
    return variables['sna_procedural_building']


visual_scripting_editor_vars_B83D7 = {}


def sna_generate_icon_list_from_collection_6BD3F_B83D7(Collection):
    variables['sna_park_list'] = []
    for i_037A6 in range(len(Collection)):
        variables['sna_park_list'].append(Collection[i_037A6].name)
    variables['sna_park_list'] = sorted(variables['sna_park_list'], reverse=False)
    return variables['sna_park_list']


visual_scripting_editor_vars_BBAA3 = {}


def sna_generate_icon_list_from_collection_6BD3F_BBAA3(Collection):
    variables['sna_landscape_list'] = []
    for i_037A6 in range(len(Collection)):
        variables['sna_landscape_list'].append(Collection[i_037A6].name)
    variables['sna_landscape_list'] = sorted(variables['sna_landscape_list'], reverse=False)
    return variables['sna_landscape_list']


def sna_update_sna_city_building_presets_type_FB155(self, context):
    sna_updated_prop = self.sna_city_building_presets_type
    bpy.ops.sna.filter_presets_fb5a4()


visual_scripting_editor_vars_EDBEF = {}


def sna_generate_icon_list_from_collection_6BD3F_EDBEF(Collection):
    variables['sna_street_asset'] = []
    for i_037A6 in range(len(Collection)):
        variables['sna_street_asset'].append(Collection[i_037A6].name)
    variables['sna_street_asset'] = sorted(variables['sna_street_asset'], reverse=False)
    return variables['sna_street_asset']


visual_scripting_editor_vars_593DA = {}


def sna_generate_icon_list_from_collection_6BD3F_593DA(Collection):
    variables['sna_street_asset'] = []
    for i_037A6 in range(len(Collection)):
        variables['sna_street_asset'].append(Collection[i_037A6].name)
    variables['sna_street_asset'] = sorted(variables['sna_street_asset'], reverse=False)
    return variables['sna_street_asset']


def sna_update_sna_city_space_type_AE473(self, context):
    sna_updated_prop = self.sna_city_space_type


def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id


def property_exists(prop_path, glob, loc):
    try:
        eval(prop_path, glob, loc)
        return True
    except:
        return False


class SNA_OT_Store_All_Assets_5B09E(bpy.types.Operator):
    bl_idname = "sna.store_all_assets_5b09e"
    bl_label = "Store all assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_property = 'sna_assets'
    sna_assets: bpy.props.StringProperty(name='Assets', description='', default='', subtype='NONE', maxlen=0)
    sna_materials: bpy.props.StringProperty(name='Materials', description='', default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        with open(os.path.join(r'C:\Users\hothifa\Desktop\New folder (4)',self.sna_assets), mode='w') as file_B938B:
            file_B938B.seek(0)
            file_B938B.write('')
            file_B938B.truncate()
        for i_01B64 in range(len(append['sna_all_assets'])):
            with open(os.path.join(r'C:\Users\hothifa\Desktop\New folder (4)',self.sna_assets), mode='a') as file_B8646:
                file_B8646.write(str(append['sna_all_assets'][i_01B64]))
            with open(os.path.join(r'C:\Users\hothifa\Desktop\New folder (4)',self.sna_materials), mode='w') as file_77F2E:
                file_77F2E.seek(0)
                file_77F2E.write('')
                file_77F2E.truncate()
            for i_7F837 in range(len(append['sna_all_materials'])):
                with open(os.path.join(r'C:\Users\hothifa\Desktop\New folder (4)',self.sna_materials), mode='a') as file_B2545:
                    file_B2545.write(str(append['sna_all_materials'][i_7F837]))
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'sna_assets', text='Assets', icon_value=0, emboss=True)
        layout.prop(self, 'sna_materials', text='M', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

# 变量存储起点
class SNA_OT_Refresh_Theme_443Bd(bpy.types.Operator):
    bl_idname = "sna.refresh_theme_443bd"
    bl_label = "REFRESH theme"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        append['sna_all_assets'] = []
        variables['sna_theme'] = []
        append['sna_all_materials'] = []
        for i_44F70 in range(len([f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))])):
            variables['sna_theme'].append([[f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_44F70], [f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_44F70], '', 0])
        bpy.ops.sna.read_97c87('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Refresh_C6Cb8(bpy.types.Operator):
    bl_idname = "sna.refresh_c6cb8"
    bl_label = "REFRESH"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        append['sna_all_assets'] = []
        variables['sna_theme'] = []
        append['sna_all_materials'] = []
        for i_83C0D in range(len([f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))])):
            variables['sna_theme'].append([[f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_83C0D], [f for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_83C0D], '', 0])
            append['sna_all_materials'] = []
            append['sna_all_assets'] = []
            for i_C1B5F in range(len([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))])):
                print([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F])
                for i_F84DA in range(len([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))])):
                    if 'textures' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]:
                        pass
                    else:
                        if ('Procedural' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA] or 'Park' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA] or 'Landscape' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]):
                            for i_135F8 in range(len([f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))])):
                                if ('.blend' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA] + '\\' + [f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8] and (not '.blend1' in [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA] + '\\' + [f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8])):
                                    print([f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8].replace('.blend', ''))
                                    append['sna_all_assets'].append([[f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8].replace('.blend', ''), [f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8].replace('.blend', ''), [os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA] + '\\' + [f for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_135F8], 0])
                        else:
                            print(str([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))]))
                            for i_82365 in range(len([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))])):
                                print([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365])
                                if ('.blend' in [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365] and (not '.blend1' in [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365])):
                                    if 'Materials' in [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365]:
                                        for i_25698 in range(len(get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'materials'))):
                                            print(str([get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'materials')[i_25698], get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'materials')[i_25698], [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 0]))
                                            append['sna_all_materials'].append([get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'materials')[i_25698], get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'materials')[i_25698], [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 0])
                                    else:
                                        for i_1C51B in range(len(get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'objects'))):
                                            print(get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'objects')[i_1C51B])
                                            append['sna_all_assets'].append([get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'objects')[i_1C51B], get_blend_contents([os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 'objects')[i_1C51B], [os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f) for f in os.listdir([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA]) if os.path.isfile(os.path.join([os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f) for f in os.listdir([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]) if os.path.isdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F], f))][i_F84DA], f))][i_82365], 0])
            append['sna_all_assets'].append(['Services_' + os.path.basename([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]), 'Services_' + os.path.basename([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]), os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'Road','Road assets.blend'), 0])
            append['sna_all_assets'].append(['Imperfections_' + os.path.basename([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]), 'Imperfections_' + os.path.basename([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F]), os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'Road','Road assets.blend'), 0])
            with open(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'All assets'), mode='w') as file_79393:
                file_79393.seek(0)
                file_79393.write('')
                file_79393.truncate()
            for i_DAC5F in range(len(append['sna_all_assets'])):
                with open(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'All assets'), mode='a') as file_7F70C:
                    file_7F70C.write(str(append['sna_all_assets'][i_DAC5F]))
                with open(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'All materials'), mode='w') as file_C4C79:
                    file_C4C79.seek(0)
                    file_C4C79.write('')
                    file_C4C79.truncate()
                for i_0EF82 in range(len(append['sna_all_materials'])):
                    with open(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_C1B5F],'All materials'), mode='a') as file_C219A:
                        file_C219A.write(str(append['sna_all_materials'][i_0EF82]))
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text='This may take a long time!', icon_value=2)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class SNA_OT_Read_97C87(bpy.types.Operator):
    bl_idname = "sna.read_97c87"
    bl_label = "Read"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        for i_48027 in range(len([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))])):
            print([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027])
            all_assets['sna_l'] = []
            for i_74205 in range(len([os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f) for f in os.listdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],)) if os.path.isfile(os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f))])):
                print(os.path.join('','assets','Assets'))
                text_928F4 = ""
                lines_928F4 = []
                if os.path.exists([os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f) for f in os.listdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],)) if os.path.isfile(os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f))][i_74205]):
                    with open([os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f) for f in os.listdir(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],)) if os.path.isfile(os.path.join(os.path.join([os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f) for f in os.listdir(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))) if os.path.isdir(os.path.join(sna_assets_path_7BE86(os.path.join(os.path.dirname(__file__), 'assets', 'Assets')), f))][i_48027],), f))][i_74205], "r") as file_928F4:
                        lines_928F4 = list(map(lambda l: l.strip(), file_928F4.readlines()))
                        text_928F4 = "\n".join(lines_928F4)
                print(text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')))
                for i_C26C7 in range(len(text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')).split(']'))):
                    if (text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')).split(']')[i_C26C7] == ''):
                        pass
                    else:
                        for i_B308C in range(len(text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')).split(']')[i_C26C7].replace('[', '').split(','))):
                            if (text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')).split(']')[i_C26C7].replace('[', '').split(',')[i_B308C] == ''):
                                pass
                            else:
                                all_assets['sna_l'].append(text_928F4.replace('G:\\\\My Drive\\\\Building\\\\Assets', os.path.join(os.path.dirname(__file__), 'assets', 'Assets')).split(']')[i_C26C7].replace('[', '').split(',')[i_B308C].replace("'", '').replace('"', ''))
            append['sna_all_assets'] = []
            for i_E241D in range(int(len(all_assets['sna_l']) / 4.0)):
                append['sna_all_assets'].append([all_assets['sna_l'][int(i_E241D * 4.0)].strip(), all_assets['sna_l'][int(i_E241D * 4.0)].strip(), all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)].strip().replace('\\\\', '\\'), (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + 'Custom asset.png') if (load_preview_icon(r'') == load_preview_icon(os.path.join(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + all_assets['sna_l'][int(i_E241D * 4.0)] + '.png',).strip())) else load_preview_icon(os.path.join(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + all_assets['sna_l'][int(i_E241D * 4.0)] + '.png',).strip()))) else (load_preview_icon(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + 'Custom asset.png') if (load_preview_icon(r'') == load_preview_icon(os.path.join(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + all_assets['sna_l'][int(i_E241D * 4.0)] + '.png',).strip())) else load_preview_icon(os.path.join(sna_remove_last_path_5D152_A1BA7(all_assets['sna_l'][int(int(i_E241D * 4.0) + 2.0)]) + '\\' + all_assets['sna_l'][int(i_E241D * 4.0)] + '.png',).strip())))])
            append['sna_all_materials'] = []
            for i_41DE6 in range(int(len(all_assets['sna_l']) / 4.0)):
                append['sna_all_materials'].append([all_assets['sna_l'][int(i_41DE6 * 4.0)].strip(), all_assets['sna_l'][int(i_41DE6 * 4.0)].strip(), all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\'), (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(os.path.join(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png',).strip()) == (load_preview_icon(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)] + '\\' + 'Custom asset.png') if (load_preview_icon(os.path.join(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png',).strip()) == load_preview_icon(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png')) else load_preview_icon(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png'))) else (load_preview_icon(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)] + '\\' + 'Custom asset.png') if (load_preview_icon(os.path.join(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png',).strip()) == load_preview_icon(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png')) else load_preview_icon(sna_remove_last_path_5D152_215A6(all_assets['sna_l'][int(int(i_41DE6 * 4.0) + 2.0)].strip().replace('\\\\', '\\')) + '\\' + all_assets['sna_l'][int(i_41DE6 * 4.0)] + '.png')))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# sna_assets_path_7BE86函数
def sna_assets_path_7BE86(Assets):
    return (Assets if (bpy.context.preferences.addons['icity'].preferences.sna_assets_path == '') else bpy.context.preferences.addons['icity'].preferences.sna_assets_path)


def sna_road_browser_append_enum_items(self, context):
    enum_items = append['sna_road_assets_filtered']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_OT_Filter_City_Assets_Ea982(bpy.types.Operator):
    bl_idname = "sna.filter_city_assets_ea982"
    bl_label = "filter City assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        print(bpy.context.scene.sna_city_space_type_append)
        filtered_0_48e33 = sna_filter_list__4A11C_48E33([bpy.context.scene.sna_city_space_type_append])
        print(str(filtered_0_48e33), str([bpy.context.scene.sna_city_space_type_append]))
        filtered_0_b2349 = sna_filter_list__4A11C_B2349(['Landscape'])
        print(str(filtered_0_b2349))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_city_browser_append_enum_items(self, context):
    enum_items = append['sna_city_assets_filtered']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_landscape_browser_append_enum_items(self, context):
    enum_items = append['sna_landscape_filtered']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_road_materials_browser_append_enum_items(self, context):
    enum_items = append['sna_road_materials_filtered']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_theme_enum_items(self, context):
    enum_items = variables['sna_theme']
    return [make_enum_item(item[0], item[1], item[2], item[3], 2**i) for i, item in enumerate(enum_items)]


class SNA_OT_Filter_Road_Bc600(bpy.types.Operator):
    bl_idname = "sna.filter_road_bc600"
    bl_label = "filter road"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        print('')
        filtered_0_f9ac6 = sna_filter_list__4A11C_F9AC6([bpy.context.scene.sna_street_asset_type_append])
        print(str(filtered_0_f9ac6))
        filtered_0_f30e5 = sna_filter_list__4A11C_F30E5([bpy.context.scene.sna_road_materials_type_append])
        print(str(filtered_0_f30e5))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_filter_list__4A11C(List):
    append['sna_theme_filtered'] = []
    for i_B4720 in range(len(append['sna_all_assets'])):
        for i_9206E in range(len(List)):
            if List[i_9206E] in append['sna_all_assets'][i_B4720][0]:
                append['sna_theme_filtered'].append(append['sna_all_assets'][i_B4720])
    return append['sna_theme_filtered']


class SNA_OT_Filter_Theme_31D4C(bpy.types.Operator):
    bl_idname = "sna.filter_theme_31d4c"
    bl_label = "filter theme"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        filtered_0_503ef = sna_filter_list__4A11C_503EF(list(bpy.context.scene.sna_theme))
        print(str(filtered_0_503ef))
        filtered_0_1e8bf = sna_filter_list__4A11C_1E8BF(list(bpy.context.scene.sna_theme))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_MT_89AD5(bpy.types.Menu):
    bl_idname = "SNA_MT_89AD5"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=3)
        layout.operator_context = "INVOKE_DEFAULT"
        layout.template_icon(icon_value=242, scale=12.0)


class SNA_MT_8CD9F(bpy.types.Menu):
    bl_idname = "SNA_MT_8CD9F"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=2)
        layout.operator_context = "INVOKE_DEFAULT"


def sna_test_enum_items(self, context):
    enum_items = [['zz', 'zz', 'df', 242], ['vb', 'vb', 'jh', 31]]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_MT_0BED6(bpy.types.Menu):
    bl_idname = "SNA_MT_0BED6"
    bl_label = "zz"

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=1)
        layout.operator_context = "INVOKE_DEFAULT"
        grid_83B36 = layout.grid_flow(columns=2, row_major=False, even_columns=False, even_rows=True, align=False)
        grid_83B36.enabled = True
        grid_83B36.active = True
        grid_83B36.use_property_split = False
        grid_83B36.use_property_decorate = False
        grid_83B36.alignment = 'Expand'.upper()
        grid_83B36.scale_x = 1.0
        grid_83B36.scale_y = 1.0
        if not True: grid_83B36.operator_context = "EXEC_DEFAULT"
        grid_83B36.prop_enum(bpy.context.scene, 'sna_test', text='541', value='zz')


class SNA_OT_Append_Panel_Lunch_221D5(bpy.types.Operator):
    bl_idname = "sna.append_panel_lunch_221d5"
    bl_label = "Append panel lunch"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You cant append in edit mode!')
        return not 'EDIT' in bpy.context.mode

    def execute(self, context):
        bpy.ops.wm.call_panel(name="SNA_PT_APPEND_PANEL_590A1", keep_open=True)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_PT_APPEND_PANEL_590A1(bpy.types.Panel):
    bl_label = 'Append panel'
    bl_idname = 'SNA_PT_APPEND_PANEL_590A1'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_context = ''
    bl_order = 0
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_E44A7 = layout.row(heading='', align=True)
        row_E44A7.alert = False
        row_E44A7.enabled = True
        row_E44A7.active = True
        row_E44A7.use_property_split = False
        row_E44A7.use_property_decorate = False
        row_E44A7.scale_x = 1.0
        row_E44A7.scale_y = 1.0
        row_E44A7.alignment = 'Expand'.upper()
        row_E44A7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_E44A7.operator('sna.open_addon_prefrences_34afe', text='Addon preferences', icon_value=117, emboss=True, depress=False)
        op = row_E44A7.operator('sna.refresh_theme_443bd', text='', icon_value=692, emboss=True, depress=False)
        box_E3D9D = layout.box()
        box_E3D9D.alert = False
        box_E3D9D.enabled = True
        box_E3D9D.active = True
        box_E3D9D.use_property_split = False
        box_E3D9D.use_property_decorate = False
        box_E3D9D.alignment = 'Expand'.upper()
        box_E3D9D.scale_x = 1.0
        box_E3D9D.scale_y = 1.0
        if not True: box_E3D9D.operator_context = "EXEC_DEFAULT"
        box_E3D9D.template_icon(icon_value=77, scale=2.0)
        grid_7BE28 = box_E3D9D.grid_flow(columns=3, row_major=False, even_columns=True, even_rows=False, align=True)
        grid_7BE28.enabled = True
        grid_7BE28.active = True
        grid_7BE28.use_property_split = False
        grid_7BE28.use_property_decorate = False
        grid_7BE28.alignment = 'Expand'.upper()
        grid_7BE28.scale_x = 1.0
        grid_7BE28.scale_y = 1.5
        if not True: grid_7BE28.operator_context = "EXEC_DEFAULT"
        grid_7BE28.prop(bpy.context.scene, 'sna_theme', text=str(list(bpy.context.scene.sna_theme)), icon_value=0, emboss=True, expand=True)
        if (list(bpy.context.scene.sna_theme) == []):
            box_C425C = grid_7BE28.box()
            box_C425C.alert = True
            box_C425C.enabled = True
            box_C425C.active = True
            box_C425C.use_property_split = False
            box_C425C.use_property_decorate = False
            box_C425C.alignment = 'Center'.upper()
            box_C425C.scale_x = 1.0
            box_C425C.scale_y = 1.0
            if not True: box_C425C.operator_context = "EXEC_DEFAULT"
            box_C425C.label(text='No themes loaded', icon_value=2)
        row_5299A = layout.row(heading='', align=False)
        row_5299A.alert = False
        row_5299A.enabled = True
        row_5299A.active = True
        row_5299A.use_property_split = False
        row_5299A.use_property_decorate = False
        row_5299A.scale_x = 1.0
        row_5299A.scale_y = 2.2810001373291016
        row_5299A.alignment = 'Expand'.upper()
        row_5299A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_5299A.prop(bpy.context.scene, 'sna_citystreet_append', text=bpy.context.scene.sna_citystreet_append, icon_value=0, emboss=True, expand=True)
        if bpy.context.scene.sna_citystreet_append == "Road":
            col_9EE10 = layout.column(heading='', align=False)
            col_9EE10.alert = False
            col_9EE10.enabled = True
            col_9EE10.active = True
            col_9EE10.use_property_split = False
            col_9EE10.use_property_decorate = False
            col_9EE10.scale_x = 1.0
            col_9EE10.scale_y = 1.0
            col_9EE10.alignment = 'Expand'.upper()
            col_9EE10.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_4CF7C = col_9EE10.box()
            box_4CF7C.alert = False
            box_4CF7C.enabled = True
            box_4CF7C.active = True
            box_4CF7C.use_property_split = False
            box_4CF7C.use_property_decorate = False
            box_4CF7C.alignment = 'Expand'.upper()
            box_4CF7C.scale_x = 1.0
            box_4CF7C.scale_y = 1.0
            if not True: box_4CF7C.operator_context = "EXEC_DEFAULT"
            col_EB3DE = box_4CF7C.column(heading='', align=False)
            col_EB3DE.alert = False
            col_EB3DE.enabled = True
            col_EB3DE.active = True
            col_EB3DE.use_property_split = False
            col_EB3DE.use_property_decorate = False
            col_EB3DE.scale_x = 1.0
            col_EB3DE.scale_y = 1.0
            col_EB3DE.alignment = 'Expand'.upper()
            col_EB3DE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            grid_86524 = col_EB3DE.grid_flow(columns=2, row_major=True, even_columns=False, even_rows=False, align=True)
            grid_86524.enabled = True
            grid_86524.active = True
            grid_86524.use_property_split = False
            grid_86524.use_property_decorate = False
            grid_86524.alignment = 'Expand'.upper()
            grid_86524.scale_x = 1.0
            grid_86524.scale_y = 1.0
            if not True: grid_86524.operator_context = "EXEC_DEFAULT"
            grid_86524.prop(bpy.context.scene, 'sna_street_asset_type_append', text='.', icon_value=0, emboss=True, expand=True)
            if bpy.context.scene.sna_street_asset_type_append == "Cars":
                box_41A34 = box_4CF7C.box()
                box_41A34.alert = False
                box_41A34.enabled = True
                box_41A34.active = True
                box_41A34.use_property_split = False
                box_41A34.use_property_decorate = False
                box_41A34.alignment = 'Expand'.upper()
                box_41A34.scale_x = 1.0
                box_41A34.scale_y = 2.0
                if not True: box_41A34.operator_context = "EXEC_DEFAULT"
                box_41A34.label(text='Coming soon!', icon_value=16)
            elif bpy.context.scene.sna_street_asset_type_append == "Texture":
                box_4CF7C.prop(bpy.context.scene, 'sna_road_materials_type_append', text='Type', icon_value=0, emboss=True)
                box_4CF7C.template_icon_view(bpy.context.scene, 'sna_road_materials_browser_append', show_labels=True, scale=7.0, scale_popup=7.0)
            else:
                box_4CF7C.template_icon_view(bpy.context.scene, 'sna_road_browser_append', show_labels=True, scale=7.0, scale_popup=7.0)
        elif bpy.context.scene.sna_citystreet_append == "City":
            col_504E8 = layout.column(heading='', align=True)
            col_504E8.alert = False
            col_504E8.enabled = True
            col_504E8.active = True
            col_504E8.use_property_split = False
            col_504E8.use_property_decorate = False
            col_504E8.scale_x = 1.0
            col_504E8.scale_y = 1.0
            col_504E8.alignment = 'Expand'.upper()
            col_504E8.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
            row_F0AB4 = col_504E8.row(heading='', align=False)
            row_F0AB4.alert = False
            row_F0AB4.enabled = True
            row_F0AB4.active = True
            row_F0AB4.use_property_split = False
            row_F0AB4.use_property_decorate = False
            row_F0AB4.scale_x = 1.0
            row_F0AB4.scale_y = 1.0
            row_F0AB4.alignment = 'Expand'.upper()
            row_F0AB4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_F0AB4.prop(bpy.context.scene, 'sna_city_space_type_append', text=bpy.context.scene.sna_city_space_type_append, icon_value=0, emboss=True, expand=True)
            if bpy.context.scene.sna_city_space_type_append == "Presets":
                box_CDBC6 = col_504E8.box()
                box_CDBC6.alert = False
                box_CDBC6.enabled = True
                box_CDBC6.active = True
                box_CDBC6.use_property_split = False
                box_CDBC6.use_property_decorate = False
                box_CDBC6.alignment = 'Expand'.upper()
                box_CDBC6.scale_x = 1.0
                box_CDBC6.scale_y = 1.0
                if not True: box_CDBC6.operator_context = "EXEC_DEFAULT"
                col_CED62 = box_CDBC6.column(heading='', align=True)
                col_CED62.alert = False
                col_CED62.enabled = True
                col_CED62.active = True
                col_CED62.use_property_split = False
                col_CED62.use_property_decorate = False
                col_CED62.scale_x = 1.0
                col_CED62.scale_y = 1.0
                col_CED62.alignment = 'Expand'.upper()
                col_CED62.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                col_CED62.template_icon_view(bpy.context.scene, 'sna_landscape_browser_append', show_labels=True, scale=7.0, scale_popup=7.0)
                box_0AB48 = col_CED62.box()
                box_0AB48.alert = False
                box_0AB48.enabled = True
                box_0AB48.active = True
                box_0AB48.use_property_split = True
                box_0AB48.use_property_decorate = False
                box_0AB48.alignment = 'Expand'.upper()
                box_0AB48.scale_x = 1.0
                box_0AB48.scale_y = 3.0999999046325684
                if not True: box_0AB48.operator_context = "EXEC_DEFAULT"
                op = box_0AB48.operator('sna.append_landscape_c97bb', text='Append', icon_value=0, emboss=True, depress=False)
            else:
                pass
            box_F5BD4 = col_504E8.box()
            box_F5BD4.alert = False
            box_F5BD4.enabled = True
            box_F5BD4.active = True
            box_F5BD4.use_property_split = False
            box_F5BD4.use_property_decorate = False
            box_F5BD4.alignment = 'Expand'.upper()
            box_F5BD4.scale_x = 1.0
            box_F5BD4.scale_y = 1.0
            if not True: box_F5BD4.operator_context = "EXEC_DEFAULT"
            box_F5BD4.template_icon_view(bpy.context.scene, 'sna_city_browser_append', show_labels=True, scale=7.0, scale_popup=7.0)
        else:
            pass
        box_6ACD3 = layout.box()
        box_6ACD3.alert = False
        box_6ACD3.enabled = True
        box_6ACD3.active = True
        box_6ACD3.use_property_split = True
        box_6ACD3.use_property_decorate = False
        box_6ACD3.alignment = 'Expand'.upper()
        box_6ACD3.scale_x = 1.0
        box_6ACD3.scale_y = 3.0999999046325684
        if not True: box_6ACD3.operator_context = "EXEC_DEFAULT"
        op = box_6ACD3.operator('sna.append_assets_ffd74', text='Append', icon_value=0, emboss=True, depress=False)


class SNA_OT_Open_Addon_Prefrences_34Afe(bpy.types.Operator):
    bl_idname = "sna.open_addon_prefrences_34afe"
    bl_label = "Open addon prefrences"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT', section='ADDONS')
        bpy.data.window_managers['WinMan'].addon_search = 'ICity'
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_hide_assets_viewport_92CB5(Collection, Input_name):
    for i_B7E96 in range(len(bpy.data.collections[Collection].all_objects)):
        for i_D4098 in range(len(bpy.data.collections[Collection].all_objects[i_B7E96].modifiers)):
            if (bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].type == 'NODES'):
                hide_assets['sna_show_all_v_park'] = not hide_assets['sna_show_all_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098][bpy.data.collections[Collection].all_objects[i_B7E96].modifiers[i_D4098].node_group.interface.items_tree[Input_name].identifier] = hide_assets['sna_show_all_v_park']
                bpy.data.collections[Collection].all_objects[i_B7E96].update_tag(refresh={'DATA', 'OBJECT'}, )
    return


class SNA_OT_Hide_Park_R_192D6(bpy.types.Operator):
    bl_idname = "sna.hide_park_r_192d6"
    bl_label = "Hide park R"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_E8BEE('ICity_Park', 'All R')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Grass_R_E07D4(bpy.types.Operator):
    bl_idname = "sna.grass_r_e07d4"
    bl_label = "Grass R"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_982E5('ICity_Park', 'Grass R')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Grass_V_4Cdd7(bpy.types.Operator):
    bl_idname = "sna.grass_v_4cdd7"
    bl_label = "Grass V"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_1E48D('ICity_Park', 'Grass V')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Trees_R_164C2(bpy.types.Operator):
    bl_idname = "sna.trees_r_164c2"
    bl_label = "Trees R"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_E138F('ICity_Park', 'Trees R')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Trees_V_25C59(bpy.types.Operator):
    bl_idname = "sna.trees_v_25c59"
    bl_label = "Trees V"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_8DFD5('ICity_Park', 'Trees V')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Hide_Park_3Ea8F(bpy.types.Operator):
    bl_idname = "sna.hide_park_3ea8f"
    bl_label = "Hide park"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_hide_assets_viewport_92CB5_3361F('ICity_Park', 'All V')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_PT_ICITY_754AD(bpy.types.Panel):
    bl_label = 'ICity'
    bl_idname = 'SNA_PT_ICITY_754AD'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'ICity'
    bl_order = 4
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        col_D0E3E = layout.column(heading='', align=True)
        col_D0E3E.alert = False
        col_D0E3E.enabled = True
        col_D0E3E.active = True
        col_D0E3E.use_property_split = True
        col_D0E3E.use_property_decorate = False
        col_D0E3E.scale_x = 1.0
        col_D0E3E.scale_y = 1.7999999523162842
        col_D0E3E.alignment = 'Expand'.upper()
        col_D0E3E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = col_D0E3E.operator('wm.url_open', text='Youtube', icon_value=495, emboss=True, depress=False)
        op.url = 'https://www.youtube.com/@ICity.3d'
        op = col_D0E3E.operator('wm.url_open', text='Discord community', icon_value=231, emboss=True, depress=False)
        op.url = 'https://discord.gg/78AaMyQ6Zm'
        op = col_D0E3E.operator('wm.url_open', text='Report a bug', icon_value=633, emboss=True, depress=False)
        op.url = 'https://discord.gg/AJ92ZW8W4M'
        op = col_D0E3E.operator('wm.url_open', text='Documentation', icon_value=674, emboss=True, depress=False)
        op.url = 'https://icity3d.com/'


def sna_road_materials_browser_enum_items(self, context):
    enum_items = materials_variables['sna_road_materials_filtered_']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_OT_Material_Filter_F04C3(bpy.types.Operator):
    bl_idname = "sna.material_filter_f04c3"
    bl_label = "Material filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        variables['sna_road_materials_browser'] = []
        print('')
        materials_variables['sna_all_materials'] = []
        list_names_0_867ff = sna_generate_icon_list_from_collection_6BD3F_867FF(bpy.data.objects['ICity_Materials'].material_slots)
        print(str(list_names_0_867ff))
        materials_variables['sna_all_materials_enum'] = []
        for i_057BD in range(len(list_names_0_867ff)):
            if (list_names_0_867ff[i_057BD] == ''):
                pass
            else:
                print(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + list_names_0_867ff[i_057BD] + '.png')).replace('\\', '/'))
                materials_variables['sna_all_materials_enum'].append([list_names_0_867ff[i_057BD], list_names_0_867ff[i_057BD], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + 'Custom asset.png').replace('\\', '/'))) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + list_names_0_867ff[i_057BD] + '.png')).replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + list_names_0_867ff[i_057BD] + '.png')).replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + 'Custom asset.png').replace('\\', '/'))) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + list_names_0_867ff[i_057BD] + '.png')).replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.materials[list_names_0_867ff[i_057BD]].sna_asset_category_path_material)) + '\\' + list_names_0_867ff[i_057BD] + '.png')).replace('\\', '/'))))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Road_Materials_Filter_6A3Ec(bpy.types.Operator):
    bl_idname = "sna.road_materials_filter_6a3ec"
    bl_label = "Road materials filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        print(bpy.context.scene.sna_road_materials_type_)
        filtered_0_71e86 = sna_filter_list__4A11C_71E86([bpy.context.scene.sna_road_materials_type_])
        print(str(filtered_0_71e86))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Start_5209E(bpy.types.Operator):
    bl_idname = "sna.start_5209e"
    bl_label = "Start"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        before_data = list(bpy.data.collections)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'ICity start.blend') + r'\Collection', filename='ICity', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.collections)))
        appended_5D310 = None if not new_data else new_data[0]
        bpy.data.collections['ICity Assets'].hide_viewport = True
        bpy.data.collections['ICity Assets'].hide_render = True
        bpy.context.view_layer.objects.active = bpy.data.objects['ICity Base']
        bpy.data.objects['ICity Road'].hide_select = True
        bpy.data.objects['ICity Road Boundry'].hide_select = True
        bpy.data.objects['ICity Spces'].hide_select = True
        bpy.data.objects['ICity Procedural ground'].hide_select = True
        bpy.data.objects['ICity building procedural base'].hide_select = True
        bpy.data.objects['Procedural building_Default_ICity'].hide_select = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text='This might take some time to set up the scene!', icon_value=0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

# 依据不同的城市空间类型（如 Procedural、Park、Presets、Custom），设定不同的活动属性，并将对应的值赋给网格属性。
class SNA_OT_City_Apply_Dae66(bpy.types.Operator):
    bl_idname = "sna.city_apply_dae66"
    bl_label = "City apply"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_5001C('space type')
        print(str((3 if (bpy.context.scene.sna_city_space_type == 'Custom') else (2 if (bpy.context.scene.sna_city_space_type == 'Presets') else (1 if (bpy.context.scene.sna_city_space_type == 'Park') else (0 if (bpy.context.scene.sna_city_space_type == 'Procedural') else None))))))
        bpy.ops.mesh.attribute_set(value_int=(3 if (bpy.context.scene.sna_city_space_type == 'Custom') else (2 if (bpy.context.scene.sna_city_space_type == 'Presets') else (1 if (bpy.context.scene.sna_city_space_type == 'Park') else (0 if (bpy.context.scene.sna_city_space_type == 'Procedural') else None)))))
        if bpy.context.scene.sna_city_space_type == "Procedural":
            sna_set_active_attribute_572EC_A11A7('Procedural index')
            print(str(variables['sna_procedural_building'].index(bpy.context.scene.sna_procedural_building_browser)))
            bpy.ops.mesh.attribute_set(value_int=variables['sna_procedural_building'].index(bpy.context.scene.sna_procedural_building_browser))
            bpy.data.objects[bpy.context.scene.sna_procedural_building_browser].update_tag(refresh={'DATA'}, )
        elif bpy.context.scene.sna_city_space_type == "Park":
            sna_set_active_attribute_572EC_30DFB('Park')
            print(str(variables['sna_park_list'].index(bpy.context.scene.sna_park_browser)), bpy.context.scene.sna_park_browser)
            bpy.ops.mesh.attribute_set(value_int=variables['sna_park_list'].index(bpy.context.scene.sna_park_browser))
        elif bpy.context.scene.sna_city_space_type == "Presets":
            sna_set_active_attribute_572EC_1DA63('Presets')
            print(str(variables['sna_building_presets'].index(bpy.context.scene.sna_building_presets_browser)), bpy.context.scene.sna_building_presets_browser)
            bpy.ops.mesh.attribute_set(value_int=variables['sna_building_presets'].index(bpy.context.scene.sna_building_presets_browser))
            sna_set_active_attribute_572EC_E3814('Landscape')
            bpy.ops.mesh.attribute_set(value_int=variables['sna_landscape_list'].index(bpy.context.scene.sna_landscape_browser))
        else:
            pass
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


@persistent
def depsgraph_update_pre_handler_361D3(dummy):
    if property_exists("bpy.context.view_layer.objects.active.name", globals(), locals()):
        variables['sna_edit_city'] = ((bpy.context.mode == 'EDIT_MESH') and (bpy.context.view_layer.objects.active.name == 'ICity Base'))


# 道路的核心操作
class SNA_OT_Road_Apply_5C3Ab(bpy.types.Operator):
    bl_idname = "sna.road_apply_5c3ab"
    bl_label = "Road apply"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        if ('Texture' == bpy.context.scene.sna_street_asset_type):
            bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_road_materials_type_].inputs[2].default_value = bpy.data.materials[bpy.context.scene.sna_road_materials_browser]
            bpy.data.objects['ICity Road'].update_tag(refresh={'DATA'}, )
        else:
            sna_set_active_attribute_572EC_5FBBE(bpy.context.scene.sna_street_asset_type)
            if 'Light' in bpy.context.scene.sna_street_asset_type:
                bpy.ops.mesh.attribute_set(value_bool=False)
            else:
                bpy.ops.mesh.attribute_set(value_bool=True)
            if bpy.context.scene.sna_street_asset_type == "Cars":
                print('')
            elif bpy.context.scene.sna_street_asset_type == "Sign":
                print('')
            elif bpy.context.scene.sna_street_asset_type == "Texture":
                print('')
            elif bpy.context.scene.sna_street_asset_type == "Imperfection":
                print('')
            elif bpy.context.scene.sna_street_asset_type == "Services":
                bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_street_asset_type].inputs[5].default_value = bpy.data.collections[bpy.context.scene.sna_street_asset_browser]
            else:
                bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_street_asset_type].inputs[4].default_value = bpy.data.objects[bpy.context.scene.sna_street_asset_browser]
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Sync_City_76707(bpy.types.Operator):
    bl_idname = "sna.sync_city_76707"
    bl_label = "sync city"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        for i_D6A85 in range(len(bpy.data.collections['ICity_Procedural'].all_objects)):
            bpy.data.collections['ICity_Procedural'].all_objects[i_D6A85].update_tag(refresh={'DATA'}, )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 设置最小楼层数
class SNA_OT_Floor_Count_Min_C2Cf8(bpy.types.Operator):
    bl_idname = "sna.floor_count_min_c2cf8"
    bl_label = "Floor count min"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_0978B('Floor count')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Floor_Count_Max_Db555(bpy.types.Operator):
    bl_idname = "sna.floor_count_max_db555"
    bl_label = "Floor count max"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_813E4('Floor count max')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Offset_X_A87Eb(bpy.types.Operator):
    bl_idname = "sna.offset_x_a87eb"
    bl_label = "Offset x"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_4CC88('Offset x')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Offset_Y_45B11(bpy.types.Operator):
    bl_idname = "sna.offset_y_45b11"
    bl_label = "Offset y"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_FD2DC('Offset y')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Rotation_Z_4Edcd(bpy.types.Operator):
    bl_idname = "sna.rotation_z_4edcd"
    bl_label = "Rotation z"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_2F07A('Rotation z')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Offset_X_Preset_5A427(bpy.types.Operator):
    bl_idname = "sna.offset_x_preset_5a427"
    bl_label = "Offset x preset"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_92991('Offset x preset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Offset_Y_Preset_Dcad4(bpy.types.Operator):
    bl_idname = "sna.offset_y_preset_dcad4"
    bl_label = "Offset y preset"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_41053('Offset y preset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Rotation_Z_Preset_60648(bpy.types.Operator):
    bl_idname = "sna.rotation_z_preset_60648"
    bl_label = "Rotation z preset"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_0DB67('Rotation z preset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


@persistent
def depsgraph_update_pre_handler_59166(dummy):
    list_0_6a49a = sna_store_atrributes_list_D7786_6A49A()


class SNA_OT_Set_Side_Count_49527(bpy.types.Operator):
    bl_idname = "sna.set_side_count_49527"
    bl_label = "Set side count"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_AE34F('street type')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Assign_Road_Deef9(bpy.types.Operator):
    bl_idname = "sna.assign_road_deef9"
    bl_label = "Assign road"
    bl_description = "Select edge that you want to assign to be road and click"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_BBC9A('Road del')
        bpy.ops.mesh.attribute_set(value_bool=False)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Remove_Road_A2302(bpy.types.Operator):
    bl_idname = "sna.remove_road_a2302"
    bl_label = "Remove road"
    bl_description = "Select edge that you want to not be a road and click"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_7B5C3('Road del')
        bpy.ops.mesh.attribute_set(value_bool=True)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 调整宽度
class SNA_OT_Road_Lanes_Width_93562(bpy.types.Operator):
    bl_idname = "sna.road_lanes_width_93562"
    bl_label = "Road lanes width"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_81051('Road lanes width')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Sidewalk_Width_99Dc0(bpy.types.Operator):
    bl_idname = "sna.sidewalk_width_99dc0"
    bl_label = "Sidewalk width"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_5CC3C('side walk offset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Crosswalk_Offset_B1E82(bpy.types.Operator):
    bl_idname = "sna.crosswalk_offset_b1e82"
    bl_label = "crosswalk offset"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_997D9('crosswalk offset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 将外部场景追加到当前场景
class SNA_OT_Append_Assets_Ffd74(bpy.types.Operator):
    bl_idname = "sna.append_assets_ffd74"
    bl_label = "Append Assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if 'Road' in bpy.context.scene.sna_citystreet_append:
            if 'Texture' in bpy.context.scene.sna_street_asset_type_append:
                print(bpy.context.scene.sna_road_materials_browser_append, '')
                for i_C1098 in range(len(append['sna_road_materials_filtered'])):
                    if append['sna_road_materials_filtered'][i_C1098][0] in bpy.context.scene.sna_road_materials_browser_append:
                        before_data = list(bpy.data.materials)
                        bpy.ops.wm.append(directory=append['sna_road_materials_filtered'][i_C1098][2] + r'\Material', filename=append['sna_road_materials_filtered'][i_C1098][0], link=False)
                        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.materials)))
                        appended_0F2E8 = None if not new_data else new_data[0]
                        if property_exists("appended_0F2E8", globals(), locals()):
                            appended_0F2E8.sna_asset_category_path_material = append['sna_road_materials_filtered'][i_C1098][2]
                            bpy.data.objects['ICity_Materials'].data.materials.append(material=appended_0F2E8, )
            else:
                if ('Services' in bpy.context.scene.sna_street_asset_type_append or 'Imperfection' in bpy.context.scene.sna_street_asset_type_append):
                    print('')
                    for i_3A396 in range(len(append['sna_road_assets_filtered'])):
                        if bpy.context.scene.sna_street_asset_type_append in append['sna_road_assets_filtered'][i_3A396][0]:
                            print(append['sna_road_assets_filtered'][i_3A396][2], append['sna_road_assets_filtered'][i_3A396][0])
                            before_data = list(bpy.data.collections)
                            bpy.ops.wm.append(directory=append['sna_road_assets_filtered'][i_3A396][2] + r'\Collection', filename=append['sna_road_assets_filtered'][i_3A396][0], link=False)
                            new_data = list(filter(lambda d: not d in before_data, list(bpy.data.collections)))
                            appended_BBE11 = None if not new_data else new_data[0]
                            if property_exists("bpy.data.collections[append['sna_road_assets_filtered'][i_3A396][0]]", globals(), locals()):
                                bpy.data.collections[append['sna_road_assets_filtered'][i_3A396][0]].sna_asset_category_path_collection = append['sna_road_assets_filtered'][i_3A396][2]
                                print(append['sna_road_assets_filtered'][i_3A396][0], ('ICity_Services' if 'Services' in append['sna_road_assets_filtered'][i_3A396][0] else 'ICity_Imperfection'))
                                sna_move_to_collection_A3C17_7B15A(False, bpy.data.collections[append['sna_road_assets_filtered'][i_3A396][0]], None, bpy.data.collections[('ICity_Services' if 'Services' in append['sna_road_assets_filtered'][i_3A396][0] else 'ICity_Imperfection')])
                else:
                    print(bpy.context.scene.sna_road_browser_append, '')
                    for i_51FAF in range(len(append['sna_road_assets_filtered'])):
                        if append['sna_road_assets_filtered'][i_51FAF][0] in bpy.context.scene.sna_road_browser_append:
                            before_data = list(bpy.data.objects)
                            bpy.ops.wm.append(directory=append['sna_road_assets_filtered'][i_51FAF][2] + r'\Object', filename=append['sna_road_assets_filtered'][i_51FAF][0], link=False)
                            new_data = list(filter(lambda d: not d in before_data, list(bpy.data.objects)))
                            appended_F0624 = None if not new_data else new_data[0]
                            if property_exists("appended_F0624", globals(), locals()):
                                appended_F0624.sna_asset_category_path_object = append['sna_road_assets_filtered'][i_51FAF][2]
                                sna_move_to_collection_A3C17_97000(True, appended_F0624, None, bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type_append])
        else:
            if 'Procedural' in bpy.context.scene.sna_city_space_type_append:
                for i_F2E6F in range(len(append['sna_city_assets_filtered'])):
                    if append['sna_city_assets_filtered'][i_F2E6F][0] in bpy.context.scene.sna_city_browser_append:
                        before_data = list(bpy.data.collections)
                        bpy.ops.wm.append(directory=append['sna_city_assets_filtered'][i_F2E6F][2] + r'\Collection', filename=append['sna_city_assets_filtered'][i_F2E6F][0], link=False)
                        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.collections)))
                        appended_CBAC9 = None if not new_data else new_data[0]
                        if property_exists("appended_CBAC9", globals(), locals()):
                            appended_CBAC9.sna_asset_category_path_collection = append['sna_city_assets_filtered'][i_F2E6F][2]
                            sna_move_to_collection_A3C17_D6B3F(False, bpy.data.collections[bpy.context.scene.sna_city_browser_append], None, bpy.data.collections['ICity Assets'])
                            for i_05E8B in range(len(bpy.data.collections[bpy.context.scene.sna_city_browser_append + ' Objects'].all_objects)):
                                bpy.data.collections['ICity_Procedural'].objects.link(object=bpy.data.collections[bpy.context.scene.sna_city_browser_append + ' Objects'].all_objects[i_05E8B], )
                                if property_exists("bpy.data.collections[bpy.context.scene.sna_city_browser_append + ' Objects'].all_objects[i_05E8B]", globals(), locals()):
                                    bpy.data.collections[bpy.context.scene.sna_city_browser_append + ' Objects'].all_objects[i_05E8B].sna_asset_category_path_object = append['sna_city_assets_filtered'][i_F2E6F][2]
            else:
                for i_AF454 in range(len(append['sna_city_assets_filtered'])):
                    if append['sna_city_assets_filtered'][i_AF454][0] in bpy.context.scene.sna_city_browser_append:
                        before_data = list(bpy.data.objects)
                        bpy.ops.wm.append(directory=append['sna_city_assets_filtered'][i_AF454][2] + r'\Object', filename=append['sna_city_assets_filtered'][i_AF454][0], link=False)
                        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.objects)))
                        appended_770CC = None if not new_data else new_data[0]
                        if property_exists("appended_770CC", globals(), locals()):
                            appended_770CC.sna_asset_category_path_object = append['sna_city_assets_filtered'][i_AF454][2]
                            sna_move_to_collection_A3C17_D47A1(True, appended_770CC, None, bpy.data.collections['ICity_' + bpy.context.scene.sna_city_space_type_append])
            bpy.context.scene.sna_city_space_type = bpy.context.scene.sna_city_space_type
            bpy.data.collections['ICity Assets'].hide_viewport = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 添加资产到场景
class SNA_OT_Append_Landscape_C97Bb(bpy.types.Operator):
    bl_idname = "sna.append_landscape_c97bb"
    bl_label = "Append landscape"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        for i_9DA95 in range(len(append['sna_landscape_filtered'])):
            if append['sna_landscape_filtered'][i_9DA95][0] in bpy.context.scene.sna_landscape_browser_append:
                before_data = list(bpy.data.objects)
                bpy.ops.wm.append(directory=append['sna_landscape_filtered'][i_9DA95][2] + r'\Object', filename=append['sna_landscape_filtered'][i_9DA95][0], link=False)
                new_data = list(filter(lambda d: not d in before_data, list(bpy.data.objects)))
                appended_5A06C = None if not new_data else new_data[0]
                if property_exists("appended_5A06C", globals(), locals()):
                    appended_5A06C.sna_asset_category_path_object = append['sna_landscape_filtered'][i_9DA95][2]
                    sna_move_to_collection_A3C17_575C9(True, appended_5A06C, None, bpy.data.collections['ICity_Landscape'])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Intersection_Offset_16E01(bpy.types.Operator):
    bl_idname = "sna.intersection_offset_16e01"
    bl_label = "Intersection Offset"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You have to be in Edit city mode!')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        sna_set_active_attribute_572EC_62FA0('offset')
        bpy.ops.mesh.attribute_set('INVOKE_DEFAULT', )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Edit_City_D7Cab(bpy.types.Operator):
    bl_idname = "sna.edit_city_d7cab"
    bl_label = "Edit city"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.context.view_layer.objects.active = bpy.data.objects['ICity Base']
        if (bpy.context.mode == 'EDIT_MESH'):
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            bpy.ops.object.select_all('INVOKE_DEFAULT', action='DESELECT')
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.sna.light_city_20ca9()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Delete_From_Scene_City_324Ff(bpy.types.Operator):
    bl_idname = "sna.delete_from_scene_city_324ff"
    bl_label = "Delete from scene city"
    bl_description = "Delete from scene."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('You cant remove this!')
        return not 'Procedural' in bpy.context.scene.sna_city_space_type

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.collections['ICity Assets'].hide_viewport = False
        bpy.data.objects[(bpy.context.scene.sna_building_presets_browser if 'Presets' in bpy.context.scene.sna_city_space_type else (bpy.context.scene.sna_park_browser if 'Park' in bpy.context.scene.sna_city_space_type else None))].select_set(state=True, )
        bpy.ops.object.delete(confirm=True)
        bpy.context.scene.sna_city_space_type = bpy.context.scene.sna_city_space_type
        bpy.data.collections['ICity Assets'].hide_viewport = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 开灯
class SNA_OT_Light_City_20Ca9(bpy.types.Operator):
    bl_idname = "sna.light_city_20ca9"
    bl_label = "Light city"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.data.node_groups['Light mode'].nodes['Boolean Math.003'].inputs[0].default_value = (variables['sna_edit_city'] and bpy.context.scene.sna_light_mode)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Delete_From_Scene_7C7D8(bpy.types.Operator):
    bl_idname = "sna.delete_from_scene_7c7d8"
    bl_label = "Delete from scene"
    bl_description = "Delete from scene road assets."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not variables['sna_edit_city']

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.collections['ICity Assets'].hide_viewport = False
        if 'Texture' in bpy.context.scene.sna_street_asset_type:
            if property_exists("bpy.data.materials[bpy.context.scene.sna_road_materials_browser]", globals(), locals()):
                bpy.data.materials.remove(material=bpy.data.materials[bpy.context.scene.sna_road_materials_browser], )
        else:
            if ('Imperfection' in bpy.context.scene.sna_street_asset_type or 'Services' in bpy.context.scene.sna_street_asset_type):
                bpy.data.collections.remove(collection=bpy.data.collections[bpy.context.scene.sna_street_asset_browser], )
            else:
                bpy.data.objects[bpy.context.scene.sna_street_asset_browser].select_set(state=True, )
                bpy.ops.object.delete(confirm=True)
        bpy.context.scene.sna_street_asset_type = bpy.context.scene.sna_street_asset_type
        bpy.data.collections['ICity Assets'].hide_viewport = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Road_Remove_Aa51D(bpy.types.Operator):
    bl_idname = "sna.road_remove_aa51d"
    bl_label = "Road Remove"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not (not variables['sna_edit_city'])

    def execute(self, context):
        if ('Texture' == bpy.context.scene.sna_street_asset_type):
            pass
        else:
            sna_set_active_attribute_572EC_42E3D(bpy.context.scene.sna_street_asset_type)
            if 'Light' in bpy.context.scene.sna_street_asset_type:
                bpy.ops.mesh.attribute_set(value_bool=True)
            else:
                bpy.ops.mesh.attribute_set(value_bool=False)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_AddonPreferences_7CCE1(bpy.types.AddonPreferences):
    bl_idname = 'icity'
    sna_assets_path: bpy.props.StringProperty(name='Assets path', description='', default='', subtype='DIR_PATH', maxlen=0)

    def draw(self, context):
        if not (False):
            layout = self.layout 
            box_A083F = layout.box()
            box_A083F.alert = False
            box_A083F.enabled = True
            box_A083F.active = True
            box_A083F.use_property_split = False
            box_A083F.use_property_decorate = False
            box_A083F.alignment = 'Expand'.upper()
            box_A083F.scale_x = 1.0
            box_A083F.scale_y = 1.0
            if not True: box_A083F.operator_context = "EXEC_DEFAULT"
            col_D81F8 = box_A083F.column(heading='', align=False)
            col_D81F8.alert = False
            col_D81F8.enabled = True
            col_D81F8.active = True
            col_D81F8.use_property_split = False
            col_D81F8.use_property_decorate = False
            col_D81F8.scale_x = 1.0
            col_D81F8.scale_y = 1.7200000286102295
            col_D81F8.alignment = 'Expand'.upper()
            col_D81F8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            col_D81F8.prop(bpy.context.preferences.addons['icity'].preferences, 'sna_assets_path', text='Assets path', icon_value=0, emboss=True)
            op = col_D81F8.operator('sna.refresh_c6cb8', text='Read files', icon_value=0, emboss=True, depress=False)
            col_D81F8.label(text=('No assets found!' if ((None == append['sna_all_assets']) or (None == append['sna_all_materials'])) else 'Assets found' + '(' + str(int(len(append['sna_all_assets']) + len(append['sna_all_materials']))) + ')'), icon_value=0)


def sna_remove_last_path_5D152(String):
    return String.replace('\\' + String.split('\\')[int(len(String.split('\\')) - 1.0)], '')


def sna_move_to_collection_A3C17(Object_collection, Item, From__default_active_collection, To):
    if Object_collection:
        if (property_exists("To.objects", globals(), locals()) and Item.name in To.objects):
            pass
        else:
            To.objects.link(object=bpy.data.objects[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).objects.unlink(object=bpy.data.objects[Item.name], )
    else:
        To.children.link(child=bpy.data.collections[Item.name], )
        (bpy.context.view_layer.active_layer_collection.collection if (From__default_active_collection == None) else From__default_active_collection).children.unlink(child=bpy.data.collections[Item.name], )
    return


class SNA_OT_Test_Assets_B9626(bpy.types.Operator):
    bl_idname = "sna.test_assets_b9626"
    bl_label = "test assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        print(os.path.join('','assets'))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_street_assets_lists_1588D():
    variables['sna_street_asset_browser'] = []
    for i_97E63 in range(len((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects))):
        if ('Signs' if (bpy.context.scene.sna_street_asset_type_append == 'Signs') else ('Tree base' if (bpy.context.scene.sna_street_asset_type_append == 'Tree base') else ('Services' if (bpy.context.scene.sna_street_asset_type_append == 'Services') else ('Trees' if (bpy.context.scene.sna_street_asset_type_append == 'Trees') else ('Bench' if (bpy.context.scene.sna_street_asset_type_append == 'Bench') else ('Lights' if (bpy.context.scene.sna_street_asset_type_append == 'Lights') else None)))))) in ((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else (bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name):
            variables['sna_street_asset_browser'].append([((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else (bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name), ((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else (bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name), '', load_preview_icon((os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + ((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else (bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name) + '.png' if 'ICity' in ((bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else (bpy.data.collections if ('Trees' in bpy.context.scene.sna_street_asset_type_append or 'Services' in bpy.context.scene.sna_street_asset_type_append) else bpy.data.objects)[i_97E63].name) else os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + 'Custom asset' + '.png'))])
    return


def sna_sidewalk_mat_C9E1B():
    variables['sna_sidewalk_mat'] = []
    for i_22F91 in range(len(bpy.data.materials)):
        if 'Sidewalk' in bpy.data.materials[i_22F91].name:
            variables['sna_sidewalk_mat'].append([bpy.data.materials[i_22F91].name, bpy.data.materials[i_22F91].name, '', load_preview_icon((os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + bpy.data.materials[i_22F91].name + '.png' if 'Sidewalk' in bpy.data.materials[i_22F91].name else os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + 'Custom asset' + '.png'))])
            print(str([bpy.data.materials[i_22F91].name, bpy.data.materials[i_22F91].name, '', load_preview_icon((os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + bpy.data.materials[i_22F91].name + '.png' if 'Sidewalk' in bpy.data.materials[i_22F91].name else os.path.join(os.path.dirname(__file__), 'assets', 'icons') + '//' + 'Custom asset' + '.png'))]))
            return


def sna_sidewalk_mat_enum_items(self, context):
    enum_items = variables['sna_sidewalk_mat']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_OT_Refresh_Edit_F156A(bpy.types.Operator):
    bl_idname = "sna.refresh_edit_f156a"
    bl_label = "Refresh edit"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_building_presets_browser_enum_items(self, context):
    enum_items = variables['sna_building_presets_browser']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_park_browser_enum_items(self, context):
    enum_items = variables['sna_park_browser']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_procedural_building_browser_enum_items(self, context):
    enum_items = variables['sna_procedural_building_browser']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_street_asset_browser_enum_items(self, context):
    enum_items = variables['sna_street_asset_browser']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_landscape_browser_enum_items(self, context):
    enum_items = variables['sna_landscape_browser']
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class SNA_OT_Filter_Presets_Fb5A4(bpy.types.Operator):
    bl_idname = "sna.filter_presets_fb5a4"
    bl_label = "Filter Presets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        print('')
        variables['sna_building_presets'] = []
        for i_082B6 in range(len(bpy.data.collections[('ICity_Presets' if 'All' in '' else 'ICity_Presets')].all_objects)):
            variables['sna_building_presets'].append(bpy.data.collections[('ICity_Presets' if 'All' in '' else 'ICity_Presets')].all_objects[i_082B6].name)
        variables['sna_building_presets_browser'] = []
        for i_83ED4 in range(len(variables['sna_building_presets'])):
            print('')
            variables['sna_building_presets_browser'].append([variables['sna_building_presets'][i_83ED4], variables['sna_building_presets'][i_83ED4], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + variables['sna_building_presets'][i_83ED4] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + variables['sna_building_presets'][i_83ED4] + '.png').replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + variables['sna_building_presets'][i_83ED4] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[variables['sna_building_presets'][i_83ED4]].sna_asset_category_path_object)) + '\\' + variables['sna_building_presets'][i_83ED4] + '.png').replace('\\', '/'))))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Procedural_Building_Filter_05Bed(bpy.types.Operator):
    bl_idname = "sna.procedural_building_filter_05bed"
    bl_label = "Procedural building filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        list_names_0_eac41 = sna_generate_icon_list_from_collection_6BD3F_EAC41(bpy.data.collections['ICity_Procedural'].all_objects)
        print(str(list_names_0_eac41))
        variables['sna_procedural_building_browser'] = []
        for i_3BAC1 in range(len(list_names_0_eac41)):
            print(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + list_names_0_eac41[i_3BAC1] + '.png').replace('\\', '/'))
            bpy.data.objects[list_names_0_eac41[i_3BAC1]].modifiers[0]['Socket_0'] = i_3BAC1
            bpy.data.objects[list_names_0_eac41[i_3BAC1]].modifiers[0]['Socket_1'] = bpy.data.objects['ICity building procedural base']
            bpy.data.objects[list_names_0_eac41[i_3BAC1]].update_tag(refresh={'DATA'}, )
            variables['sna_procedural_building_browser'].append([list_names_0_eac41[i_3BAC1], list_names_0_eac41[i_3BAC1], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + list_names_0_eac41[i_3BAC1] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + list_names_0_eac41[i_3BAC1] + '.png').replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + list_names_0_eac41[i_3BAC1] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_eac41[i_3BAC1]].sna_asset_category_path_object)) + '\\' + list_names_0_eac41[i_3BAC1] + '.png').replace('\\', '/'))))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Park_Filter_5A7A2(bpy.types.Operator):
    bl_idname = "sna.park_filter_5a7a2"
    bl_label = "Park filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        list_names_0_b83d7 = sna_generate_icon_list_from_collection_6BD3F_B83D7(bpy.data.collections['ICity_Park'].all_objects)
        print(str(list_names_0_b83d7))
        variables['sna_park_browser'] = []
        for i_5519B in range(len(list_names_0_b83d7)):
            print(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + list_names_0_b83d7[i_5519B] + '.png').replace('\\', '/'))
            variables['sna_park_browser'].append([list_names_0_b83d7[i_5519B], list_names_0_b83d7[i_5519B], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + list_names_0_b83d7[i_5519B] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + list_names_0_b83d7[i_5519B] + '.png').replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + list_names_0_b83d7[i_5519B] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_b83d7[i_5519B]].sna_asset_category_path_object)) + '\\' + list_names_0_b83d7[i_5519B] + '.png').replace('\\', '/'))))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Landscape_Filter_0Bf89(bpy.types.Operator):
    bl_idname = "sna.landscape_filter_0bf89"
    bl_label = "Landscape filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        list_names_0_bbaa3 = sna_generate_icon_list_from_collection_6BD3F_BBAA3(bpy.data.collections['ICity_Landscape'].all_objects)
        print(str(list_names_0_bbaa3))
        variables['sna_landscape_browser'] = []
        for i_C2F17 in range(len(list_names_0_bbaa3)):
            print('')
            variables['sna_landscape_browser'].append([list_names_0_bbaa3[i_C2F17], list_names_0_bbaa3[i_C2F17], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + list_names_0_bbaa3[i_C2F17] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + list_names_0_bbaa3[i_C2F17] + '.png').replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + list_names_0_bbaa3[i_C2F17] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_bbaa3[i_C2F17]].sna_asset_category_path_object)) + '\\' + list_names_0_bbaa3[i_C2F17] + '.png').replace('\\', '/'))))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Filter_Street_Assets_C5C0E(bpy.types.Operator):
    bl_idname = "sna.filter_street_assets_c5c0e"
    bl_label = "Filter street assets"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if ('Services' in bpy.context.scene.sna_street_asset_type or 'Imperfection' in bpy.context.scene.sna_street_asset_type):
            if (property_exists("bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].children", globals(), locals()) and (len(bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].children) > 0)):
                list_names_0_edbef = sna_generate_icon_list_from_collection_6BD3F_EDBEF(bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].children)
                variables['sna_street_asset_browser'] = []
                for i_2FB8C in range(len(list_names_0_edbef)):
                    variables['sna_street_asset_browser'].append([list_names_0_edbef[i_2FB8C], list_names_0_edbef[i_2FB8C], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + list_names_0_edbef[i_2FB8C] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + list_names_0_edbef[i_2FB8C] + '.png').replace('\\', '/')))) else (load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + 'Custom asset.png').replace('\\', '/')) if (load_preview_icon(r'') == load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + list_names_0_edbef[i_2FB8C] + '.png').replace('\\', '/'))) else load_preview_icon(bpy.path.abspath(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.collections[list_names_0_edbef[i_2FB8C]].sna_asset_category_path_collection)) + '\\' + list_names_0_edbef[i_2FB8C] + '.png').replace('\\', '/'))))])
        else:
            if (property_exists("bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].all_objects", globals(), locals()) and (len(bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].all_objects) > 0)):
                list_names_0_593da = sna_generate_icon_list_from_collection_6BD3F_593DA(bpy.data.collections['ICity_' + bpy.context.scene.sna_street_asset_type].all_objects)
                variables['sna_street_asset_browser'] = []
                for i_EA4BD in range(len(list_names_0_593da)):
                    variables['sna_street_asset_browser'].append([list_names_0_593da[i_EA4BD], list_names_0_593da[i_EA4BD], '', (load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', '16e8992ffebf47daba61aa6815a7177b (1).png')) if (load_preview_icon(r'') == (load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png') if (load_preview_icon(r'') == load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + list_names_0_593da[i_EA4BD] + '.png')) else load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + list_names_0_593da[i_EA4BD] + '.png'))) else (load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + 'Custom asset.png') if (load_preview_icon(r'') == load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + list_names_0_593da[i_EA4BD] + '.png')) else load_preview_icon(os.path.dirname(sna_replace_to_addon_path_4DC0E(bpy.data.objects[list_names_0_593da[i_EA4BD]].sna_asset_category_path_object)) + '\\' + list_names_0_593da[i_EA4BD] + '.png')))])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# 路径转换
def sna_replace_to_addon_path_4DC0E(path):
    return bpy.path.abspath(path).replace('G:\\My Drive\\Building\\Assets', bpy.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))).replace('C:\\Users\\hothifa\\AppData\\Roaming\\Blender Foundation\\Blender\\4.1\\scripts\\addons\\icity\\assets\\Assets', bpy.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'Assets'))).replace('\\', '/')


def sna_is_collection_not_empty_B0A78(Collection_name):
    return (len(bpy.data.collections[Collection_name].all_objects) != 0)


class SNA_PT_ICITY_EDITOR_6D34D(bpy.types.Panel):
    bl_label = 'ICity editor'
    bl_idname = 'SNA_PT_ICITY_EDITOR_6D34D'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'ICity'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        box_7C4E0 = layout.box()
        box_7C4E0.alert = False
        box_7C4E0.enabled = True
        box_7C4E0.active = True
        box_7C4E0.use_property_split = False
        box_7C4E0.use_property_decorate = False
        box_7C4E0.alignment = 'Expand'.upper()
        box_7C4E0.scale_x = 1.0
        box_7C4E0.scale_y = 1.0
        if not True: box_7C4E0.operator_context = "EXEC_DEFAULT"
        row_C774B = box_7C4E0.row(heading='', align=True)
        row_C774B.alert = False
        row_C774B.enabled = True
        row_C774B.active = True
        row_C774B.use_property_split = False
        row_C774B.use_property_decorate = False
        row_C774B.scale_x = 1.0
        row_C774B.scale_y = 1.0
        row_C774B.alignment = 'Center'.upper()
        row_C774B.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
        row_C774B.template_icon(icon_value=load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'New Project (26).png')), scale=(6 if property_exists("bpy.data.collections['ICity']", globals(), locals()) else 6))
        if property_exists("bpy.data.collections['ICity']", globals(), locals()):
            pass
        else:
            col_28D9D = box_7C4E0.column(heading='', align=False)
            col_28D9D.alert = False
            col_28D9D.enabled = True
            col_28D9D.active = True
            col_28D9D.use_property_split = False
            col_28D9D.use_property_decorate = False
            col_28D9D.scale_x = 1.0
            col_28D9D.scale_y = 1.0
            col_28D9D.alignment = 'Expand'.upper()
            col_28D9D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_6BBDC = col_28D9D.box()
            box_6BBDC.alert = False
            box_6BBDC.enabled = True
            box_6BBDC.active = True
            box_6BBDC.use_property_split = False
            box_6BBDC.use_property_decorate = False
            box_6BBDC.alignment = 'Expand'.upper()
            box_6BBDC.scale_x = 2.559999942779541
            box_6BBDC.scale_y = 2.259999990463257
            if not True: box_6BBDC.operator_context = "EXEC_DEFAULT"
            op = box_6BBDC.operator('sna.start_5209e', text='Start', icon_value=0, emboss=False, depress=False)
        if property_exists("bpy.data.collections['ICity']", globals(), locals()):
            box_27D05 = box_7C4E0.box()
            box_27D05.alert = False
            box_27D05.enabled = True
            box_27D05.active = True
            box_27D05.use_property_split = False
            box_27D05.use_property_decorate = False
            box_27D05.alignment = 'Expand'.upper()
            box_27D05.scale_x = 1.0
            box_27D05.scale_y = 1.0
            if not True: box_27D05.operator_context = "EXEC_DEFAULT"
            col_C76CC = box_27D05.column(heading='', align=True)
            col_C76CC.alert = False
            col_C76CC.enabled = True
            col_C76CC.active = True
            col_C76CC.use_property_split = False
            col_C76CC.use_property_decorate = False
            col_C76CC.scale_x = 1.0
            col_C76CC.scale_y = 1.100000023841858
            col_C76CC.alignment = 'Expand'.upper()
            col_C76CC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            col_C4407 = col_C76CC.column(heading='', align=True)
            col_C4407.alert = False
            col_C4407.enabled = True
            col_C4407.active = True
            col_C4407.use_property_split = False
            col_C4407.use_property_decorate = False
            col_C4407.scale_x = 1.0
            col_C4407.scale_y = 2.0
            col_C4407.alignment = 'Expand'.upper()
            col_C4407.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = col_C4407.operator('sna.edit_city_d7cab', text='Edit city', icon_value=0, emboss=True, depress=variables['sna_edit_city'])
            col_C76CC.prop(bpy.context.scene, 'sna_proxy_mode', text='Proxy mode', icon_value=0, emboss=True, toggle=True)
            if variables['sna_edit_city']:
                box_27D05.label(text=('Road attributes are stored on edges!' if 'Road' in bpy.context.scene.sna_citystreet else ('City attributes are stored on faces!' if 'City' in bpy.context.scene.sna_citystreet else None)), icon_value=110)
            else:
                box_27D05.separator(factor=0.5)
            col_84076 = box_27D05.column(heading='', align=False)
            col_84076.alert = False
            col_84076.enabled = True
            col_84076.active = True
            col_84076.use_property_split = False
            col_84076.use_property_decorate = False
            col_84076.scale_x = 1.0
            col_84076.scale_y = 1.0
            col_84076.alignment = 'Expand'.upper()
            col_84076.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_626E8 = col_84076.row(heading='', align=False)
            row_626E8.alert = False
            row_626E8.enabled = True
            row_626E8.active = True
            row_626E8.use_property_split = False
            row_626E8.use_property_decorate = False
            row_626E8.scale_x = 1.0
            row_626E8.scale_y = 2.2810001373291016
            row_626E8.alignment = 'Expand'.upper()
            row_626E8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_626E8.prop(bpy.context.scene, 'sna_citystreet', text=bpy.context.scene.sna_citystreet, icon_value=0, emboss=True, expand=True)
            # 主体操作部分 Road和City
            if bpy.context.scene.sna_citystreet == "Road":
                col_84076.separator(factor=1.0)
                box_22FAC = col_84076.box()
                box_22FAC.alert = False
                box_22FAC.enabled = True
                box_22FAC.active = True
                box_22FAC.use_property_split = False
                box_22FAC.use_property_decorate = False
                box_22FAC.alignment = 'Expand'.upper()
                box_22FAC.scale_x = 1.0
                box_22FAC.scale_y = 1.0
                if not True: box_22FAC.operator_context = "EXEC_DEFAULT"
                col_80A9F = box_22FAC.column(heading='', align=False)
                col_80A9F.alert = False
                col_80A9F.enabled = True
                col_80A9F.active = True
                col_80A9F.use_property_split = False
                col_80A9F.use_property_decorate = False
                col_80A9F.scale_x = 1.0
                col_80A9F.scale_y = 1.0
                col_80A9F.alignment = 'Expand'.upper()
                col_80A9F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_5DF5F = col_80A9F.row(heading='', align=False)
                row_5DF5F.alert = False
                row_5DF5F.enabled = True
                row_5DF5F.active = True
                row_5DF5F.use_property_split = False
                row_5DF5F.use_property_decorate = False
                row_5DF5F.scale_x = 1.3480000495910645
                row_5DF5F.scale_y = 1.5999999046325684
                row_5DF5F.alignment = 'Expand'.upper()
                row_5DF5F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_5DF5F.prop(bpy.context.scene, 'sna_street_assetoptions', text=bpy.context.scene.sna_street_assetoptions, icon_value=0, emboss=True, expand=True)
                if bpy.context.scene.sna_street_assetoptions == "Assets":
                    col_2F17C = col_80A9F.column(heading='', align=False)
                    col_2F17C.alert = False
                    col_2F17C.enabled = True
                    col_2F17C.active = True
                    col_2F17C.use_property_split = False
                    col_2F17C.use_property_decorate = False
                    col_2F17C.scale_x = 1.0
                    col_2F17C.scale_y = 1.0
                    col_2F17C.alignment = 'Expand'.upper()
                    col_2F17C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    col_2F17C.separator(factor=1.0)
                    box_D0F78 = col_2F17C.box()
                    box_D0F78.alert = False
                    box_D0F78.enabled = True
                    box_D0F78.active = True
                    box_D0F78.use_property_split = False
                    box_D0F78.use_property_decorate = False
                    box_D0F78.alignment = 'Expand'.upper()
                    box_D0F78.scale_x = 1.0
                    box_D0F78.scale_y = 1.0
                    if not True: box_D0F78.operator_context = "EXEC_DEFAULT"
                    row_9ABA8 = box_D0F78.row(heading='', align=True)
                    row_9ABA8.alert = False
                    row_9ABA8.enabled = True
                    row_9ABA8.active = True
                    row_9ABA8.use_property_split = False
                    row_9ABA8.use_property_decorate = False
                    row_9ABA8.scale_x = 1.0
                    row_9ABA8.scale_y = 1.0
                    row_9ABA8.alignment = 'Expand'.upper()
                    row_9ABA8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    attr_30A53 = '["' + str(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'].node_group.interface.items_tree['All V'].identifier + '"]') 
                    row_9ABA8.prop(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'], attr_30A53, text='Show viewport all', icon_value=284, emboss=True)
                    attr_F2CEA = '["' + str(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'].node_group.interface.items_tree['All R'].identifier + '"]') 
                    row_9ABA8.prop(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'], attr_F2CEA, text='Show render all', icon_value=258, emboss=True)
                    col_2F17C.separator(factor=1.0)
                    grid_7EDA5 = col_2F17C.grid_flow(columns=2, row_major=True, even_columns=False, even_rows=False, align=True)
                    grid_7EDA5.enabled = True
                    grid_7EDA5.active = True
                    grid_7EDA5.use_property_split = False
                    grid_7EDA5.use_property_decorate = False
                    grid_7EDA5.alignment = 'Expand'.upper()
                    grid_7EDA5.scale_x = 1.0
                    grid_7EDA5.scale_y = 1.0
                    if not True: grid_7EDA5.operator_context = "EXEC_DEFAULT"
                    grid_7EDA5.prop(bpy.context.scene, 'sna_street_asset_type', text='Side count', icon_value=0, emboss=True, expand=True)
                    if bpy.context.scene.sna_street_asset_type == "Cars":
                        box_02964 = col_2F17C.box()
                        box_02964.alert = False
                        box_02964.enabled = True
                        box_02964.active = True
                        box_02964.use_property_split = False
                        box_02964.use_property_decorate = False
                        box_02964.alignment = 'Expand'.upper()
                        box_02964.scale_x = 1.0
                        box_02964.scale_y = 2.0
                        if not True: box_02964.operator_context = "EXEC_DEFAULT"
                        box_02964.label(text='Coming soon!', icon_value=16)
                    elif bpy.context.scene.sna_street_asset_type == "Texture":
                        col_2F17C.prop(bpy.context.scene, 'sna_road_materials_type_', text='Type', icon_value=0, emboss=True)
                        col_2F17C.template_icon_view(bpy.context.scene, 'sna_road_materials_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                        col_928D8 = col_2F17C.column(heading='', align=False)
                        col_928D8.alert = False
                        col_928D8.enabled = True
                        col_928D8.active = True
                        col_928D8.use_property_split = False
                        col_928D8.use_property_decorate = False
                        col_928D8.scale_x = 1.0
                        col_928D8.scale_y = 1.2999999523162842
                        col_928D8.alignment = 'Expand'.upper()
                        col_928D8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        row_C1856 = col_928D8.row(heading='', align=True)
                        row_C1856.alert = False
                        row_C1856.enabled = True
                        row_C1856.active = True
                        row_C1856.use_property_split = False
                        row_C1856.use_property_decorate = False
                        row_C1856.scale_x = 1.0
                        row_C1856.scale_y = 2.200000047683716
                        row_C1856.alignment = 'Expand'.upper()
                        row_C1856.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
                        op = row_C1856.operator('sna.road_apply_5c3ab', text='Assign', icon_value=0, emboss=True, depress=False)
                    elif bpy.context.scene.sna_street_asset_type == "Sign":
                        col_D805D = col_2F17C.column(heading='', align=False)
                        col_D805D.alert = False
                        col_D805D.enabled = True
                        col_D805D.active = True
                        col_D805D.use_property_split = False
                        col_D805D.use_property_decorate = False
                        col_D805D.scale_x = 1.0
                        col_D805D.scale_y = 1.0
                        col_D805D.alignment = 'Expand'.upper()
                        col_D805D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        col_D805D.separator(factor=1.5)
                        row_5F764 = col_D805D.row(heading='', align=True)
                        row_5F764.alert = False
                        row_5F764.enabled = True
                        row_5F764.active = True
                        row_5F764.use_property_split = False
                        row_5F764.use_property_decorate = False
                        row_5F764.scale_x = 1.0
                        row_5F764.scale_y = 2.2150001525878906
                        row_5F764.alignment = 'Expand'.upper()
                        row_5F764.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
                        op = row_5F764.operator('sna.road_apply_5c3ab', text='Assign', icon_value=0, emboss=True, depress=False)
                        op = row_5F764.operator('mesh.attribute_set', text='remove', icon_value=0, emboss=True, depress=False)
                        op.value_bool = False
                        col_D6697 = col_D805D.column(heading='', align=True)
                        col_D6697.alert = False
                        col_D6697.enabled = True
                        col_D6697.active = True
                        col_D6697.use_property_split = False
                        col_D6697.use_property_decorate = False
                        col_D6697.scale_x = 1.0
                        col_D6697.scale_y = 2.0
                        col_D6697.alignment = 'Expand'.upper()
                        col_D6697.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        col_D6697.prop(bpy.data.node_groups['Road 2'].nodes['Sign'].inputs[10], 'default_value', text='Spacing', icon_value=0, emboss=True)
                        col_D6697.prop(bpy.data.node_groups['Road 2'].nodes['Sign'].inputs[11], 'default_value', text='Path offset', icon_value=0, emboss=True)
                        col_D6697.prop(bpy.data.node_groups['Road 2'].nodes['Sign'].inputs[12], 'default_value', text='Depth offset', icon_value=0, emboss=True)
                    elif bpy.context.scene.sna_street_asset_type == "Traffic light":
                        col_2F17C.separator(factor=1.5)
                    else:
                        col_FE7BC = col_2F17C.column(heading='', align=False)
                        col_FE7BC.alert = False
                        col_FE7BC.enabled = True
                        col_FE7BC.active = True
                        col_FE7BC.use_property_split = False
                        col_FE7BC.use_property_decorate = False
                        col_FE7BC.scale_x = 1.0
                        col_FE7BC.scale_y = 1.2999999523162842
                        col_FE7BC.alignment = 'Expand'.upper()
                        col_FE7BC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        box_FA482 = col_FE7BC.box()
                        box_FA482.alert = False
                        box_FA482.enabled = True
                        box_FA482.active = True
                        box_FA482.use_property_split = False
                        box_FA482.use_property_decorate = False
                        box_FA482.alignment = 'Expand'.upper()
                        box_FA482.scale_x = 1.0
                        box_FA482.scale_y = 1.0
                        if not True: box_FA482.operator_context = "EXEC_DEFAULT"
                        row_7324E = box_FA482.row(heading='', align=True)
                        row_7324E.alert = False
                        row_7324E.enabled = True
                        row_7324E.active = True
                        row_7324E.use_property_split = False
                        row_7324E.use_property_decorate = False
                        row_7324E.scale_x = 1.0
                        row_7324E.scale_y = 1.0
                        row_7324E.alignment = 'Expand'.upper()
                        row_7324E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        attr_4C303 = '["' + str(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'].node_group.interface.items_tree[bpy.context.scene.sna_street_asset_type + ' V'].identifier + '"]') 
                        row_7324E.prop(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'], attr_4C303, text='Show viewport', icon_value=284, emboss=True)
                        attr_BEA71 = '["' + str(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'].node_group.interface.items_tree[bpy.context.scene.sna_street_asset_type + ' R'].identifier + '"]') 
                        row_7324E.prop(bpy.data.objects['ICity Road'].modifiers['GeometryNodes'], attr_BEA71, text='Show render', icon_value=258, emboss=True)
                        if 'Imperfection' in bpy.context.scene.sna_street_asset_type:
                            pass
                        else:
                            col_FE7BC.template_icon_view(bpy.context.scene, 'sna_street_asset_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                        col_BC6CE = col_FE7BC.column(heading='', align=False)
                        col_BC6CE.alert = False
                        col_BC6CE.enabled = True
                        col_BC6CE.active = True
                        col_BC6CE.use_property_split = False
                        col_BC6CE.use_property_decorate = False
                        col_BC6CE.scale_x = 1.0
                        col_BC6CE.scale_y = 1.2999999523162842
                        col_BC6CE.alignment = 'Expand'.upper()
                        col_BC6CE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        row_6105F = col_BC6CE.row(heading='', align=True)
                        row_6105F.alert = False
                        row_6105F.enabled = True
                        row_6105F.active = True
                        row_6105F.use_property_split = False
                        row_6105F.use_property_decorate = False
                        row_6105F.scale_x = 1.0
                        row_6105F.scale_y = 1.7000000476837158
                        row_6105F.alignment = 'Expand'.upper()
                        row_6105F.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
                        if 'Imperfection' in bpy.context.scene.sna_street_asset_type:
                            pass
                        else:
                            op = row_6105F.operator('sna.road_apply_5c3ab', text='Assign', icon_value=0, emboss=True, depress=False)
                            if 'Traffic light' in bpy.context.scene.sna_street_asset_type:
                                pass
                            else:
                                op = row_6105F.operator('sna.road_remove_aa51d', text='remove', icon_value=0, emboss=True, depress=False)
                        if 'Traffic light' in bpy.context.scene.sna_street_asset_type:
                            pass
                        else:
                            if 'Imperfection' in bpy.context.scene.sna_street_asset_type:
                                if property_exists("bpy.data.objects['ICity Road']", globals(), locals()):
                                    col_1009E = col_BC6CE.column(heading='', align=True)
                                    col_1009E.alert = False
                                    col_1009E.enabled = True
                                    col_1009E.active = True
                                    col_1009E.use_property_split = False
                                    col_1009E.use_property_decorate = False
                                    col_1009E.scale_x = 1.0
                                    col_1009E.scale_y = 0.699999988079071
                                    col_1009E.alignment = 'Expand'.upper()
                                    col_1009E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                                    box_5E4A3 = col_1009E.box()
                                    box_5E4A3.alert = False
                                    box_5E4A3.enabled = True
                                    box_5E4A3.active = True
                                    box_5E4A3.use_property_split = False
                                    box_5E4A3.use_property_decorate = False
                                    box_5E4A3.alignment = 'Expand'.upper()
                                    box_5E4A3.scale_x = 1.0
                                    box_5E4A3.scale_y = 1.0
                                    if not True: box_5E4A3.operator_context = "EXEC_DEFAULT"
                                    box_5E4A3.label(text='Leaves path scattering', icon_value=0)
                                    box_5E4A3.prop(bpy.data.node_groups['Road 2'].nodes['Group.012'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_5E4A3.prop(bpy.data.node_groups['Road 2'].nodes['Group.012'].inputs[2], 'default_value', text='Spacing', icon_value=0, emboss=True)
                                    box_613CB = col_1009E.box()
                                    box_613CB.alert = False
                                    box_613CB.enabled = True
                                    box_613CB.active = True
                                    box_613CB.use_property_split = False
                                    box_613CB.use_property_decorate = False
                                    box_613CB.alignment = 'Expand'.upper()
                                    box_613CB.scale_x = 1.0
                                    box_613CB.scale_y = 1.0
                                    if not True: box_613CB.operator_context = "EXEC_DEFAULT"
                                    box_613CB.label(text='Leaves scattering', icon_value=0)
                                    box_613CB.prop(bpy.data.node_groups['Road 2'].nodes['Group.054'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_613CB.prop(bpy.data.node_groups['Road 2'].nodes['Group.054'].inputs[2], 'default_value', text='Density', icon_value=0, emboss=True)
                                    box_0FC83 = col_1009E.box()
                                    box_0FC83.alert = False
                                    box_0FC83.enabled = True
                                    box_0FC83.active = True
                                    box_0FC83.use_property_split = False
                                    box_0FC83.use_property_decorate = False
                                    box_0FC83.alignment = 'Expand'.upper()
                                    box_0FC83.scale_x = 1.0
                                    box_0FC83.scale_y = 1.0
                                    if not True: box_0FC83.operator_context = "EXEC_DEFAULT"
                                    box_0FC83.label(text='Manholes path scattering', icon_value=0)
                                    box_0FC83.prop(bpy.data.node_groups['Road 2'].nodes['Group.011'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_0FC83.prop(bpy.data.node_groups['Road 2'].nodes['Group.011'].inputs[2], 'default_value', text='Spacing', icon_value=0, emboss=True)
                                    box_D5E98 = col_1009E.box()
                                    box_D5E98.alert = False
                                    box_D5E98.enabled = True
                                    box_D5E98.active = True
                                    box_D5E98.use_property_split = False
                                    box_D5E98.use_property_decorate = False
                                    box_D5E98.alignment = 'Expand'.upper()
                                    box_D5E98.scale_x = 1.0
                                    box_D5E98.scale_y = 1.0
                                    if not True: box_D5E98.operator_context = "EXEC_DEFAULT"
                                    box_D5E98.label(text='Water drain path scattering', icon_value=0)
                                    box_D5E98.prop(bpy.data.node_groups['Road 2'].nodes['Group.002'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_D5E98.prop(bpy.data.node_groups['Road 2'].nodes['Group.002'].inputs[2], 'default_value', text='Spacing', icon_value=0, emboss=True)
                                    box_85D7D = col_1009E.box()
                                    box_85D7D.alert = False
                                    box_85D7D.enabled = True
                                    box_85D7D.active = True
                                    box_85D7D.use_property_split = False
                                    box_85D7D.use_property_decorate = False
                                    box_85D7D.alignment = 'Expand'.upper()
                                    box_85D7D.scale_x = 1.0
                                    box_85D7D.scale_y = 1.0
                                    if not True: box_85D7D.operator_context = "EXEC_DEFAULT"
                                    box_85D7D.label(text='Small imperfections scattering', icon_value=0)
                                    box_85D7D.prop(bpy.data.node_groups['Road 2'].nodes['Switch.008'].inputs[1], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_85D7D.prop(bpy.data.node_groups['Road 2'].nodes['Value'].outputs[0], 'default_value', text='Density', icon_value=0, emboss=True)
                                    box_62B9E = col_1009E.box()
                                    box_62B9E.alert = False
                                    box_62B9E.enabled = True
                                    box_62B9E.active = True
                                    box_62B9E.use_property_split = False
                                    box_62B9E.use_property_decorate = False
                                    box_62B9E.alignment = 'Expand'.upper()
                                    box_62B9E.scale_x = 1.0
                                    box_62B9E.scale_y = 1.0
                                    if not True: box_62B9E.operator_context = "EXEC_DEFAULT"
                                    box_62B9E.label(text='Trash imperfection scattering', icon_value=0)
                                    box_62B9E.prop(bpy.data.node_groups['Road 2'].nodes['Switch.009'].inputs[1], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_62B9E.prop(bpy.data.node_groups['Road 2'].nodes['Value.001'].outputs[0], 'default_value', text='Density', icon_value=0, emboss=True)
                                    box_A8198 = col_1009E.box()
                                    box_A8198.alert = False
                                    box_A8198.enabled = True
                                    box_A8198.active = True
                                    box_A8198.use_property_split = False
                                    box_A8198.use_property_decorate = False
                                    box_A8198.alignment = 'Expand'.upper()
                                    box_A8198.scale_x = 1.0
                                    box_A8198.scale_y = 1.0
                                    if not True: box_A8198.operator_context = "EXEC_DEFAULT"
                                    box_A8198.label(text='Water Puddles scattering', icon_value=0)
                                    box_A8198.prop(bpy.data.node_groups['Road 2'].nodes['Group.013'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_A8198.prop(bpy.data.node_groups['Road 2'].nodes['Group.013'].inputs[2], 'default_value', text='Density', icon_value=0, emboss=True)
                                    box_79229 = col_1009E.box()
                                    box_79229.alert = False
                                    box_79229.enabled = True
                                    box_79229.active = True
                                    box_79229.use_property_split = False
                                    box_79229.use_property_decorate = False
                                    box_79229.alignment = 'Expand'.upper()
                                    box_79229.scale_x = 1.0
                                    box_79229.scale_y = 1.0
                                    if not True: box_79229.operator_context = "EXEC_DEFAULT"
                                    box_79229.label(text='Cracks scattering', icon_value=0)
                                    box_79229.prop(bpy.data.node_groups['Road 2'].nodes['Group'].inputs[3], 'default_value', text='Collection', icon_value=0, emboss=True)
                                    box_79229.prop(bpy.data.node_groups['Road 2'].nodes['Group'].inputs[2], 'default_value', text='Density', icon_value=0, emboss=True)
                            else:
                                col_BC3E1 = col_BC6CE.column(heading='', align=True)
                                col_BC3E1.alert = False
                                col_BC3E1.enabled = True
                                col_BC3E1.active = True
                                col_BC3E1.use_property_split = False
                                col_BC3E1.use_property_decorate = False
                                col_BC3E1.scale_x = 1.0
                                col_BC3E1.scale_y = 1.2999999523162842
                                col_BC3E1.alignment = 'Expand'.upper()
                                col_BC3E1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                                if 'Tree' in bpy.context.scene.sna_street_asset_type:
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes['Tree spacing'].outputs[0], 'default_value', text='Spacing', icon_value=0, emboss=True)
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes['Tree spacing'].outputs[0], 'default_value', text='Offset', icon_value=0, emboss=True)
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes['Tree depth offset'].outputs[0], 'default_value', text='Depth offset', icon_value=0, emboss=True)
                                else:
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_street_asset_type].inputs[10], 'default_value', text='Spacing', icon_value=0, emboss=True)
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_street_asset_type].inputs[11], 'default_value', text='Offset', icon_value=0, emboss=True)
                                    col_BC3E1.prop(bpy.data.node_groups['Road 2'].nodes[bpy.context.scene.sna_street_asset_type].inputs[12], 'default_value', text='Depth offset', icon_value=0, emboss=True)
                    if (('Light' in bpy.context.scene.sna_street_asset_type or 'Traffic light' in bpy.context.scene.sna_street_asset_type) and property_exists("bpy.data.lights['ICity Road light'].color", globals(), locals())):
                        col_23D0C = col_2F17C.column(heading='', align=True)
                        col_23D0C.alert = False
                        col_23D0C.enabled = True
                        col_23D0C.active = True
                        col_23D0C.use_property_split = False
                        col_23D0C.use_property_decorate = False
                        col_23D0C.scale_x = 1.0
                        col_23D0C.scale_y = 2.0
                        col_23D0C.alignment = 'Expand'.upper()
                        col_23D0C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        col_23D0C.prop(bpy.data.lights['ICity Road light'], 'color', text='Light color', icon_value=0, emboss=True)
                        col_23D0C.prop(bpy.data.lights['ICity Road light'], 'energy', text='Light power', icon_value=0, emboss=True)
                elif bpy.context.scene.sna_street_assetoptions == "Options":
                    col_80A9F.separator(factor=1.0)
                    col_00A0B = col_80A9F.column(heading='', align=False)
                    col_00A0B.alert = False
                    col_00A0B.enabled = True
                    col_00A0B.active = True
                    col_00A0B.use_property_split = False
                    col_00A0B.use_property_decorate = False
                    col_00A0B.scale_x = 1.0
                    col_00A0B.scale_y = 1.0
                    col_00A0B.alignment = 'Expand'.upper()
                    col_00A0B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_05448 = col_00A0B.row(heading='', align=True)
                    row_05448.alert = False
                    row_05448.enabled = True
                    row_05448.active = True
                    row_05448.use_property_split = False
                    row_05448.use_property_decorate = False
                    row_05448.scale_x = 1.0
                    row_05448.scale_y = 2.2150001525878906
                    row_05448.alignment = 'Expand'.upper()
                    row_05448.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
                    op = row_05448.operator('sna.assign_road_deef9', text='Assign Road', icon_value=0, emboss=True, depress=False)
                    op = row_05448.operator('sna.remove_road_a2302', text='Remove Road', icon_value=0, emboss=True, depress=False)
                    col_00A0B.separator(factor=1.0)
                    col_6B052 = col_00A0B.column(heading='', align=False)
                    col_6B052.alert = False
                    col_6B052.enabled = True
                    col_6B052.active = True
                    col_6B052.use_property_split = False
                    col_6B052.use_property_decorate = False
                    col_6B052.scale_x = 1.0
                    col_6B052.scale_y = 1.0
                    col_6B052.alignment = 'Expand'.upper()
                    col_6B052.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    box_DC2DC = col_6B052.box()
                    box_DC2DC.alert = False
                    box_DC2DC.enabled = True
                    box_DC2DC.active = True
                    box_DC2DC.use_property_split = False
                    box_DC2DC.use_property_decorate = False
                    box_DC2DC.alignment = 'Expand'.upper()
                    box_DC2DC.scale_x = 1.0
                    box_DC2DC.scale_y = 2.0
                    if not True: box_DC2DC.operator_context = "EXEC_DEFAULT"
                    col_76495 = box_DC2DC.column(heading='', align=True)
                    col_76495.alert = False
                    col_76495.enabled = True
                    col_76495.active = True
                    col_76495.use_property_split = False
                    col_76495.use_property_decorate = False
                    col_76495.scale_x = 1.0
                    col_76495.scale_y = 1.0
                    col_76495.alignment = 'Expand'.upper()
                    col_76495.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    col_76495.label(text='Road segment attributes', icon_value=486)
                    col_76495.label(text='Stored on edge', icon_value=110)
                    op = col_76495.operator('sna.set_side_count_49527', text='Set side count', icon_value=0, emboss=True, depress=False)
                    op = col_76495.operator('sna.road_lanes_width_93562', text='Road lanes width', icon_value=0, emboss=True, depress=False)
                    op = col_76495.operator('sna.sidewalk_width_99dc0', text='Sidewalk width', icon_value=0, emboss=True, depress=False)
                    box_E7AC7 = col_6B052.box()
                    box_E7AC7.alert = False
                    box_E7AC7.enabled = True
                    box_E7AC7.active = True
                    box_E7AC7.use_property_split = False
                    box_E7AC7.use_property_decorate = False
                    box_E7AC7.alignment = 'Expand'.upper()
                    box_E7AC7.scale_x = 1.0
                    box_E7AC7.scale_y = 2.0
                    if not True: box_E7AC7.operator_context = "EXEC_DEFAULT"
                    col_A0FAF = box_E7AC7.column(heading='', align=True)
                    col_A0FAF.alert = False
                    col_A0FAF.enabled = True
                    col_A0FAF.active = True
                    col_A0FAF.use_property_split = False
                    col_A0FAF.use_property_decorate = False
                    col_A0FAF.scale_x = 1.0
                    col_A0FAF.scale_y = 1.0
                    col_A0FAF.alignment = 'Expand'.upper()
                    col_A0FAF.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    col_A0FAF.label(text='Road intersection attributes', icon_value=486)
                    col_A0FAF.label(text='Stored on vertex', icon_value=110)
                    op = col_A0FAF.operator('sna.intersection_offset_16e01', text='Intersection offset', icon_value=0, emboss=True, depress=False)
                    op = col_A0FAF.operator('sna.crosswalk_offset_b1e82', text='Crosswalk offset', icon_value=0, emboss=True, depress=False)
                else:
                    pass
            elif bpy.context.scene.sna_citystreet == "City":
                col_79CA6 = col_84076.column(heading='', align=False)
                col_79CA6.alert = False
                col_79CA6.enabled = True
                col_79CA6.active = True
                col_79CA6.use_property_split = False
                col_79CA6.use_property_decorate = False
                col_79CA6.scale_x = 1.0
                col_79CA6.scale_y = 1.0
                col_79CA6.alignment = 'Expand'.upper()
                col_79CA6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_C5AC3 = col_79CA6.row(heading='', align=False)
                row_C5AC3.alert = False
                row_C5AC3.enabled = True
                row_C5AC3.active = True
                row_C5AC3.use_property_split = False
                row_C5AC3.use_property_decorate = False
                row_C5AC3.scale_x = 1.0
                row_C5AC3.scale_y = 1.0
                row_C5AC3.alignment = 'Expand'.upper()
                row_C5AC3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_C5AC3.prop(bpy.context.scene, 'sna_city_space_type', text='.', icon_value=0, emboss=True, expand=True)
                if bpy.context.scene.sna_city_space_type == "Procedural":
                    col_08F13 = col_79CA6.column(heading='', align=False)
                    col_08F13.alert = False
                    col_08F13.enabled = True
                    col_08F13.active = True
                    col_08F13.use_property_split = False
                    col_08F13.use_property_decorate = False
                    col_08F13.scale_x = 1.0
                    col_08F13.scale_y = 1.0
                    col_08F13.alignment = 'Expand'.upper()
                    col_08F13.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    if sna_is_collection_not_empty_B0A78('ICity_Procedural'):
                        box_19452 = col_08F13.box()
                        box_19452.alert = False
                        box_19452.enabled = True
                        box_19452.active = True
                        box_19452.use_property_split = False
                        box_19452.use_property_decorate = False
                        box_19452.alignment = 'Expand'.upper()
                        box_19452.scale_x = 1.0
                        box_19452.scale_y = 1.0
                        if not True: box_19452.operator_context = "EXEC_DEFAULT"
                        row_0D362 = box_19452.row(heading='', align=True)
                        row_0D362.alert = False
                        row_0D362.enabled = True
                        row_0D362.active = True
                        row_0D362.use_property_split = False
                        row_0D362.use_property_decorate = False
                        row_0D362.scale_x = 1.0
                        row_0D362.scale_y = 1.0
                        row_0D362.alignment = 'Expand'.upper()
                        row_0D362.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        row_0D362.prop(bpy.data.node_groups['Hide viewport input'].nodes['Group.020'].inputs[0], 'default_value', text='Show viewport all', icon_value=284, emboss=True)
                        row_0D362.prop(bpy.data.node_groups['Hide viewport input'].nodes['Group.020'].inputs[1], 'default_value', text='Show render all', icon_value=258, emboss=True)
                    col_08F13.template_icon_view(bpy.context.scene, 'sna_procedural_building_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                    box_57F3F = col_08F13.box()
                    box_57F3F.alert = False
                    box_57F3F.enabled = True
                    box_57F3F.active = True
                    box_57F3F.use_property_split = False
                    box_57F3F.use_property_decorate = False
                    box_57F3F.alignment = 'Expand'.upper()
                    box_57F3F.scale_x = 1.0
                    box_57F3F.scale_y = 1.5
                    if not True: box_57F3F.operator_context = "EXEC_DEFAULT"
                    box_57F3F.label(text='Buildings hight', icon_value=297)
                    op = box_57F3F.operator('sna.floor_count_min_c2cf8', text='Storey count', icon_value=0, emboss=True, depress=False)
                    box_8E415 = col_08F13.box()
                    box_8E415.alert = False
                    box_8E415.enabled = True
                    box_8E415.active = True
                    box_8E415.use_property_split = False
                    box_8E415.use_property_decorate = False
                    box_8E415.alignment = 'Expand'.upper()
                    box_8E415.scale_x = 1.0
                    box_8E415.scale_y = 1.5
                    if not False: box_8E415.operator_context = "EXEC_DEFAULT"
                    box_8E415.label(text='Lighting', icon_value=239)
                    if sna_is_collection_not_empty_B0A78('ICity_Procedural'):
                        box_8E415.prop(bpy.data.node_groups['Light controler'].nodes['Switch'].inputs[0], 'default_value', text='Building light', icon_value=0, emboss=True, toggle=True)
                        box_8E415.prop(bpy.data.node_groups['Light controler'].nodes['Random Value.002'].inputs[6], 'default_value', text='Probability', icon_value=0, emboss=True, slider=True)
                    if sna_is_collection_not_empty_B0A78('ICity_Procedural'):
                        box_1203C = col_08F13.box()
                        box_1203C.alert = False
                        box_1203C.enabled = True
                        box_1203C.active = True
                        box_1203C.use_property_split = False
                        box_1203C.use_property_decorate = False
                        box_1203C.alignment = 'Expand'.upper()
                        box_1203C.scale_x = 1.0
                        box_1203C.scale_y = 1.0
                        if not True: box_1203C.operator_context = "EXEC_DEFAULT"
                        box_1203C.label(text='Props', icon_value=124)
                        row_9A266 = box_1203C.row(heading='', align=True)
                        row_9A266.alert = False
                        row_9A266.enabled = True
                        row_9A266.active = True
                        row_9A266.use_property_split = False
                        row_9A266.use_property_decorate = False
                        row_9A266.scale_x = 1.0
                        row_9A266.scale_y = 1.0
                        row_9A266.alignment = 'Expand'.upper()
                        row_9A266.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                        row_9A266.prop(bpy.data.node_groups['Hide viewport input'].nodes['Group.019'].inputs[0], 'default_value', text='Show viewport', icon_value=284, emboss=True)
                        row_9A266.prop(bpy.data.node_groups['Hide viewport input'].nodes['Group.019'].inputs[1], 'default_value', text='Show render', icon_value=258, emboss=True)
                    box_0106D = col_08F13.box()
                    box_0106D.alert = False
                    box_0106D.enabled = True
                    box_0106D.active = True
                    box_0106D.use_property_split = False
                    box_0106D.use_property_decorate = False
                    box_0106D.alignment = 'Expand'.upper()
                    box_0106D.scale_x = 1.0
                    box_0106D.scale_y = 1.0
                    if not True: box_0106D.operator_context = "EXEC_DEFAULT"
                    box_0106D.label(text='Ground Props', icon_value=124)
                    row_D3F65 = box_0106D.row(heading='', align=True)
                    row_D3F65.alert = False
                    row_D3F65.enabled = True
                    row_D3F65.active = True
                    row_D3F65.use_property_split = False
                    row_D3F65.use_property_decorate = False
                    row_D3F65.scale_x = 1.0
                    row_D3F65.scale_y = 1.0
                    row_D3F65.alignment = 'Expand'.upper()
                    row_D3F65.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    attr_7A9B1 = '["' + str('Socket_2' + '"]') 
                    row_D3F65.prop(bpy.data.objects['ICity Procedural ground'].modifiers['GeometryNodes'], attr_7A9B1, text='Show viewport', icon_value=284, emboss=True)
                    attr_6AF46 = '["' + str('Socket_3' + '"]') 
                    row_D3F65.prop(bpy.data.objects['ICity Procedural ground'].modifiers['GeometryNodes'], attr_6AF46, text='Show render', icon_value=258, emboss=True)
                elif bpy.context.scene.sna_city_space_type == "Park":
                    col_E7026 = col_79CA6.column(heading='', align=False)
                    col_E7026.alert = False
                    col_E7026.enabled = True
                    col_E7026.active = True
                    col_E7026.use_property_split = False
                    col_E7026.use_property_decorate = False
                    col_E7026.scale_x = 1.0
                    col_E7026.scale_y = 1.0
                    col_E7026.alignment = 'Expand'.upper()
                    col_E7026.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    box_C0D17 = col_E7026.box()
                    box_C0D17.alert = False
                    box_C0D17.enabled = True
                    box_C0D17.active = True
                    box_C0D17.use_property_split = False
                    box_C0D17.use_property_decorate = False
                    box_C0D17.alignment = 'Expand'.upper()
                    box_C0D17.scale_x = 1.0
                    box_C0D17.scale_y = 1.0
                    if not True: box_C0D17.operator_context = "EXEC_DEFAULT"
                    row_F1591 = box_C0D17.row(heading='', align=True)
                    row_F1591.alert = False
                    row_F1591.enabled = True
                    row_F1591.active = True
                    row_F1591.use_property_split = False
                    row_F1591.use_property_decorate = False
                    row_F1591.scale_x = 1.0
                    row_F1591.scale_y = 1.0
                    row_F1591.alignment = 'Expand'.upper()
                    row_F1591.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_F1591.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[1], 'default_value', text='Show viewport all', icon_value=284, emboss=True)
                    row_F1591.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[2], 'default_value', text='Show render all', icon_value=258, emboss=True)
                    col_E7026.template_icon_view(bpy.context.scene, 'sna_park_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                    col_B54D3 = col_E7026.column(heading='', align=False)
                    col_B54D3.alert = False
                    col_B54D3.enabled = True
                    col_B54D3.active = True
                    col_B54D3.use_property_split = False
                    col_B54D3.use_property_decorate = False
                    col_B54D3.scale_x = 1.0
                    col_B54D3.scale_y = 1.0
                    col_B54D3.alignment = 'Expand'.upper()
                    col_B54D3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    box_97B99 = col_B54D3.box()
                    box_97B99.alert = False
                    box_97B99.enabled = True
                    box_97B99.active = True
                    box_97B99.use_property_split = False
                    box_97B99.use_property_decorate = False
                    box_97B99.alignment = 'Expand'.upper()
                    box_97B99.scale_x = 1.0
                    box_97B99.scale_y = 1.0
                    if not True: box_97B99.operator_context = "EXEC_DEFAULT"
                    box_97B99.label(text='Trees', icon_value=651)
                    row_33EA6 = box_97B99.row(heading='', align=True)
                    row_33EA6.alert = False
                    row_33EA6.enabled = True
                    row_33EA6.active = True
                    row_33EA6.use_property_split = False
                    row_33EA6.use_property_decorate = False
                    row_33EA6.scale_x = 1.0
                    row_33EA6.scale_y = 1.0
                    row_33EA6.alignment = 'Expand'.upper()
                    row_33EA6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_33EA6.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[5], 'default_value', text='Show viewport all', icon_value=284, emboss=True)
                    row_33EA6.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[6], 'default_value', text='Show render all', icon_value=258, emboss=True)
                elif bpy.context.scene.sna_city_space_type == "Presets":
                    col_79CA6.template_icon_view(bpy.context.scene, 'sna_building_presets_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                    col_EC116 = col_79CA6.column(heading='', align=False)
                    col_EC116.alert = False
                    col_EC116.enabled = True
                    col_EC116.active = True
                    col_EC116.use_property_split = False
                    col_EC116.use_property_decorate = False
                    col_EC116.scale_x = 1.0
                    col_EC116.scale_y = 1.0
                    col_EC116.alignment = 'Expand'.upper()
                    col_EC116.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_7468A = col_EC116.row(heading='', align=True)
                    row_7468A.alert = False
                    row_7468A.enabled = True
                    row_7468A.active = True
                    row_7468A.use_property_split = False
                    row_7468A.use_property_decorate = False
                    row_7468A.scale_x = 1.0
                    row_7468A.scale_y = 1.9900000095367432
                    row_7468A.alignment = 'Expand'.upper()
                    row_7468A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    op = row_7468A.operator('sna.offset_x_preset_5a427', text='Offset x', icon_value=0, emboss=True, depress=False)
                    op = row_7468A.operator('sna.offset_y_preset_dcad4', text='Offset y', icon_value=0, emboss=True, depress=False)
                    op = row_7468A.operator('sna.rotation_z_preset_60648', text='Rotation z', icon_value=0, emboss=True, depress=False)
                    col_EC116.template_icon_view(bpy.context.scene, 'sna_landscape_browser', show_labels=True, scale=7.0, scale_popup=7.0)
                    row_35139 = col_EC116.row(heading='', align=True)
                    row_35139.alert = False
                    row_35139.enabled = True
                    row_35139.active = True
                    row_35139.use_property_split = False
                    row_35139.use_property_decorate = False
                    row_35139.scale_x = 1.0
                    row_35139.scale_y = 1.0
                    row_35139.alignment = 'Expand'.upper()
                    row_35139.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_35139.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[5], 'default_value', text='Show viewport all', icon_value=284, emboss=True)
                    row_35139.prop(bpy.data.node_groups['Spaces'].nodes['Group.001'].inputs[6], 'default_value', text='Show render all', icon_value=258, emboss=True)
                else:
                    pass
                col_02D31 = col_79CA6.column(heading='', align=False)
                col_02D31.alert = False
                col_02D31.enabled = True
                col_02D31.active = True
                col_02D31.use_property_split = False
                col_02D31.use_property_decorate = False
                col_02D31.scale_x = 1.0
                col_02D31.scale_y = 1.0
                col_02D31.alignment = 'Expand'.upper()
                col_02D31.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_7B011 = col_02D31.row(heading='', align=True)
                row_7B011.alert = False
                row_7B011.enabled = True
                row_7B011.active = True
                row_7B011.use_property_split = False
                row_7B011.use_property_decorate = False
                row_7B011.scale_x = 1.0
                row_7B011.scale_y = 1.9900000095367432
                row_7B011.alignment = 'Expand'.upper()
                row_7B011.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                op = row_7B011.operator('sna.offset_x_a87eb', text='Offset x', icon_value=0, emboss=True, depress=False)
                op = row_7B011.operator('sna.offset_y_45b11', text='Offset y', icon_value=0, emboss=True, depress=False)
                op = row_7B011.operator('sna.rotation_z_4edcd', text='Rotation z', icon_value=0, emboss=True, depress=False)
                row_6D74F = col_02D31.row(heading='', align=True)
                row_6D74F.alert = False
                row_6D74F.enabled = True
                row_6D74F.active = True
                row_6D74F.use_property_split = False
                row_6D74F.use_property_decorate = False
                row_6D74F.scale_x = 1.0
                row_6D74F.scale_y = 1.9900000095367432
                row_6D74F.alignment = 'Expand'.upper()
                row_6D74F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                op = row_6D74F.operator('sna.city_apply_dae66', text='Assign', icon_value=0, emboss=True, depress=False)
            else:
                pass


def sna_update_sna_street_asset_type_append(self, context):
    sna_update_sna_street_asset_type_append_FC104(self, context)
    sna_update_sna_street_asset_type_append_F3D9F(self, context)


def sna_update_sna_city_space_type(self, context):
    sna_update_sna_city_space_type_F658C(self, context)
    sna_update_sna_city_space_type_AE473(self, context)


def sna_sidewalk_curb_mat_enum_items(self, context):
    return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]


def sna_append_browser_enum_items(self, context):
    return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]

# 枚举选项格式为 (identifier, name, description, icon, number)，其中：
# identifier 是选项的唯一标识符。
# name 是显示在UI中的名称。
# description 是描述（这里为空）。
# icon 是图标（这里为空）。
# number 是选项的索引。

def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_citystreet = bpy.props.EnumProperty(name='city-street', description='', items=[('City', 'City', '', 0, 0), ('Road', 'Road', '', 0, 1)])
    bpy.types.Scene.sna_citystreet_append = bpy.props.EnumProperty(name='city-street append', description='', items=[('City', 'City', '', 0, 0), ('Road', 'Road', '', 0, 1)])
    bpy.types.Scene.sna_city_space_type_append = bpy.props.EnumProperty(name='City space type append', description='', items=[('Procedural', 'Procedural', '', 0, 0), ('Park', 'Park', '', 0, 1), ('Presets', 'Presets', '', 0, 2)], update=sna_update_sna_city_space_type_append_A7B1C)
    bpy.types.Scene.sna_street_asset_type_append = bpy.props.EnumProperty(name='street asset type append', description='', items=[('Light', 'Light', '', 0, 0), ('Bench', 'Bench', '', 0, 1), ('Tree', 'Tree', '', 0, 2), ('Services', 'Services', '', 0, 3), ('Bollard', 'Bollard', '', 0, 4), ('Traffic light', 'Traffic light', '', 0, 5), ('Cars', 'Cars', '', 0, 6), ('Sign', 'Sign', '', 0, 7), ('Texture', 'Texture', '', 0, 8), ('Imperfection', 'Imperfection', '', 0, 9)], update=sna_update_sna_street_asset_type_append)
    bpy.types.Scene.sna_street_assetoptions = bpy.props.EnumProperty(name='street asset-options', description='', items=[('Assets', 'Assets', '', 0, 0), ('Options', 'Options', '', 0, 1)])
    bpy.types.Scene.sna_street_asset_type = bpy.props.EnumProperty(name='street asset type', description='', items=[('Light', 'Light', '', 0, 0), ('Bench', 'Bench', '', 0, 1), ('Tree', 'Tree', '', 0, 2), ('Services', 'Services', '', 0, 3), ('Bollard', 'Bollard', '', 0, 4), ('Traffic light', 'Traffic light', '', 0, 5), ('Cars', 'Cars', '', 0, 6), ('Sign', 'Sign', '', 0, 7), ('Texture', 'Texture', '', 0, 8), ('Imperfection', 'Imperfection', '', 0, 9)], update=sna_update_sna_street_asset_type_BF136)
    bpy.types.Scene.sna_landscape_browser_append = bpy.props.EnumProperty(name='Landscape browser append', description='', items=sna_landscape_browser_append_enum_items)
    bpy.types.Scene.sna_street_asset_browser = bpy.props.EnumProperty(name='Street asset browser', description='', items=sna_street_asset_browser_enum_items)
    bpy.types.Scene.sna_procedural_building_browser = bpy.props.EnumProperty(name='Procedural building browser', description='', items=sna_procedural_building_browser_enum_items)
    bpy.types.Scene.sna_city_space_type = bpy.props.EnumProperty(name='City space type', description='', items=[('Procedural', 'Procedural', '', 0, 0), ('Park', 'Park', '', 0, 1), ('Presets', 'Presets', '', 0, 2)], update=sna_update_sna_city_space_type)
    bpy.types.Scene.sna_city_building_presets_type = bpy.props.EnumProperty(name='City building presets type', description='', items=[('Skyscrapper', 'Skyscrapper', '', 0, 0), ('Court', 'Court', '', 0, 1), ('Market', 'Market', '', 0, 2), ('Fire station', 'Fire station', '', 0, 3), ('Police station', 'Police station', '', 0, 4), ('Hospital', 'Hospital', '', 0, 5)], update=sna_update_sna_city_building_presets_type_FB155)
    bpy.types.Scene.sna_city_building_presets_type_append = bpy.props.EnumProperty(name='City building presets type append', description='', items=[('Skyscrapper', 'Skyscrapper', '', 0, 0), ('Court', 'Court', '', 0, 1), ('Market', 'Market', '', 0, 2), ('Fire station', 'Fire station', '', 0, 3), ('Police station', 'Police station', '', 0, 4), ('Hospital', 'Hospital', '', 0, 5)], update=sna_update_sna_city_building_presets_type_append_A77BA)
    bpy.types.Scene.sna_road_materials_type_append = bpy.props.EnumProperty(name='Road materials type append', description='', items=[('Road', 'Road', '', 0, 0), ('Curb', 'Curb', '', 0, 1), ('Sidewalk', 'Sidewalk', '', 0, 2)], update=sna_update_sna_road_materials_type_append_CB7F1)
    bpy.types.Scene.sna_building_presets_browser = bpy.props.EnumProperty(name='Building presets browser', description='', items=sna_building_presets_browser_enum_items)
    bpy.types.Scene.sna_style = bpy.props.EnumProperty(name='Style', description='', items=[('All', 'All', '', 0, 0), ('General', 'General', '', 0, 1), ('Chicago', 'Chicago', '', 0, 2)])
    bpy.types.Scene.sna_park_browser = bpy.props.EnumProperty(name='Park browser', description='', items=sna_park_browser_enum_items)
    bpy.types.Scene.sna_sidewalk_mat = bpy.props.EnumProperty(name='Sidewalk mat', description='', items=sna_sidewalk_mat_enum_items)
    bpy.types.Scene.sna_sidewalk_curb_mat = bpy.props.EnumProperty(name='Sidewalk Curb mat', description='', items=sna_sidewalk_curb_mat_enum_items)
    bpy.types.Scene.sna_landscape_browser = bpy.props.EnumProperty(name='Landscape browser', description='', items=sna_landscape_browser_enum_items)
    bpy.types.Scene.sna_theme = bpy.props.EnumProperty(name='THEME', description='', items=sna_theme_enum_items, options={'ENUM_FLAG'}, update=sna_update_sna_theme_88C83)
    bpy.types.Scene.sna_append_browser = bpy.props.EnumProperty(name='Append browser', description='', items=sna_append_browser_enum_items)
    bpy.types.Scene.sna_test = bpy.props.EnumProperty(name='Test', description='', items=sna_test_enum_items)
    bpy.types.Scene.sna_city_browser_append = bpy.props.EnumProperty(name='City browser append', description='', items=sna_city_browser_append_enum_items)
    bpy.types.Scene.sna_road_browser_append = bpy.props.EnumProperty(name='Road browser append', description='', items=sna_road_browser_append_enum_items)
    bpy.types.Scene.sna_assets_folder_path = bpy.props.StringProperty(name='Assets folder path', description='', default='', subtype='FILE_PATH', maxlen=0)
    bpy.types.Object.sna_asset_category_path_object = bpy.props.StringProperty(name='Asset category path object', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Collection.sna_asset_category_path_collection = bpy.props.StringProperty(name='Asset category path collection', description='', default='', subtype='FILE_PATH', maxlen=0)
    bpy.types.Material.sna_asset_category_path_material = bpy.props.StringProperty(name='Asset category path material', description='', default='', subtype='FILE_PATH', maxlen=0)
    bpy.types.Scene.sna_road_materials_browser = bpy.props.EnumProperty(name='Road materials browser', description='', items=sna_road_materials_browser_enum_items)
    bpy.types.Scene.sna_road_materials_browser_append = bpy.props.EnumProperty(name='Road materials browser append', description='', items=sna_road_materials_browser_append_enum_items)
    bpy.types.Scene.sna_road_materials_type_ = bpy.props.EnumProperty(name='Road materials type ', description='', items=[('Road', 'Road', '', 0, 0), ('Curb', 'Curb', '', 0, 1), ('Sidewalk', 'Sidewalk', '', 0, 2)], update=sna_update_sna_road_materials_type__75061)
    bpy.types.Scene.sna_light_mode = bpy.props.BoolProperty(name='Light mode', description='', default=False)
    bpy.types.Scene.sna_proxy_mode = bpy.props.BoolProperty(name='Proxy mode', description='', default=False, update=sna_update_sna_proxy_mode_0EBCB)
    bpy.utils.register_class(SNA_OT_Store_All_Assets_5B09E)
    bpy.utils.register_class(SNA_OT_Refresh_Theme_443Bd)
    bpy.utils.register_class(SNA_OT_Refresh_C6Cb8)
    bpy.utils.register_class(SNA_OT_Read_97C87)
    bpy.utils.register_class(SNA_OT_Filter_City_Assets_Ea982)
    bpy.utils.register_class(SNA_OT_Filter_Road_Bc600)
    bpy.utils.register_class(SNA_OT_Filter_Theme_31D4C)
    bpy.utils.register_class(SNA_MT_89AD5)
    bpy.utils.register_class(SNA_MT_8CD9F)
    bpy.utils.register_class(SNA_MT_0BED6)
    bpy.utils.register_class(SNA_OT_Append_Panel_Lunch_221D5)
    bpy.utils.register_class(SNA_PT_APPEND_PANEL_590A1)
    bpy.utils.register_class(SNA_OT_Open_Addon_Prefrences_34Afe)
    bpy.utils.register_class(SNA_OT_Hide_Park_R_192D6)
    bpy.utils.register_class(SNA_OT_Grass_R_E07D4)
    bpy.utils.register_class(SNA_OT_Grass_V_4Cdd7)
    bpy.utils.register_class(SNA_OT_Trees_R_164C2)
    bpy.utils.register_class(SNA_OT_Trees_V_25C59)
    bpy.utils.register_class(SNA_OT_Hide_Park_3Ea8F)
    bpy.utils.register_class(SNA_PT_ICITY_754AD)
    bpy.utils.register_class(SNA_OT_Material_Filter_F04C3)
    bpy.utils.register_class(SNA_OT_Road_Materials_Filter_6A3Ec)
    bpy.utils.register_class(SNA_OT_Start_5209E)
    bpy.utils.register_class(SNA_OT_City_Apply_Dae66)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_361D3)
    bpy.utils.register_class(SNA_OT_Road_Apply_5C3Ab)
    bpy.utils.register_class(SNA_OT_Sync_City_76707)
    bpy.utils.register_class(SNA_OT_Floor_Count_Min_C2Cf8)
    bpy.utils.register_class(SNA_OT_Floor_Count_Max_Db555)
    bpy.utils.register_class(SNA_OT_Offset_X_A87Eb)
    bpy.utils.register_class(SNA_OT_Offset_Y_45B11)
    bpy.utils.register_class(SNA_OT_Rotation_Z_4Edcd)
    bpy.utils.register_class(SNA_OT_Offset_X_Preset_5A427)
    bpy.utils.register_class(SNA_OT_Offset_Y_Preset_Dcad4)
    bpy.utils.register_class(SNA_OT_Rotation_Z_Preset_60648)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre_handler_59166)
    bpy.utils.register_class(SNA_OT_Set_Side_Count_49527)
    bpy.utils.register_class(SNA_OT_Assign_Road_Deef9)
    bpy.utils.register_class(SNA_OT_Remove_Road_A2302)
    bpy.utils.register_class(SNA_OT_Road_Lanes_Width_93562)
    bpy.utils.register_class(SNA_OT_Sidewalk_Width_99Dc0)
    bpy.utils.register_class(SNA_OT_Crosswalk_Offset_B1E82)
    bpy.utils.register_class(SNA_OT_Append_Assets_Ffd74)
    bpy.utils.register_class(SNA_OT_Append_Landscape_C97Bb)
    bpy.utils.register_class(SNA_OT_Intersection_Offset_16E01)
    bpy.utils.register_class(SNA_OT_Edit_City_D7Cab)
    bpy.utils.register_class(SNA_OT_Delete_From_Scene_City_324Ff)
    bpy.utils.register_class(SNA_OT_Light_City_20Ca9)
    bpy.utils.register_class(SNA_OT_Delete_From_Scene_7C7D8)
    bpy.utils.register_class(SNA_OT_Road_Remove_Aa51D)
    bpy.utils.register_class(SNA_AddonPreferences_7CCE1)
    bpy.utils.register_class(SNA_OT_Test_Assets_B9626)
    bpy.utils.register_class(SNA_OT_Refresh_Edit_F156A)
    bpy.utils.register_class(SNA_OT_Filter_Presets_Fb5A4)
    bpy.utils.register_class(SNA_OT_Procedural_Building_Filter_05Bed)
    bpy.utils.register_class(SNA_OT_Park_Filter_5A7A2)
    bpy.utils.register_class(SNA_OT_Landscape_Filter_0Bf89)
    bpy.utils.register_class(SNA_OT_Filter_Street_Assets_C5C0E)
    bpy.utils.register_class(SNA_PT_ICITY_EDITOR_6D34D)
    ecology_extension.register()
    asset_extension.register()
    traffic_extension.register()
    pedestrian_extension.register()
    template_extension.register()
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new('sna.open_addon_prefrences_34afe', 'M', 'PRESS',
        ctrl=False, alt=False, shift=True, repeat=False)
    addon_keymaps['0285F'] = (km, kmi)


def unregister():
    global _icons
    template_extension.unregister()
    pedestrian_extension.unregister()
    traffic_extension.unregister()
    asset_extension.unregister()
    ecology_extension.unregister()
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_proxy_mode
    del bpy.types.Scene.sna_light_mode
    del bpy.types.Scene.sna_road_materials_type_
    del bpy.types.Scene.sna_road_materials_browser_append
    del bpy.types.Scene.sna_road_materials_browser
    del bpy.types.Material.sna_asset_category_path_material
    del bpy.types.Collection.sna_asset_category_path_collection
    del bpy.types.Object.sna_asset_category_path_object
    del bpy.types.Scene.sna_assets_folder_path
    del bpy.types.Scene.sna_road_browser_append
    del bpy.types.Scene.sna_city_browser_append
    del bpy.types.Scene.sna_test
    del bpy.types.Scene.sna_append_browser
    del bpy.types.Scene.sna_theme
    del bpy.types.Scene.sna_landscape_browser
    del bpy.types.Scene.sna_sidewalk_curb_mat
    del bpy.types.Scene.sna_sidewalk_mat
    del bpy.types.Scene.sna_park_browser
    del bpy.types.Scene.sna_style
    del bpy.types.Scene.sna_building_presets_browser
    del bpy.types.Scene.sna_road_materials_type_append
    del bpy.types.Scene.sna_city_building_presets_type_append
    del bpy.types.Scene.sna_city_building_presets_type
    del bpy.types.Scene.sna_city_space_type
    del bpy.types.Scene.sna_procedural_building_browser
    del bpy.types.Scene.sna_street_asset_browser
    del bpy.types.Scene.sna_landscape_browser_append
    del bpy.types.Scene.sna_street_asset_type
    del bpy.types.Scene.sna_street_assetoptions
    del bpy.types.Scene.sna_street_asset_type_append
    del bpy.types.Scene.sna_city_space_type_append
    del bpy.types.Scene.sna_citystreet_append
    del bpy.types.Scene.sna_citystreet
    bpy.utils.unregister_class(SNA_OT_Store_All_Assets_5B09E)
    bpy.utils.unregister_class(SNA_OT_Refresh_Theme_443Bd)
    bpy.utils.unregister_class(SNA_OT_Refresh_C6Cb8)
    bpy.utils.unregister_class(SNA_OT_Read_97C87)
    bpy.utils.unregister_class(SNA_OT_Filter_City_Assets_Ea982)
    bpy.utils.unregister_class(SNA_OT_Filter_Road_Bc600)
    bpy.utils.unregister_class(SNA_OT_Filter_Theme_31D4C)
    bpy.utils.unregister_class(SNA_MT_89AD5)
    bpy.utils.unregister_class(SNA_MT_8CD9F)
    bpy.utils.unregister_class(SNA_MT_0BED6)
    bpy.utils.unregister_class(SNA_OT_Append_Panel_Lunch_221D5)
    bpy.utils.unregister_class(SNA_PT_APPEND_PANEL_590A1)
    bpy.utils.unregister_class(SNA_OT_Open_Addon_Prefrences_34Afe)
    bpy.utils.unregister_class(SNA_OT_Hide_Park_R_192D6)
    bpy.utils.unregister_class(SNA_OT_Grass_R_E07D4)
    bpy.utils.unregister_class(SNA_OT_Grass_V_4Cdd7)
    bpy.utils.unregister_class(SNA_OT_Trees_R_164C2)
    bpy.utils.unregister_class(SNA_OT_Trees_V_25C59)
    bpy.utils.unregister_class(SNA_OT_Hide_Park_3Ea8F)
    bpy.utils.unregister_class(SNA_PT_ICITY_754AD)
    bpy.utils.unregister_class(SNA_OT_Material_Filter_F04C3)
    bpy.utils.unregister_class(SNA_OT_Road_Materials_Filter_6A3Ec)
    bpy.utils.unregister_class(SNA_OT_Start_5209E)
    bpy.utils.unregister_class(SNA_OT_City_Apply_Dae66)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_361D3)
    bpy.utils.unregister_class(SNA_OT_Road_Apply_5C3Ab)
    bpy.utils.unregister_class(SNA_OT_Sync_City_76707)
    bpy.utils.unregister_class(SNA_OT_Floor_Count_Min_C2Cf8)
    bpy.utils.unregister_class(SNA_OT_Floor_Count_Max_Db555)
    bpy.utils.unregister_class(SNA_OT_Offset_X_A87Eb)
    bpy.utils.unregister_class(SNA_OT_Offset_Y_45B11)
    bpy.utils.unregister_class(SNA_OT_Rotation_Z_4Edcd)
    bpy.utils.unregister_class(SNA_OT_Offset_X_Preset_5A427)
    bpy.utils.unregister_class(SNA_OT_Offset_Y_Preset_Dcad4)
    bpy.utils.unregister_class(SNA_OT_Rotation_Z_Preset_60648)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre_handler_59166)
    bpy.utils.unregister_class(SNA_OT_Set_Side_Count_49527)
    bpy.utils.unregister_class(SNA_OT_Assign_Road_Deef9)
    bpy.utils.unregister_class(SNA_OT_Remove_Road_A2302)
    bpy.utils.unregister_class(SNA_OT_Road_Lanes_Width_93562)
    bpy.utils.unregister_class(SNA_OT_Sidewalk_Width_99Dc0)
    bpy.utils.unregister_class(SNA_OT_Crosswalk_Offset_B1E82)
    bpy.utils.unregister_class(SNA_OT_Append_Assets_Ffd74)
    bpy.utils.unregister_class(SNA_OT_Append_Landscape_C97Bb)
    bpy.utils.unregister_class(SNA_OT_Intersection_Offset_16E01)
    bpy.utils.unregister_class(SNA_OT_Edit_City_D7Cab)
    bpy.utils.unregister_class(SNA_OT_Delete_From_Scene_City_324Ff)
    bpy.utils.unregister_class(SNA_OT_Light_City_20Ca9)
    bpy.utils.unregister_class(SNA_OT_Delete_From_Scene_7C7D8)
    bpy.utils.unregister_class(SNA_OT_Road_Remove_Aa51D)
    bpy.utils.unregister_class(SNA_AddonPreferences_7CCE1)
    bpy.utils.unregister_class(SNA_OT_Test_Assets_B9626)
    bpy.utils.unregister_class(SNA_OT_Refresh_Edit_F156A)
    bpy.utils.unregister_class(SNA_OT_Filter_Presets_Fb5A4)
    bpy.utils.unregister_class(SNA_OT_Procedural_Building_Filter_05Bed)
    bpy.utils.unregister_class(SNA_OT_Park_Filter_5A7A2)
    bpy.utils.unregister_class(SNA_OT_Landscape_Filter_0Bf89)
    bpy.utils.unregister_class(SNA_OT_Filter_Street_Assets_C5C0E)
    bpy.utils.unregister_class(SNA_PT_ICITY_EDITOR_6D34D)
