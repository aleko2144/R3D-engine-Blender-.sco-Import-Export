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
	
def LoadFromSCO_Object(file, context, op, filepath):
	sco_lines = file.readlines()
	
	name = ''
	central_point = [0.0, 0.0, 0.0]
	num_verts = 0
	num_faces = 0
	verts_data = []
	faces_data = []
	faces_uv = []
	mats_data = []
	
	faces_all_data = []
	
	used_materials_list = []
	
	iter = 0
	while(True):
		test_str_strip = sco_lines[iter].strip()
		iter += 1
		
		if (test_str_strip[:4] == "Name"):
			name = test_str_strip.split(sep = '=')[1].strip()
		elif (test_str_strip[:12] == "CentralPoint"):
			temp_vector = test_str_strip.split(sep = '=')[1].strip().split(sep = ' ')
			central_point[0] = float(temp_vector[0])
			central_point[1] = float(temp_vector[1])
			central_point[2] = float(temp_vector[2])
		elif (test_str_strip[:5] == "Verts"):
			num_verts = int(test_str_strip.split(sep = '=')[1].strip())
			break
	
	for i in range(num_verts):
		test_str_strip = sco_lines[i + iter].strip()
		temp_vector = test_str_strip.strip().split(sep = ' ')
		verts_data.append((float(temp_vector[0]), float(temp_vector[1]), float(temp_vector[2])))
		
	iter += num_verts
	
	num_faces = int(sco_lines[iter].strip().split(sep = '=')[1].strip())
	iter += 1
	
	for i in range(num_faces):
		test_str_strip = sco_lines[i + iter].strip()

		temp_data = test_str_strip.strip().split()
		#print(temp_data)
			
		temp_face = []
		temp_uv = []
		uv_offset = 0
		for k in range(int(temp_data[0])):
			temp_face.append(int(temp_data[k + 1]))
			temp_uv.append([float(temp_data[k + uv_offset + 5]), 1 - float(temp_data[k + uv_offset + 6])])
			uv_offset += 1
			
		faces_data.append((temp_face))
						  
		mats_data.append(temp_data[4])
		
		if not (temp_data[4] in bpy.data.materials):
			bpy.data.materials.new(temp_data[4])
			
		if not (temp_data[4] in used_materials_list):
			used_materials_list.append(temp_data[4])
		
		faces_uv.append(temp_uv)
		
		faces_all_data.append(temp_data)
		
	scoMesh = (bpy.data.meshes.new(name))
	scoObj = bpy.data.objects.new(name, scoMesh)
	
	#print(used_materials_list)
	
	for i in range(len(used_materials_list)):
		scoObj.data.materials.append(bpy.data.materials[used_materials_list[i]])
		
	Ev = threading.Event()
	Tr = threading.Thread(target=scoMesh.from_pydata, args = (verts_data, [], faces_data))
	Tr.start()
	Ev.set()
	Tr.join()
				
	context.scene.collection.objects.link(scoObj)

	bm = bmesh.new()
	bm.from_mesh(scoMesh)
	uv_layer = bm.loops.layers.uv.verify()
				
	#https://blender.stackexchange.com/questions/185496/how-to-unwrap-a-mesh-from-view-in-python-blender-2-8

	i = 0
	
	for face in bm.faces:
		k = 0
		
		face.material_index = used_materials_list.index(mats_data[i])
		
		for loop in face.loops:
			loop_uv = loop[uv_layer]
			loop_uv.uv = faces_uv[i][k]
			
			#i - face index
			#k - vert num (not index)
			#print('i={}, k={}'.format(i, k))
			k += 1
		i += 1
		
		face.smooth = True
		
	scoObj.location.x = central_point[0]
	scoObj.location.y = central_point[2]
	scoObj.location.z = central_point[1]
	
	for v in bm.verts:
		v.co.x -= scoObj.location.x
		v.co.y -= scoObj.location.y
		v.co.z -= scoObj.location.z

	bm.to_mesh(scoMesh)
	scoMesh.update()

def read(file, context, op, filepath):
	LoadFromSCO_Object(file, context, op, filepath)
