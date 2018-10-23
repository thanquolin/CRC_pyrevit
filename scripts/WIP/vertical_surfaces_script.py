# coding: utf8
"""Inscribe la superficie neta de acabado vertical de las habitaciones, la parte de esa superficie perteneciente a tabiques de pladur, y la longitud de los rodapiés.\
 Son necesarios 4 parámetros instancia de habitación en el proyecto: MED_Área neta de superficie vertical (Área), MED_Área vertical hidrofugada (Área),\
 MED_Rodapié (Longitud), MED_Cuarto húmedo (Sí/No), y 2 parámetros de tipo de muro: MED_Excluido (Sí/No), MED_Hidrofugado (Sí/No),\
 que indican si el muro tiene acabado y si el tipo de muro va hidrofugado cuando da a un cuarto húmedo, respectivamente."""

#pyRevit info
__title__ = 'Medición Acabados\nde Paredes'
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
        self.hydro = doc.GetElement(instance.Host.GetTypeId()).GetParameters("MED_Hidrofugado")[0].AsInteger() == 1


#Ignoramos las puertas y ventanas en muros excluidos (para no restarlos de la medición)
door_matrix = [paquetito(door) for door in doors if doc.GetElement(door.Host.GetTypeId()).GetParameters("MED_Excluido")[0].AsInteger() == 0]
window_matrix = [paquetito(window) for window in windows if doc.GetElement(window.Host.GetTypeId()).GetParameters("MED_Excluido")[0].AsInteger() == 0]

#excluded e hydro (ambos parámetros de tipo)
fec_walls = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
hydro = list()
excluded = list()
for tipo in fec_walls:
    if tipo.LookupParameter("MED_Hidrofugado").AsInteger() == 1:
        hydro.append(tipo.LookupParameter("Type Name").AsString())
    if tipo.LookupParameter("MED_Excluido").AsInteger() == 1:
        excluded.append(tipo.LookupParameter("Type Name").AsString())

def FeetToMeters(length):
        return round(length * 0.3048, 3)
def SqFeetToSqMeters(area):
        return round(area * 0.09290304, 3)

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
    height = room.Volume / room.Area
    # get relevant walls
    relevant_walls_and_curves = list()
    for line in elements_and_curves:
        if line[0].Category.Name == 'Walls':
            if line[0].Name not in excluded and line[0].WallType.FamilyName != 'Curtain Wall' if line[0].ToString() != 'Autodesk.Revit.DB.FamilyInstance' else False:
                relevant_walls_and_curves.append(line + [line[0].Name in hydro, line[0].Id])
    # now we have [ element, curve, hydro, id ]
    # add area of wall hosted doors and windows from or to that room
    final_walls = list()
    for wall in relevant_walls_and_curves:
        opening_area = 0
        hydro_opening_area = 0
        skirting_cut = 0
        for door in door_matrix:
            if door.hostid == wall[3]:
                if door.toroom == room.Id or door.fromroom == room.Id:
                    opening_area += (door.width*door.height)
                    skirting_cut += door.width
                    if room.GetParameters("MED_Cuarto húmedo")[0].AsInteger() == 1 and wall[2]:
                        hydro_opening_area += (door.width*door.height)
        for window in window_matrix:
            if window.hostid == wall[3]:
                if window.toroom == room.Id or window.fromroom == room.Id:
                    opening_area += (window.width*window.height)
                    if room.GetParameters("MED_Cuarto húmedo")[0].AsInteger() == 1 and wall[2]:
                        hydro_opening_area += (window.width*window.height)
        final_walls.append(wall + [opening_area, skirting_cut, hydro_opening_area])
    # now we have [ element, curve, hydro, id, opening_area, skirting_cut, hydro_opening_area ]
    # LOS PANELES HIDROFUGADOS VAN HASTA EL TECHO, EL ACABADO NO
    vert_area = 0
    hydro_area = 0
    skirt_len = 0
    for wall in final_walls:
        vert_area += (wall[1].Length * height) - wall[4]
        skirt_len += wall[1].Length - wall[5]
        if wall[2] == True:
            hydro_area += (wall[1].Length * height) - wall[6]
    return room, SqFeetToSqMeters(vert_area), SqFeetToSqMeters(hydro_area) if room.GetParameters("MED_Cuarto húmedo")[0].AsInteger() == 1 else 0, FeetToMeters(skirt_len)

data = list()
for room in FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
    data.append(RoomCalc(room,excluded,hydro))
t = Transaction(doc,"Cálculo Áreas Habitaciones")
t.Start()
for line in data:
    print("Habitación" + line[0].LookupParameter("Number").AsString() + " - " + line[0].LookupParameter("Name").AsString() + ": MED_VERT " + str(line[1]) + " m2, MED_HYDRO " + str(line[2]) + " m2, MED_ROD " + str(line[3]) + " m." )
    line[0].LookupParameter("MED_Área neta de superficie vertical").SetValueString(str(line[1])+" m²")
    line[0].LookupParameter("MED_Área vertical hidrofugada").SetValueString(str(line[2])+" m²")
    line[0].LookupParameter("MED_Rodapié").SetValueString(str(line[3])+" m")
t.Commit()

# COMPROBAR QUE EL PARÁMETRO EXISTE, ETC
# AÑADIR LA MEDICIÓN DE HYDRO POR TIPO DE MURO

#REPORT TIME
endtime ="\nHe tardado " + str(timer.get_time())[:3] + " segundos en llevar a cabo esta tarea."
print(endtime)
