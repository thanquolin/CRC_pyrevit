# coding: utf-8
"""PMA-Room Placer."""
#pyRevit info
__title__ = 'Room\nPlacer'
__author__  = 'Carlos Romero Carballo'

import clr
import csv
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

room_fec = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
rooms_per_level = dict()
for room in room_fec:
    if room.Level.Name not in rooms_per_level.keys():
        rooms_per_level[room.Level.Name] = [room]
    else:
        prev = rooms_per_level[room.Level.Name]
        rooms_per_level[room.Level.Name] = prev + [room]

print([ [key, len(rooms_per_level[key])] for key in rooms_per_level.keys()])

class PMAroom:
    def __init__(self, cod, a, b, c, d, name, sup):
        self.cod = cod
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.name = name
        self.sup = sup
        self.group = cod.split("-")[0]
    def __repr__(self):
        return "PMAroom({}, {}, {}, {}, {}, {}, {})".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.sup)
    def __str__(self):
        return "Habitación {}: Unidad Funcional: {}, Área Funcional: {}, Subárea Funcional: {},\
            Departamento: {}, Recinto: {},, Superficie: {} m2".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup)
    def __str__(self):
        return "Habitación {}: Unidad Funcional: {}, Área Funcional: {}, Subárea Funcional: {},\
            Departamento: {}, Recinto: {}, Superficie: {} m2".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup)
    def __eq__(self, other):
        '''Compara si los códigos de dos habitaciones son iguales.'''
        return self.cod == other.cod
    def sameGroup(self,other):
        '''Comprueba si dos habitaciones pertenecen al mismo grupo.'''
        return self.group == other.group
    def text(self):
        '''Devuelve una lista con los campos de texto de la habitación.'''
        return [self.a, self.b, self.c, self.d, self.name]
    def Crear(self, lvl, uv):
        nroom = doc.Create.NewRoom(lvl,uv)
        def Asignar(room, par, val):
            return room.GetParameters(par)[0].Set(val)
        Asignar(nroom, "Number", self.cod)
        Asignar(nroom, "(1) Unidad Funcional", self.a.decode('utf-8'))
        Asignar(nroom, "(2) Área Funcional", self.b.decode('utf-8'))
        Asignar(nroom, "(3) Subárea Funcional", self.c.decode('utf-8'))
        Asignar(nroom, "(4) Departamento", self.d.decode('utf-8'))
        Asignar(nroom, "Name", self.name.decode('utf-8'))
        Asignar(nroom, "PMA Reducido", 1)


PMArooms_from_PMA = dict()
visto = list()
kk = 0
with open(r"C:\Users\carlosromero\Desktop\PMA_REVIT_CARLOS.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter = ';', quotechar = "|")
    for row in reader:
        if row[0]:
            PMArooms_from_PMA[row[0]] = PMAroom(row[0],row[2],row[4],row[6],row[8],row[10],float(row[13].replace(",",".")))
            if row[0] in visto:
                kk += 1
            else:
                visto.append(row[0])
print("PMArooms_from_PMA: " + str(len(PMArooms_from_PMA.keys())))
print("repes: " + str(kk))

levels = {level.Name:level for level in FilteredElementCollector(doc).OfClass(Level).WhereElementIsNotElementType().ToElements() if level.Name in rooms_per_level.keys()}

t = Transaction(doc, "Room Replacement")
t.Start()
for level in levels.keys():
    rvt_rooms = rooms_per_level[level]
    for room in rvt_rooms:
        uv = UV(room.Location.Point.X, room.Location.Point.Y)
        cod = room.GetParameters("Nuevos Codigos")[0].AsString()
        doc.Delete(room.Id)
        PMArooms_from_PMA[cod].Crear(levels[level],uv)
t.Commit()
