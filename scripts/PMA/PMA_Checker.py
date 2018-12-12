# coding: utf8
"""PMA-Checker."""
#pyRevit info
__title__ = 'PMA\nChecker'
__author__  = 'Carlos Romero Carballo'

import math
import clr
import csv
import codecs
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#(A) No sigue si hay habitaciones de área 0 en el modelo.
for room in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements():
    if not room.Area:
        raise ValueError("Hay habitaciones Not placed, Redundant o Not Enclosed en el modelo (con área 0).")

#(B) y (C) Listados de habitaciones de PMA y Revit.
class PMAroom:
    def __init__(self, cod, a, b, c, d, name, inst, sup, obs):
        self.cod = cod
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.name = name
        self.inst = inst
        self.sup = sup
        self.obs = obs
        self.group = cod.split("-")[0]
    def __repr__(self):
        return "PMAroom({}, {}, {}, {}, {}, {}, {}, {}, {})".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup, self.obs)
    def __str__(self):
        return "Habitación {}: Unidad Funcional: {}, Área Funcional: {}, Subárea Funcional: {},\
            Departamento: {}, Recinto: {}, Instancia: {}, Superficie: {} m2, Observaciones: {}".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup, self.obs)
    def __str__(self):
        return "Habitación {}: Unidad Funcional: {}, Área Funcional: {}, Subárea Funcional: {},\
            Departamento: {}, Recinto: {}, Instancia: {}, Superficie: {} m2, Observaciones: {}".format(
            self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup, self.obs)
    def __eq__(self, other):
        '''Compara si dos habitaciones son EXACTAMENTE iguales.'''
        return [self.cod, self.a, self.b, self.c, self.d, self.name, self.inst, self.sup, self.obs] == [other.cod, other.a, other.b, other.c, other.d, other.name, other.inst, other.sup, other.obs]
    def sameGroup(self,other):
        '''Comprueba si dos habitaciones pertenecen al mismo grupo.'''
        return [self.group, self.a, self.b, self.c, self.d, self.name] == [other.group, other.a, other.b, other.c, other.d, other.name]

#(B) PMArooms desde PMAroom.
PMArooms_from_PMA = list()

with open(r"C:\Users\carlosromero\Desktop\PMA_REVIT_CARLOS.csv", "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter = ';', quotechar = "|")
    for row in reader:
        if row[0]:
            PMArooms_from_PMA.append(PMAroom(row[0],row[2],row[4],row[6],row[8],row[10],row[11],row[13],row[14]))

#(C) PMArooms desde Revit.
valid_rooms = [room for room in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements() if room.Area]
def PMAroom_from_Revit(room):
    def pFlt(el,name):
        return el.GetParameters(name)[0].AsDouble()
    def pInt(el, name):
        return el.GetParameters(name)[0].AsInteger()
    def pStr(el, name):
        return el.GetParameters(name)[0].AsString()
    return PMAroom(
        pStr(room, "Number"),
        pStr(room, "(1) Unidad Funcional"),
        pStr(room, "(2) Área Funcional"),
        pStr(room, "(3) Subárea Funcional"),
        pStr(room, "(4) Departamento"),
        pStr(room, "Name"),
        pInt(room, "PMA Instancia"),
        pFlt(room, "PMA Superficie"),
        pStr(room, "PMA Observaciones")
    )
#revit_rooms puede contener habitaciones duplicadas o erróneas que hay que filtrar y listar.
revit_rooms = [PMAroom_from_Revit(room) for room in valid_rooms]

#(D) Habitaciones erróneas (tienen que irse fuera primero, no queremos que aparezcan en el listado de duplicadas en el caso de estar mal y además duplicadas)
def roomOk(room):
    '''Acepta objetos PMAroom, los compara con PMArooms_from_PMA, y determina si coincide con alguna combinación de código de grupo, nombres (1-4) y name.'''
    for instance in PMArooms_from_PMA:
        if room.sameGroup(instace):
            return True
    return False
#(E) Habitaciones duplicadas (sean duplicadas de las originales del PMA o de las que se han creado nuevas).
def roomUnique(room, roomlist):
    '''Acepta objetos PMAroom y una lista de PMAroom, e indica si se encuentra repetido en la lista.'''
    for idx in range(len(roomlist)):
        if roomlist[idx] in roomlist[:idx] + roomlist[(idx + 1):]:
            return False
    return True

wrong_rooms = list()
duplicate_rooms = list()
comparison_rooms = list()

for room in revit_rooms:
    if not roomOk(room):
        wrong_rooms.append(room)
    elif not roomUnique(room, PMArooms_from_PMA):
        duplicate_rooms.append(room)
    else:
        comparison_rooms.append(room)

# (F) y (G) Exportación de las listas de erróneas y duplicadas (excel o pantalla?)
