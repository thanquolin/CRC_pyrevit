"""Inscribe en el parametro "ORIENTACION" la orientacion de la normal de los muros"""

__title__ = 'Orientacion\nde Muros'
__author__  = 'Carlos Romero'

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory
import Autodesk.Revit.DB as DB
import clr

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

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
res = []
for x, y in zip (ori_x,ori_y):
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
