# -*- coding: utf-8 -*-
__title__ = 'Instance Room Locations'
__doc__ = 'Writes Linked File Room Numbers and Names in Family Instances of a given Category'
__author__ = 'Carlos Romero'

import Autodesk
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document

fec = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements()
linkNames = [l.Name for l in fec]

from pyrevit import forms
items = linkNames
res = forms.SelectFromList.show(items, button_name='Select Link')

linkDoc = fec[items.index(res)].GetLinkDocument()
p = [p for p in linkDoc.Phases][-1]

cats = ["Fire Alarm Devices", "Plumbing Fixtures"]
catnames = [BuiltInCategory.OST_FireAlarmDevices, BuiltInCategory.OST_PlumbingFixtures]

newitems = cats
newres = forms.SelectFromList.show(newitems, button_name='Select Category')

cat = catnames[cats.index(newres)]

collector = FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType().ToElements()
data = list()

for e in collector:
    try:
        room = linkDoc.GetRoomAtPoint(e.GetSpatialElementCalculationPoint(),p)
    except:
        room = linkDoc.GetRoomAtPoint(e.Location.Point,p)
    if room:
        number = room.LookupParameter("Number").AsString() if room.LookupParameter("Number") else "No number"
        name = room.LookupParameter("Name").AsString() if room.LookupParameter("Name") else "No name"
        line = number + "-" + name
        data.append(line)
    else:
        data.append("Not in a room")

parName = forms.ask_for_string(
    default='Parameter Name',
    prompt='In which parameter do you want to store the location information?',
    title='Enter Instance Parameter Name'
)

t = Transaction(doc, "Instance Room Locations")
t.Start()

for e, d in zip(collector, data):
    e.LookupParameter(parName).Set(d)

t.Commit()
