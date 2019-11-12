#coding: utf8
"""Inscribe la superficie neta de acabado vertical de las habitaciones, la parte de esa superficie perteneciente a tabiques de pladur, y la longitud de los rodapiés.\
 Son necesarios 4 parámetros instancia de habitación en el proyecto: MED_Área neta de superficie vertical (Área), MED_Área vertical hidrofugada (Área),\
 MED_Rodapié (Longitud), MED_Cuarto húmedo (Sí/No), y 2 parámetros de tipo de muro: MED_Excluido (Sí/No), MED_Hidrofugado (Sí/No),\
 que indican si el muro tiene acabado y si el tipo de muro va hidrofugado cuando da a un cuarto húmedo, respectivamente."""

#pyRevit info
__title__ = 'Medición Acabados\ncon Clases'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
import Autodesk.Revit
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
dbDoorCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Doors
dbWindowCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Windows
dbWallCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Walls

hydroPar = "MED_Hidrofugado"
excludedPar = "MED_Excluido"
supPar = "MED_Área neta de superficie vertical"
supHydroPar = "MED_Área vertical hidrofugada"
rodPar = "MED_Rodapié"

for ph in doc.Phases:
    if ph.Name == 'New Construction' or ph.Name == 'Nueva construcción':
        phase = ph
        break

def FeetToMeters(length):
        return round(length * 0.3048, 3)
def SqFeetToSqMeters(area):
        return round(area * 0.09290304, 3)

def DBGetElements(doc, categ):
    return  FilteredElementCollector(doc).OfCategory(categ).WhereElementIsNotElementType().ToElements()

class MEDFam():
    def __init__(self, dbElement):
        self.dbElement = dbElement
        self.id = dbElement.Id
        self.toRoomId = dbElement.ToRoom[phase].Id if dbElement.ToRoom[phase] != None else Autodesk.Revit.DB.ElementId.InvalidElementId
        self.fromRoomId = dbElement.FromRoom[phase].Id if dbElement.FromRoom[phase] != None else Autodesk.Revit.DB.ElementId.InvalidElementId
        self.width = doc.GetElement(dbElement.GetTypeId()).LookupParameter("Width").AsDouble() if not dbElement.LookupParameter("Width") else dbElement.LookupParameter("Width").AsDouble()
        self.height = doc.GetElement(dbElement.GetTypeId()).LookupParameter("Height").AsDouble() if not dbElement.LookupParameter("Height") else dbElement.LookupParameter("Height").AsDouble()
        self.hostId = dbElement.Host.Id if dbElement.Host != None else Autodesk.Revit.DB.ElementId.InvalidElementId

class MEDDoor(MEDFam):
    def isDoor(self):
        return True
class MEDWindow(MEDFam):
    def isWindow(self):
        return True

class MEDWallTypes():
    def __init__(self, dbElement):
        self.dbElement = dbElement
        self.id = dbElement.Id
        self.hydro = True if dbElement.LookupParameter(hydroPar).AsInteger() == 1 else False
        self.excluded = True if dbElement.LookupParameter(excludedPar).AsInteger() == 1 else False

dbDoors = [MEDDoor(element) for element in DBGetElements(doc,dbDoorCategory) if element != None]
dbWindows = [MEDWindow(element) for element in DBGetElements(doc,dbWindowCategory) if element != None]
dbWallTypes = [MEDWallTypes(element) for element in FilteredElementCollector(doc).OfCategory(dbWallCategory).WhereElementIsElementType().ToElements()]


#Configuración para Cálculo
calculator = SpatialElementGeometryCalculator(doc)
options = Autodesk.Revit.DB.SpatialElementBoundaryOptions()
boundloc = Autodesk.Revit.DB.AreaVolumeSettings.GetAreaVolumeSettings(doc).GetSpatialElementBoundaryLocation(SpatialElementType.Room)
options.SpatialElementBoundaryLocation = boundloc

