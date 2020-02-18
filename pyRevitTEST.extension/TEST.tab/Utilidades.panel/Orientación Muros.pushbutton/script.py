# -*- coding: utf-8 -*-
"""Writes wall orientation in "Orientation" parameter if it exists."""
#pyRevit info
__title__ = 'Wall\norientation'
__author__  = 'Carlos Romero Carballo'

import math
import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def project_to_real_north(x, y, radians):
	"""Transforms project north 2D normals into real north 2D normals, given the angle between project and real north."""
	newX = x * math.cos(radians) + y * math.sin(radians)
	newY = -x * math.sin(radians) + y * math.cos(radians)
	return round(newX, 4), round(newY, 4)

def vector_orientation (x, y):
	"""Assigns an orientation to a 2D vector according to the Spanish CTE compass rose."""
	if x <= 0.3826 and x >= -0.3826 and y <= 1 and y >= 0.9238:
		return "North"
	elif x < 0.8660 and x > 0.3826 and y < 0.9238 and y > 0.5000:
		return "Northeast"
	elif x <= 1 and x >= 0.8660 and y <= 0.5000 and y >= -0.3583:
		return "East"
	elif x < 0.9335 and x > 0.3090 and y < -0.3583 and y > -0.9510:
		return "Southeast"
	elif x <= 0.3090 and x >= -0.3090 and y <= -0.9510 and y >= -1:
		return "South"
	elif x < -0.3090 and x > -0.9335 and y < -0.3583 and y > -0.9510:
		return "Southwest"
	elif x <= -0.8660 and x >= -1 and y <= 0.5000 and y >= -0.3583:
		return "West"
	elif x < -0.3826 and x > -0.8660 and y < 0.9238 and y > 0.5000:
		return "Northwest"
	else:
		return "No orientation"

#Angle between project north and real north (in radians).
#Final -1 "undoes" real to project north transformation.
angle = doc.ActiveProjectLocation.get_ProjectPosition(XYZ(0,0,0)).Angle * -1
walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

if type(walls[0].GetParameters("Orientation")[0]) != Parameter or walls[0].GetParameters("Orientation")[0].StorageType != DB.StorageType.String:
	print("There is no Orientation parameter with text StorageType in walls, create and/or assign it to wall category.")
else:
	new_walls = list()
	ori_x = list()
	ori_y = list()
	for wall in walls:
		try:
			ori_x.append( round( wall.Orientation.Normalize().X , 4))
			ori_y.append( round( wall.Orientation.Normalize().Y , 4))
			new_walls.append(wall)
		except:
			print("Could not obtain [" + wall.Id.ToString() +"] wall orientation.")

	new_ori_x = list()
	new_ori_y = list()
	for x, y in zip(ori_x, ori_y):
		new_ori_x.append(project_to_real_north(x,y,angle)[0])
		new_ori_y.append(project_to_real_north(x,y,angle)[1])

	res = list()
	for x, y in zip (new_ori_x,new_ori_y):
		res.append(vector_orientation(x,y))

	t = Transaction(doc, "Wall Orientation")
	t.Start()
	for wall, dir in zip(new_walls,res):
		if wall.GetParameters("Orientation"):
			try:
				wall.GetParameters("Orientation")[0].Set(dir)
			except:
				print("Could not write parameter in [" + wall.Id.ToString() + "] wall.")
	t.Commit()
