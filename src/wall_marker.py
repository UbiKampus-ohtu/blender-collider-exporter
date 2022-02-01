import os
import bpy
import json
import math
from mathutils import Vector

def blender_vector3_to_unity(vec3):
  return Vector((
    -vec3.x,
    vec3.z,
    -vec3.y
  ))

def format_vector3(vec3):
  return {
    'x':vec3.x,
    'y':vec3.y,
    'z':vec3.z
  }

def get_bounding_parameters(obj):
  world_origin = Vector((0,0,0))
  bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
  for corner in bbox_corners:
    world_origin += corner
  
  world_origin = world_origin / 8
  width = obj.dimensions.x
  depth = obj.dimensions.y
  height = obj.dimensions.z
  
  rotation = Vector((0,0,0))
  rotation.x = math.degrees(obj.rotation_euler.x)
  rotation.y = math.degrees(obj.rotation_euler.y)
  rotation.z = math.degrees(obj.rotation_euler.z)
  
  return {
    'origin': format_vector3(blender_vector3_to_unity(world_origin)),
    'rotation': format_vector3(blender_vector3_to_unity(rotation)),
    'dimensions': {
      'width': width,
      'depth': depth,
      'height': height
    }
  }

def get_objects_from_scene_with_material_name(material_name):
  target_material = bpy.data.materials.get(material_name)
  if target_material == None:
    return []
  
  objects = bpy.context.scene.objects
  result = []
  
  for obj in objects:
    if obj.data.materials[0].name == target_material.name:
      print(obj.data.materials[0].name,target_material.name)
      result.append(obj)
  return result

def generate_bbox_json(material_name, filename):
  result = []
  objects = get_objects_from_scene_with_material_name(material_name)
  for obj in objects:
    data = get_bounding_parameters(obj)
    result.append(data)
  
  json_data = json.dumps({"colliders":result}, indent=1, ensure_ascii=True)
  
  file_path = bpy.path.abspath("//" + filename + ".json")
  
  with open(file_path, 'w') as file:
    file.write(json_data + '\n')
  print("Export success")
  return len(objects)

class ExportColliders(bpy.types.Operator) :
  bl_idname = "scene.export_colliders"
  bl_label = "Add Tetrahedron"
  bl_options = {"UNDO"}
  
  def invoke(self, context, event):
    obj_len = generate_bbox_json("wall", "collider_export")
    self.report({"INFO"}, "Exported " + str(obj_len) + " object(s)")
    return {"FINISHED"}

class ColliderExportPanel(bpy.types.Panel):
  bl_label = "Export colliders"
  bl_space_type = "VIEW_3D"
  bl_region_type = "UI"
  bl_category = "Unity Export"

  def draw(self, context):
    layout = self.layout
    row = layout.row()
    
    column = layout.column(align = True)
    column.operator("scene.export_colliders", text = "Export colliders")
    
    
def register():
  bpy.utils.register_class(ExportColliders)
  bpy.utils.register_class(ColliderExportPanel)

register()