class BoundaryGroup():
    def __init__(self, boundary, hab):
        self.wall = doc.GetElement(boundary.ElementId)
        self.code = boundary.ElementId.IntegerValue
        self.hydro = True if doc.GetElement(doc.GetElement(boundary.ElementId).GetTypeId()).LookupParameter(hydroPar).AsInteger() == 1 else False
        self.length = boundary.GetCurve().Length
        #Longitud y área de puertas y ventanas que dan a la habitación calculada que vienen de este muro (se registra una vez y ya sólo se suman longitudes de perímetro).
        self.nopeRodapie = sum(map(float,[door.width for door in dbDoors if (door.toRoomId.IntegerValue == hab.Id.IntegerValue or door.fromRoomId.IntegerValue == hab.Id.IntegerValue) and door.hostId.IntegerValue == self.wall.Id.IntegerValue]))
        self.nopeArea = sum(map(float,[door.width * door.height for door in dbDoors if (door.toRoomId.IntegerValue == hab.Id.IntegerValue or door.fromRoomId.IntegerValue == hab.Id.IntegerValue) and door.hostId.IntegerValue == self.wall.Id.IntegerValue])) + sum(map(float,[window.width * window.height for window in dbWindows if (window.toRoomId.IntegerValue == hab.Id.IntegerValue or window.fromRoomId.IntegerValue == hab.Id.IntegerValue) and window.hostId.IntegerValue == self.wall.Id.IntegerValue]))

    def newLine(self, boundarySegment):
        self.length += boundarySegment.GetCurve().Length

#AQUÍ ESTAMOS: Hay que conseguir que metiendo líneas con su muro, vayan rellenando las pocas boundarywalls que haya, con todo dentro. Luego se pueden meter parámetros de puerta y ventana a cada uno. Hay que excluir Curtain y Stacked.

def RoomCalc(room):
    # get boundary elements and segments
    boundaryDic = {}
    #NotImplementedError: Method 'Approximate' in type 'Autodesk.LibG.CurveHost' from assembly 'LibG.ProtoInterface, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null' does not have an implementation.
    for boundarylist in room.GetBoundarySegments(options):
        #La lista de boundaries va dentro de otra.
        for boundary in boundarylist:
            #Que el elemento exista, sea un muro, no sea curtain wall, ni modelo in situ. Finalmente, que el tipo de muro no esté excluido.
            element = doc.GetElement(boundary.ElementId)
            if element != None and element.Category.Name == "Walls" and element.WallType.FamilyName != "Curtain Wall" and element.ToString() != "Autodesk.Revit.DB.FamilyInstance" and doc.GetElement(element.GetTypeId()).GetParameters(excludedPar)[0].AsInteger() != 1:
                if boundary.ElementId.IntegerValue not in boundaryDic.keys():
                    boundaryDic[boundary.ElementId.IntegerValue] = BoundaryGroup(boundary, room)
                else:
                    boundaryDic[boundary.ElementId.IntegerValue].newLine(boundary)

    # get room height
    height = room.Volume / room.Area
    # add area of wall hosted doors and windows from or to that room
    areaSeca = 0
    areaWA = 0
    rodapie = 0
    for bGroup in boundaryDic.values():
        if bGroup.hydro:
            areaWA += bGroup.length * height - bGroup.nopeArea
            rodapie += bGroup.length - bGroup.nopeRodapie
        else:
            areaSeca += bGroup.length * height - bGroup.nopeArea
            rodapie += bGroup.length - bGroup.nopeRodapie

    return room, SqFeetToSqMeters(areaSeca + areaWA), SqFeetToSqMeters(areaWA), FeetToMeters(rodapie)

data = list()
for room in FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
    data.append(RoomCalc(room))
t = Transaction(doc,"Cálculo Áreas Habitaciones")
t.Start()
for line in data:
    line[0].GetParameters(supPar)[0].SetValueString(str(line[1])+" m²")
    line[0].GetParameters(supHydroPar)[0].SetValueString(str(line[2])+" m²")
    line[0].GetParameters(rodPar)[0].SetValueString(str(line[3])+" m")
t.Commit()

# COMPROBAR QUE EL PARÁMETRO EXISTE, ETC
# AÑADIR LA MEDICIÓN DE HYDRO POR TIPO DE MURO
#EXPLICAR QUE EL ÁREA HIDROFUGADA SÓLO SE VALORA SI LA HABITACIÓN ES HÚMEDA.
#LOS MUROS DE FACHADA QUE LLEVAN TODO EL PAQUETE PUEDEN SER HYDRO Y NO VAN EXCLUIDOS.
