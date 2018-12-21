# coding: utf-8
"""PMA-Checker."""
#pyRevit info
__title__ = 'PMA\nChecker'
__author__  = 'Carlos Romero Carballo'

import unicodedata
import math
import clr
import csv
import codecs
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def sqft_to_sqmt(val):
    return val*0.3048*0.3048

#(A) No sigue si hay habitaciones de área 0 en el modelo.
valid_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
for room in valid_rooms:
    if not room.Area:
        raise ValueError("Hay habitaciones Not placed, Redundant o Not Enclosed en el modelo (con area 0).")

#(B) y (C) Listados de habitaciones de PMA y Revit.
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
    #OJO PORQUE EN LAS DOS ÚLTIMAS NO ESTAMOS COMPARANDO TODOS LOS CAMPOS Y SEGURAMENTE HABRÁ HABITACIONES CON CÓDIGOS IGUALES Y OTROS CAMPOS NO IGUALES.

#(B) PMArooms desde PMAroom.
PMArooms_from_PMA = list()

with open(r"C:\Users\carlosromero\Desktop\PMA_REVIT_CARLOS.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter = ';', quotechar = "|")
    for row in reader:
        if row[0]:
            PMArooms_from_PMA.append(PMAroom(row[0],row[2],row[4],row[6],row[8],row[10],float(row[13].replace(",","."))))
print("PMArooms_from_PMA: " + str(len(PMArooms_from_PMA)))

#(C) PMArooms desde Revit.
def PMAroom_from_Revit(room):
    def pStr(el, name):
        if el.GetParameters(name)[0].AsString():
            return el.GetParameters(name)[0].AsString()
        else:
            return ""

    return PMAroom(
        pStr(room, "Number"),
        pStr(room, "(1) Unidad Funcional"),
        pStr(room, "(2) Área Funcional"),
        pStr(room, "(3) Subárea Funcional"),
        pStr(room, "(4) Departamento"),
        pStr(room, "Name"),
        sqft_to_sqmt(room.Area),
    )
#revit_rooms puede contener habitaciones duplicadas o erróneas que hay que filtrar y listar.
groups = [inst.group for inst in PMArooms_from_PMA]
revit_rooms = [PMAroom_from_Revit(room) for room in valid_rooms if room.GetParameters("PMA Reducido")[0].AsInteger()]
print("revit_rooms: " + str(len(revit_rooms)))
#(D) Habitaciones erróneas (tienen que irse fuera primero, no queremos que aparezcan en el listado de duplicadas en el caso de estar mal y además duplicadas)
#(E) Habitaciones duplicadas (sean duplicadas de las originales del PMA o de las que se han creado nuevas).

wrong_rooms = list()
duplicate_rooms = list()
comparison_rooms = list()
visto = list()
for room in revit_rooms:
    if [room.cod] + room.text() not in [[pr.cod] + pr.text() for pr in PMArooms_from_PMA]:
        wrong_rooms.append(room)
        #print("-".join([room.cod] + room.text()))
        #print("-".join([pr.cod] + pr.text()))
        #print("--")
    else:
        if room.cod in visto:
            duplicate_rooms.append(room)
        else:
            comparison_rooms.append(room)
            visto.append(room.cod)
print("wrong_rooms: " + str(len(wrong_rooms)))
print("duplicate_rooms: " + str(len(duplicate_rooms)))
print("comparison_rooms: " + str(len(comparison_rooms)))

#(F) y (G) Exportación de las listas de erróneas y duplicadas (excel o pantalla?)

#(H) Diccionario de grupos.
group_dictionary = dict()

for room in comparison_rooms:
    if room.group not in group_dictionary.keys():
        group_dictionary[room.group] = room.text() + [room.sup]
    else:
        prev = group_dictionary[room.group][-1]
        new = group_dictionary[room.group][:-1] + [prev + room.sup]
        group_dictionary[room.group] = new

#(I) Diferencia sup. nº instancias por grupo.
comparison = list()
for group in sorted(group_dictionary.keys()):
    output = group_dictionary[group]
    output[-1] = str(round(output[-1],2)).replace(".",",")
    comparison.append( [group] + output)
# hay que sacar los grupos del pma y las sumas de sus instancias y superficies


with open(r"C:\Users\carlosromero\Desktop\result.csv", "wb") as csvnewfile:
    writer = csv.writer(csvnewfile, delimiter = ';', quotechar = "|", quoting = csv.QUOTE_MINIMAL)
    for row in comparison:
        writer.writerow(row)

csvnewfile.close()
