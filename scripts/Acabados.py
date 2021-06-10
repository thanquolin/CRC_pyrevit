# -*- coding: utf-8 -*-
# Acabados sin separar zonas secas y húmedas para el cartón yeso
# Hay que tener en cuenta los tabiques secundarios en el acabado: IMPORTANTE!!!!
# Para ello, restamos al área de acabado de la habitación el área de los walls de tipo recogido en un listado
# Y por otro lado, medimos por código de acabado los muros en el capítulo de terminaciones
__title__ = 'Acabados HPC'
__doc__ = 'Acabados HPC'
__author__ = 'Carlos'

import Autodesk
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
from Autodesk.Revit.UI.Selection import * 
from Autodesk.Revit.UI import *

dbDoorCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Doors
dbWindowCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Windows
dbWallCategory = Autodesk.Revit.DB.BuiltInCategory.OST_Walls

excludedPar = "MED_Excluido"
supPar = "MED_Área de Acabado Vertical Neto"
rodPar = "MED_Perímetro Neto"

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
        self.toRoomId = dbElement.ToRoom[phase].Id if dbElement.ToRoom[phase] != None \
                        else Autodesk.Revit.DB.ElementId.InvalidElementId
        self.fromRoomId = dbElement.FromRoom[phase].Id if dbElement.FromRoom[phase] != None \
                        else Autodesk.Revit.DB.ElementId.InvalidElementId
        def dim(par):
            return dbElement.Symbol.GetParameters(par)[0].AsDouble() if not dbElement.GetParameters(par) \
                   else dbElement.GetParameters(par)[0].AsDouble()
        self.width = dim("Width")
        self.height = dim("Height")
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
        self.length = boundary.GetCurve().Length
        #Longitud y área de puertas y ventanas que dan a la habitación calculada que vienen de este muro (se registra una vez y ya sólo se suman longitudes de perímetro).
        self.nopeRodapie = sum(map(float,[door.width for door in dbDoors if (door.toRoomId.IntegerValue == hab.Id.IntegerValue or door.fromRoomId.IntegerValue == hab.Id.IntegerValue) and door.hostId.IntegerValue == self.wall.Id.IntegerValue]))
        self.nopeArea = sum(map(float,[door.width * door.height for door in dbDoors if (door.toRoomId.IntegerValue == hab.Id.IntegerValue or door.fromRoomId.IntegerValue == hab.Id.IntegerValue) and \
            door.hostId.IntegerValue == self.wall.Id.IntegerValue])) + sum(map(float,[window.width * window.height for window in dbWindows if (window.toRoomId.IntegerValue == hab.Id.IntegerValue or \
            window.fromRoomId.IntegerValue == hab.Id.IntegerValue) and window.hostId.IntegerValue == self.wall.Id.IntegerValue]))

    def newLine(self, boundarySegment):
        self.length += boundarySegment.GetCurve().Length

#AQUÍ ESTAMOS: Hay que conseguir que metiendo líneas con su muro, vayan rellenando las pocas boundarywalls que haya, con todo dentro. Luego se pueden meter parámetros de puerta y ventana a cada uno. Hay que excluir Curtain y Stacked.

def RoomCalc(room):
    # get boundary elements and segments
    boundaryDic = {}
    #NotImplementedError: Method 'Approximate' in type 'Autodesk.LibG.CurveHost' from assembly 'LibG.ProtoInterface, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null' does not have an implementation.
    for boundarylist in room.GetBoundarySegments(options):
        #La lista de boundaries va dentro de otra PORQUE PUEDE HABER VARIOS BUCLES EN LA HABITACIÓN. OJO PORQUE EL PRIMERO ES EL BUCLE EXTERIOR (Y EL RESTO SON PILARES Y COSAS ASÍ), PERO TODOS CUENTAN PARA EL PERÍMETRO DE ACABADO
        for boundary in boundarylist:
            #Que el elemento exista, sea un muro, no sea curtain wall, ni modelo in situ. Finalmente, que el tipo de muro no esté excluido.
            element = doc.GetElement(boundary.ElementId)
            if element != None and element.Category.Name == "Walls" and element.WallType.FamilyName != "Curtain Wall" and element.ToString() != "Autodesk.Revit.DB.FamilyInstance" and doc.GetElement(element.GetTypeId()).GetParameters(excludedPar)[0].AsInteger() != 1:
                if "REV" in element.Name:
                    print("ERROR DE BOUNDARIES CON ACABADOS SECUNDARIOS")
                if boundary.ElementId.IntegerValue not in boundaryDic.keys():
                    boundaryDic[boundary.ElementId.IntegerValue] = BoundaryGroup(boundary, room)
                else:
                    boundaryDic[boundary.ElementId.IntegerValue].newLine(boundary)

    # get room height
    height = room.Volume / room.Area
    # add area of wall hosted doors and windows from or to that room
    area = 0
    rodapie = 0
    for bGroup in boundaryDic.values():
        area += bGroup.length * height - bGroup.nopeArea
        rodapie += bGroup.length - bGroup.nopeRodapie

    return room, area, rodapie

#Añadido de última hora para restar acabados secundarios
secString = "ARQ_REV_13"
dbWalls = FilteredElementCollector(doc).OfCategory(dbWallCategory).WhereElementIsNotElementType().ToElements()
secs = [w for w in dbWalls if secString in w.Name]
secRooms = []
for w in secs:
    wpt = w.Location.Curve.Evaluate(0.5,True)
    wdir = w.Location.Curve.Direction
    perp = XYZ(-wdir.Y/5, wdir.X/5, 0)
    if doc.GetRoomAtPoint(wpt):
        secRooms.append(doc.GetRoomAtPoint(wpt))
    elif doc.GetRoomAtPoint(wpt.Add(perp)):
        secRooms.append(doc.GetRoomAtPoint(wpt.Add(perp)))
    elif doc.GetRoomAtPoint(wpt.Add(perp.Negate())):
        secRooms.append(doc.GetRoomAtPoint(wpt.Add(perp.Negate())))
    else:
        secRooms.append("ERROR")
secDic = {}
for r,s in zip(secRooms,secs):
    if r.Id.IntegerValue not in secDic.keys():
        secDic[r.Id.IntegerValue] = s.GetParameters("Area")[0].AsDouble()
    else:
        secDic[r.Id.IntegerValue] += s.GetParameters("Area")[0].AsDouble()


t = Transaction(doc,"Acabados Habitaciones")
t.Start()

data = list()
for room in FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
    #Nos quitamos de en medio las habitaciones Not Placed, Not Enclosed, Redundant. 
    if room.Area != 0:
        data.append(RoomCalc(room))
    else:
        room.GetParameters(supPar)[0].Set(0)
        room.GetParameters(rodPar)[0].Set(0)


for line in data:
    if line[0].Id.IntegerValue in secDic.keys():
        line[0].GetParameters(supPar)[0].Set(line[1] - secDic[line[0].Id.IntegerValue])
    else:
        line[0].GetParameters(supPar)[0].Set(line[1])
    line[0].GetParameters(rodPar)[0].Set(line[2])
t.Commit()