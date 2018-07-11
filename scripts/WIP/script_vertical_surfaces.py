# coding: utf8
"""Inscribe la superficie neta de acabado vertical de las habitaciones, la parte de esa superficie perteneciente a tabiques de pladur, y la longitud de los rodapiés.\
 Son necesarios 4 parámetros instancia de habitación en el proyecto: MED_Área neta de superficie vertical (Área), MED_Área vertical hidrofugada (Área),\
 MED_Rodapié (Longitud), MED_Cuarto húmedo (Sí/No), y 2 parámetros de tipo de muro: MED_Excluido (Sí/No), MED_Hidrofugado (Sí/No),\
 que indican si el muro tiene acabado y si el tipo de muro va hidrofugado cuando da a un cuarto húmedo, respectivamente."""

#TO DO: Crear excluded e hydro a partir de los elementos del modelo. Comprobar que existen todos los parámetros y responden a los tipos requeridos.

#pyRevit info
__title__ = 'Medición Acabados\nde Paredes'
__author__  = 'Carlos Romero Carballo'

#IMPORTS
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

from pyrevit.coreutils import Timer
timer = Timer()

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
import Autodesk

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)

#VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
fec_doors = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
fec_windows = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
doors = [element for element in fec_doors if element != None]
windows = [element for element in fec_windows if element != None]

def FeetToMeters(length):
        return round(length * 0.3048, 3)
def SqFeetToSqMeters(area):
        return round(area * 0.09290304, 3)
#excluded e hydro (ambos parámetros de tipo)
fec_walls = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
hydro = list()
excluded = list()
for tipo in fec_walls:
    if tipo.LookupParameter("MED_Hidrofugado").AsInteger() == 1:
        hydro.append(tipo.LookupParameter("Type Name").AsString())
    if tipo.LookupParameter("MED_Excluido").AsInteger() == 1:
        excluded.append(tipo.LookupParameter("Type Name").AsString())

#Phases (DE MOMENTO COGE 'NEW CONSTRUCTION' o 'NUEVA CONSTRUCCIÓN', AÑADIR SELECTOR)
for ph in doc.Phases:
    if ph.Name == 'New Construction' or ph.Name == 'Nueva construcción':
        phase = ph
        break
#door element, id, fromRoom (id), toRoom (id), Width, height, wall (id)
door_matrix = [[door, door.Id, door.ToRoom[phase].Id if door.ToRoom[phase] != None else 0, door.FromRoom[phase].Id if door.FromRoom[phase] != None else 0,
FeetToMeters(doc.GetElement(door.GetTypeId()).LookupParameter("Width").AsDouble()) if not door.LookupParameter("Width") else FeetToMeters(door.LookupParameter("Width").AsDouble()),\
FeetToMeters(doc.GetElement(door.GetTypeId()).LookupParameter("Height").AsDouble()) if not door.LookupParameter("Height") else FeetToMeters(door.LookupParameter("Height").AsDouble()),\
door.Host.Id if door.Host != None else 0]\
for door in doors]

window_matrix = [[window, window.Id, window.ToRoom[phase].Id if window.ToRoom[phase] != None else 0, window.FromRoom[phase].Id if window.FromRoom[phase] != None else 0,\
FeetToMeters(doc.GetElement(window.GetTypeId()).LookupParameter("Width").AsDouble()) if not window.LookupParameter("Width") else FeetToMeters(window.LookupParameter("Width").AsDouble()),\
FeetToMeters(doc.GetElement(window.GetTypeId()).LookupParameter("Height").AsDouble()) if not window.LookupParameter("Height") else FeetToMeters(window.LookupParameter("Height").AsDouble()),\
window.Host.Id if window.Host != None else 0]\
for window in windows]

#FUNCTIONS

def RoomCalc(room, excluded, hydro):
    """excluded and hydro are lists of wall type names"""
    calculator = SpatialElementGeometryCalculator(doc)
    options = Autodesk.Revit.DB.SpatialElementBoundaryOptions()
    # get boundary location from area computation settings
    boundloc = Autodesk.Revit.DB.AreaVolumeSettings.GetAreaVolumeSettings(doc).GetSpatialElementBoundaryLocation(SpatialElementType.Room)
    options.SpatialElementBoundaryLocation = boundloc
    # get boundary elements and segments
    elements_and_curves = list()
    #NotImplementedError: Method 'Approximate' in type 'Autodesk.LibG.CurveHost' from assembly 'LibG.ProtoInterface, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null' does not have an implementation.
    for boundarylist in room.GetBoundarySegments(options):
        for boundary in boundarylist:
            temp = list()
            if doc.GetElement(boundary.ElementId) != None:
                temp.append(doc.GetElement(boundary.ElementId))
                temp.append(boundary.GetCurve())
                elements_and_curves.append(temp)
    # get room height
    height = FeetToMeters(room.Volume / room.Area)
    # get relevant walls
    relevant_walls_and_curves = list()
    for line in elements_and_curves:
        if line[0].Category.Name == 'Walls':
            if line[0].Name not in excluded and line[0].WallType.FamilyName != 'Curtain Wall' if line[0].ToString() != 'Autodesk.Revit.DB.FamilyInstance' else False:
                relevant_walls_and_curves.append(line + [line[0].Name in hydro] + [line[0].Id])
    # now we have [ element, curve, hydro, id ]
    # add area of wall hosted doors and windows from or to that room
    final_walls = list()
    for wall in relevant_walls_and_curves:
        opening_area = 0
        skirting_length = 0
        for door in door_matrix:
            if door[6] == wall[3]:
                if door[3] == room.Id or door[4] == room.Id:
                    opening_area += (door[4]*door[5])
                    skirting_length += door[4]
        for window in window_matrix:
            if window[6] == wall[3]:
                if window[3] == room.Id or window[4] == room.Id:
                    opening_area += (window[4]*window[5])
        final_walls.append(wall + [opening_area] + [skirting_length])
    # now we have [ element, curve, hydro, id, opening_area, skirting_length ]
    vert_area = 0
    hydro_area = 0
    skirt_len = 0
    for wall in final_walls:
        vert_area += ((FeetToMeters(wall[1].Length) * height) - wall[4])
        skirt_len += FeetToMeters(wall[1].Length - wall[5])
        if wall[2] == True:
            hydro_area += ((FeetToMeters(wall[1].Length) * height) - wall[4])
    return room, vert_area, hydro_area, skirt_len

data = list()
for room in FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
    data.append(RoomCalc(room,excluded,hydro))
t = Transaction(doc,"Cálculo Áreas Habitaciones")
t.Start()
for line in data:
    print("Habitación" + line[0].LookupParameter("Number").AsString() + " - " + line[0].LookupParameter("Name").AsString() + ": MED_VERT " + str(line[1]) + " m2, MED_HYDRO " + str(line[2]) + " m2, MED_ROD " + str(line[3]) + " m." )
    line[0].LookupParameter("MED_Área neta de superficie vertical").Set(line[1])
    line[0].LookupParameter("MED_Área vertical hidrofugada").Set(line[2])
    line[0].LookupParameter("MED_Rodapié").Set(line[3])
t.Commit()

# COMPROBAR QUE EL PARÁMETRO EXISTE, ETC

#REPORT TIME
endtime ="\nHe tardado " + str(timer.get_time()) + " segundos en llevar a cabo esta tarea."
print(endtime)
