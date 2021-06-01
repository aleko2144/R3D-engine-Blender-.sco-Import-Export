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

bl_info = {
    'name': 'R3D engine SCO format',
    'author': 'Andrey Prozhoga',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'api': 34893,
    'description': 'Import-Export SCO meshes',
    'warning': '',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/'\
        'Import-Export/M3_Import',
    'tracker_url': 'vk.com/rnr_mods',
    'category': 'Import-Export'}

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    import imp
    if 'import_sco' in locals():
        imp.reload(import_sco)
#   if 'export_m3' in locals():
#       imp.reload(export_sco)

import time
import datetime
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportSCO(bpy.types.Operator, ImportHelper):
    '''Import from sco file format (.sco)'''
    bl_idname = 'import_scene.r3d_sco'
    bl_label = 'Import sco'

    filename_ext = '.sco'
    filter_glob: StringProperty(default='*.sco', options={'HIDDEN'})

    def execute(self, context):
        from . import import_sco
        print('Importing file', self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(self.filepath, 'r') as file:
            import_sco.read(file, context, self, self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')
        return {'FINISHED'}
		
class ExportSCO(bpy.types.Operator, ImportHelper):
    '''Export to sco file format (.sco)'''
    bl_idname = 'export_scene.r3d_sco'
    bl_label = 'Export sco'

    filename_ext = '.sco'
    filter_glob: StringProperty(default='*.sco', options={'HIDDEN'})

    generate_pro_file: BoolProperty(name='Generate pro-file',
                        description='Generate .pro file, which can usedto assembly the resources file', default=False)
									
    textures_path: StringProperty(
        name="Textures directory",
        default="txr\\",
        )

    def execute(self, context):
        from . import export_sco
        print('Exporting file', self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        export_sco.write(self.filepath+'.sco', context, self, self.filepath, self.generate_pro_file, self.textures_path)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished exporting in', t, 'seconds')
        return {'FINISHED'}

		
def menu_func_import(self, context):
    self.layout.operator(ImportSCO.bl_idname, text='R3D (.sco)')


def menu_func_export(self, context):
   self.layout.operator(ExportSCO.bl_idname, text='R3D (.sco)')

classes = (
    ImportSCO,
    ExportSCO,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register() 
