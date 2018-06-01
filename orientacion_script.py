"""Inscribe en el parametro "ORIENTACION" la orientacion de la normal de los muros"""

__title__ = 'Orientacion\nde Muros'
__author__  = 'Carlos Romero'

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

import math
import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#funciones
#funcion para transformar los vectores de los muros (que apuntan a norte de proyecto) a norte real.
def project_to_real_north(x, y, radians):
	newX = x * math.cos(radians) + y * math.sin(radians)
	newY = -x * math.sin(radians) + y * math.cos(radians)
	return round(newX, 4), round(newY, 4)
#funcion para asignarle una orientacion al vector
def ori (x, y):
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
		return "Sin orientacion"

#Angulo entre Norte de proyecto y Norte real (en radianes).
#el -1 del final "deshace" la transformacion de real a proyecto
angle = doc.ActiveProjectLocation.get_ProjectPosition(XYZ(0,0,0)).Angle * -1
walls = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
new_walls = []
ori_x = []
ori_y = []
print("Muros en el modelo: " + str(len(walls)))

for wall in walls:
	try:
		ori_x.append( round( wall.Orientation.Normalize().X , 4))
		ori_y.append( round( wall.Orientation.Normalize().Y , 4))
		new_walls.append(wall)
	except:
		print("No ha podido sacar la orientacion de uno de los muros.")

print("Muros con orientacion: " + str(len(new_walls)))

#transformamos las normales
new_ori_x = list()
new_ori_y = list()

for x, y in zip(ori_x, ori_y):
	new_ori_x.append(project_to_real_north(x,y,angle)[0])
	new_ori_y.append(project_to_real_north(x,y,angle)[1])

res = []
for x, y in zip (new_ori_x,new_ori_y):
	res.append(ori(x,y))

t = Transaction(doc, "Orientacion Muros")
t.Start()

for wall, dir in zip(new_walls,res):
	if wall.LookupParameter("Orientacion"):
		try:
			wall.LookupParameter("Orientacion").Set(dir)
		except:
			print("No se puede escribir en el parametro de uno de los muros.")


t.Commit()


#for timing
endtime ="He tardado: " + str(timer.get_time()) + " segundos."
print(endtime)
