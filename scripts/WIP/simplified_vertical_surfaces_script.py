# coding: utf8
"""Inscribe la superficie neta de acabado vertical de las habitaciones, y la longitud de los rodapiés.\
 Son necesarios 2 parámetros instancia de habitación en el proyecto: MED_Área neta de superficie vertical (Área)\
 y MED_Rodapié (Longitud), y un parámetro de tipo de muro: MED_Excluido (Sí/No), que indica si el muro tiene acabado."""

#pyRevit info
__title__ = 'Medición Simplificada\nAcabados de Paredes'
__author__  = 'Carlos Romero Carballo'

from pyrevit.coreutils import Timer
timer = Timer()

import Autodesk.Revit
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#Phases (DE MOMENTO COGE 'NEW CONSTRUCTION' o 'NUEVA CONSTRUCCIÓN', AÑADIR SELECTOR)
for ph in doc.Phases:
    if ph.Name == 'New Construction' or ph.Name == 'Nueva construcción':
        phase = ph
        break

fec_doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
fec_windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
doors = [element for element in fec_doors if element != None]
windows = [element for element in fec_windows if element != None]

class paquetito:
    def __init__(self, instance):
        self.obj = instance
        self.id = instance.Id
        self.toroom = instance.ToRoom[phase].Id if instance.ToRoom[phase] != None else 0
        self.fromroom = instance.FromRoom[phase].Id if instance.FromRoom[phase] != None else 0
        self.width = doc.GetElement(instance.GetTypeId()).LookupParameter("Width").AsDouble() if not instance.LookupParameter("Width") else instance.LookupParameter("Width").AsDouble()
        self.height = doc.GetElement(instance.GetTypeId()).LookupParameter("Height").AsDouble() if not instance.LookupParameter("Height") else instance.LookupParameter("Height").AsDouble()
        self.hostid = instance.Host.Id if instance.Host != None else 0


#Ignoramos las puertas y ventanas en muros excluidos (para no restarlos de la medición)
door_matrix = [paquetito(door) for door in doors if doc.GetElement(door.Host.GetTypeId()).GetParameters("MED_Excluido")[0].AsInteger() == 0]
window_matrix = [paquetito(window) for window in windows if doc.GetElement(window.Host.GetTypeId()).GetParameters("MED_Excluido")[0].AsInteger() == 0]

#excluded e hydro (ambos parámetros de tipo)
fec_walls = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
excluded = list()
for tipo in fec_walls:
    if tipo.LookupParameter("MED_Excluido").AsInteger() == 1:
        excluded.append(tipo.LookupParameter("Type Name").AsString())

def FeetToMeters(length):
        return round(length * 0.3048, 2)
def SqFeetToSqMeters(area):
        return round(area * 0.09290304, 2)

def RoomCalc(room, excluded):
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
    height = room.Volume / room.Area
    # get relevant walls
    relevant_walls_and_curves = list()
    for line in elements_and_curves:
        if line[0].Category.Name == 'Walls':
            if line[0].Name not in excluded and line[0].WallType.FamilyName != 'Curtain Wall' if line[0].ToString() != 'Autodesk.Revit.DB.FamilyInstance' else False:
                relevant_walls_and_curves.append(line + [line[0].Id])
    # now we have [ element, curve, id ]
    # add area of wall hosted doors and windows from or to that room
    final_walls = list()
    for wall in relevant_walls_and_curves:
        opening_area = 0
        skirting_cut = 0
        for door in door_matrix:
            if door.hostid == wall[2]:
                if door.toroom == room.Id or door.fromroom == room.Id:
                    opening_area += (door.width*door.height)
                    skirting_cut += door.width
        for window in window_matrix:
            if window.hostid == wall[2]:
                if window.toroom == room.Id or window.fromroom == room.Id:
                    opening_area += (window.width*window.height)
        final_walls.append(wall + [opening_area, skirting_cut])
    # now we have [ element, curve, id, opening_area, skirting_cut ]
    # LOS PANELES HIDROFUGADOS VAN HASTA EL TECHO, EL ACABADO NO
    # RESTA LA VENTANA ENTERA DE DONDE TENGA EL RCP, Y DEL MURO DONDE ESTÉ HOSTEADA
    vert_area = 0
    skirt_len = 0
    for wall in final_walls:
        vert_area += (wall[1].Length * height) - wall[3]
        skirt_len += wall[1].Length - wall[4]
    return room, SqFeetToSqMeters(vert_area), FeetToMeters(skirt_len)

data = list()
for room in FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
    data.append(RoomCalc(room,excluded))
t = Transaction(doc,"Cálculo Áreas Habitaciones")
t.Start()
for line in data:
    print("Habitación" + line[0].LookupParameter("Number").AsString() + " - " + line[0].LookupParameter("Name").AsString() + ": MED_VERT " + str(line[1]) + " m2, MED_ROD " + str(line[2]) + " m." )
    line[0].LookupParameter("MED_Área neta de superficie vertical").SetValueString(str(line[1])+" m²")
    line[0].LookupParameter("MED_Rodapié").SetValueString(str(line[2])+" m")
t.Commit()

# COMPROBAR QUE EL PARÁMETRO EXISTE, ETC

#REPORT TIME
endtime ="\nHe tardado " + str(timer.get_time())[:3] + " segundos en llevar a cabo esta tarea."
print(endtime)
