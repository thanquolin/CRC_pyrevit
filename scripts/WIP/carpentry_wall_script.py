# coding: utf8
"""Crea un muro con cada tipo de puerta y ventana en el proyecto en él, todo creado en la primera fase del proyecto y demolido en la segunda."""

#pyRevit info
__title__ = 'Muro\nCarpinterías'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
import Autodesk.Revit.UI
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
language = uidoc.Application.Application.Language

creation_phase = doc.Phases[0]
demolition_phase = doc.Phases[1]

def m_to_feet(m):
    return m / 0.3048

#Nearest level to Elevation 0
levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
level_dic = {round(level.Elevation,3):level for level in levels}
level = level_dic[min([abs(val) for val in level_dic.keys()])]

#Lenguaje
def par_get(parameter):
    idx = 0 if language == Autodesk.Revit.ApplicationServices.LanguageType.English_USA else 1
    parameters = {"Width":["Width","Anchura"], "Height":["Height","Altura"], "Family Name":["Family Name","Nombre de familia"], "Section":["Section","Sección"], "Type Name":["Type Name","Nombre de tipo"], "View Name":["View Name","Nombre de vista"]  }
    return parameters[parameter][idx]

# Lista del primer ejemplar de cada tipo de carpintería
def instance_collector(category):
    return FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()

cat_doors = Autodesk.Revit.DB.BuiltInCategory.OST_Doors
cat_windows = Autodesk.Revit.DB.BuiltInCategory.OST_Windows
all_doors = instance_collector(cat_doors)
all_windows = instance_collector(cat_windows)

door_types_ex = list()
door_type_ids = list()
for door in all_doors:
    if door.GetTypeId() not in door_type_ids:
        door_types_ex.append(door)
        door_type_ids.append(door.GetTypeId())
window_types_ex = list()
window_type_ids = list()
for window in all_windows:
    if window.GetTypeId() not in window_type_ids:
        window_types_ex.append(window)
        window_type_ids.append(window.GetTypeId())

carp_list = door_types_ex + window_types_ex

point = uidoc.Selection.PickPoint()

levelid = FilteredElementCollector(doc).OfClass(Level).ToElements()[0].Id
curve = Line.CreateBound(XYZ(point.X, point.Y, level.Elevation), XYZ(point.X + m_to_feet(2 * len(carp_list)), point.Y, level.Elevation))
walltype = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()[0]
wall_height = m_to_feet(4)
t = Transaction(doc,"Wall")
t.Start()
wall = Wall.Create(doc,curve,walltype.Id,level.Id,wall_height,0.0,False,False)
wall.CreatedPhaseId = creation_phase.Id
wall.DemolishedPhaseId = demolition_phase.Id

column = point.X + m_to_feet(1)
for carp in carp_list:
    sill_height = carp.GetParameters("Sill Height")[0].AsDouble() if carp.Category.Name == "Windows" else 0
    point = XYZ(column, 0,sill_height)
    type = doc.GetElement(carp.GetTypeId())
    host = wall
    inst = doc.Create.NewFamilyInstance(point, type, host, level, Autodesk.Revit.DB.Structure.StructuralType.NonStructural)
    inst.CreatedPhaseId = creation_phase.Id
    inst.DemolishedPhaseId = demolition_phase.Id
    column += m_to_feet(2)
t.Commit()
