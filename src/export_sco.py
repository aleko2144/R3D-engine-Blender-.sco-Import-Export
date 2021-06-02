import struct
import sys
import timeit
import threading
import pdb

import bpy
import mathutils
import os.path
from bpy.props import *
from bpy_extras.image_utils import load_image
from ast import literal_eval as make_tuple

from math import sqrt
from math import atan2

import re

import bmesh
	
def SaveAsSCO_Object(file, context, op, filepath, object):
	bm = bmesh.new()
	bm.from_mesh(object.data)
	uv_layer = bm.loops.layers.uv.verify()
	
	bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
	
	file.write('[ObjectBegin]\n')
	file.write('name= {}\n'.format(object.name))
	file.write('CentralPoint= {} {} {}\n'.format(object.location.x, object.location.z, object.location.y))
	file.write('Verts= {}\n'.format(len(bm.verts)))
	
	for v in bm.verts:
		v.co.x += object.location.x
		v.co.y += object.location.y
		v.co.z += object.location.z
		
		file.write('{} {} {}\n'.format(v.co.x, v.co.z, v.co.y))
		
	file.write('Faces= {}\n'.format(len(bm.faces)))
	
	for face in bm.faces:
		face.normal_flip()
		file.write('{} '.format(len(face.loops)))
		
		for loop in face.loops:
			index_str = str(loop.vert.index)
			#file.write(' ' * (6 - len(index_str)))
			file.write('{} '.format(loop.vert.index))
		
		file.write('{}          	'.format(object.data.materials[face.material_index].name))
		
		for loop in face.loops:
			loop_uv = loop[uv_layer]
			file.write('{} '.format(loop_uv.uv[0]))
			file.write('{} '.format(1 - loop_uv.uv[1]))
	
		file.write('\n')
		
	bm.free()
		
	file.write('[ObjectEnd]\n')

def SaveAsSCO_Materials(filepath):
	file = open(filepath + 'materials.mat','w')
	for material in bpy.data.materials:
		file.write('[MaterialBegin]\n')
		file.write('Name= {}\n'.format(material.name))
		file.write('Flags= texture_gouraud_envmap\n')
		file.write('Opacity= 255\n')	
		file.write('Texture= {}.bmp\n'.format(material.name))
		file.write('EnvMap= water.dds\n')
		file.write('EnvPower= 20\n')
		file.write('Color24= 255 255 255\n')
		file.write('[MaterialEnd]\n')
		file.write('\n')
	file.close()

def write(context, op, filepath):
	for i in range(len(bpy.context.selected_objects)):
		object = bpy.context.selected_objects[i]
		if object.type == 'MESH':
			scoFile = open(filepath + object.name +'.sco','w')
			SaveAsSCO_Object(scoFile, context, op, filepath, object)
			scoFile.close()
			
	SaveAsSCO_Materials(filepath)
