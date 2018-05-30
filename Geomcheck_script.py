"""Inscribe en el parametro "MED_Net vertical finish room area" de todas las habitaciones del modelo el area neta de acabados verticales."""
"""Se cruzan las caras verticales de la geometria de la habitacion con las caras verticales de los muros que forman sus boundaries. No funciona para habitaciones para las que Revit no puede crear geometria."""

__title__ = 'Room Geometry\nCheck'
__author__ = 'Carlos Romero'

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory
import Autodesk.Revit.DB as DB
import clr

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

rooms = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

flag = False

for e in rooms:
        try:
            a = e.Geometry
        except:
            print ("No geometry in room number " + str(e.Number))
            flag = True

if not flag:
        print ("All model rooms have geometry.")
#for timing
endtime ="It took me " + str(timer.get_time()) + " seconds to calculate this."
print(endtime)
