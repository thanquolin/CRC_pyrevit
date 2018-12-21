# coding: utf-8
"""PMA-Checker."""
#pyRevit info
__title__ = 'Room\nChecker'
__author__  = 'Carlos Romero Carballo'

import clr
import csv
import codecs
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

codelist = list()
with open(r"C:\Users\carlosromero\Desktop\PMA_REVIT_CARLOS.csv", "r") as csvfile:
    reader = csv.reader(codecs.EncodedFile(csvfile, 'utf-8', 'utf8'), delimiter=";")
    for row in reader:
        if row[0]:
            codelist.append(row[0])

grouplist = list()
for cod in codelist:
    if cod.split("-")[0] in grouplist:
        pass
    else:
        grouplist.append(cod.split("-")[0])

room_fec = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
valid = list()
no_area = list()
for room in room_fec:
    if room.Area:
        valid.append(room)
    else:
        no_area.append(room)

rvt_rooms_cods = [room.GetParameters("Nuevos Codigos")[0].AsString() for room in valid]
visto = list()
rep_cods = list()
for cod in rvt_rooms_cods:
    if cod not in visto:
        visto.append(cod)
    else:
        rep_cods.append(cod)

rooms = {}
to_doublemark = list()
for room in valid:
    if room.GetParameters("Nuevos Codigos")[0].AsString() not in rep_cods:
        rooms[room.GetParameters("Nuevos Codigos")[0].AsString()] = room
    else:
        to_doublemark.append(room)

in_pma = list()
not_in_pma = list()
new = list()
for cod in rooms.keys():
    if cod not in codelist:
        if cod.split("-")[0] in grouplist:
            new.append(rooms[cod])
        else:
            not_in_pma.append(rooms[cod])
    else:
        in_pma.append(rooms[cod])

t = Transaction(doc, "Marcar Rooms")
t.Start()
for room in no_area:
    room.GetParameters("Comments")[0].Set("Sin Área")
for room in new:
    room.GetParameters("Comments")[0].Set("Nueva?")
for room in not_in_pma:
    room.GetParameters("Comments")[0].Set("No está en el PMA")
for room in to_doublemark:
    room.GetParameters("Comments")[0].Set("Habitación repetida (correcta o no)")
for room in in_pma:
    room.GetParameters("Comments")[0].Set("Correcta")
t.Commit()
