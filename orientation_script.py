"""Writes wall orientation in "ORIENTATION" wall parameter if it exists."""
#pyRevit info
__title__ = 'Wall\norientation'
__author__  = 'Carlos Romero Carballo'


#IMPORTS

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

#for the script to work
import math
import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

#FUNCTIONS

#function that transforms project north 2D normals into real north 2D normals, given the angle between project and real north.
def project_to_real_north(x, y, radians):
	newX = x * math.cos(radians) + y * math.sin(radians)
	newY = -x * math.sin(radians) + y * math.cos(radians)
	return round(newX, 4), round(newY, 4)

#function that assigns an orientation to a 2D vector according to the Spanish CTE compass rose.
def vector_orientation (x, y):
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


#VARIABLES

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#Angle between project north and real north (in radians).
#final -1 "undoes" real to project north transformation.
angle = doc.ActiveProjectLocation.get_ProjectPosition(XYZ(0,0,0)).Angle * -1
walls = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
new_walls = []
ori_x = []
ori_y = []
print("Walls in model: " + str(len(walls)))



#DATA PROCESSING

if type(walls[0].LookupParameter("ORIENTATION")) != Parameter or walls[0].LookupParameter("ORIENTATION").StorageType != DB.StorageType.String:
	print("There is no ORIENTATION parameter with text StorageType in walls, create and/or assign it to wall category.")
else:
	#initial wall normals.
	for wall in walls:
		try:
			ori_x.append( round( wall.Orientation.Normalize().X , 4))
			ori_y.append( round( wall.Orientation.Normalize().Y , 4))
			new_walls.append(wall)
		except:
			print("Could not obtain wall orientation.")
	print("Walls with orientation: " + str(len(new_walls)))

	#normal transform (project to real north).
	new_ori_x = list()
	new_ori_y = list()
	for x, y in zip(ori_x, ori_y):
		new_ori_x.append(project_to_real_north(x,y,angle)[0])
		new_ori_y.append(project_to_real_north(x,y,angle)[1])

	#final vector orientation assignment.
	res = []
	for x, y in zip (new_ori_x,new_ori_y):
		res.append(vector_orientation(x,y))


	#DB WRITE

	#transaction to write into DB.
	t = Transaction(doc, "Wall Orientation")
	t.Start()
	for wall, dir in zip(new_walls,res):
		if wall.LookupParameter("ORIENTATION"):
			try:
				wall.LookupParameter("ORIENTATION").Set(dir)
			except:
				print("Could not write parameter in one of the walls.")
	t.Commit()

	#report time
	endtime ="It took me: " + str(timer.get_time()) + " seconds to perform this task."
	print(endtime)
