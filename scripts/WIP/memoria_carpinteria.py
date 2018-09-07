# coding: utf8
"""Crea un alzado recortado para cada tipo de puerta y ventana en el proyecto, desde el exterior, con el nombre del tipo. Debe existir alguna vista 3D en el proyecto."""

#pyRevit info
__title__ = 'Memoria\nCarpintería'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
import Autodesk.Revit.UI.Selection

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def instance_collector(category):
    return FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
vft = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeSection)

doors = instance_collector(Autodesk.Revit.DB.BuiltInCategory.OST_Doors)
windows = instance_collector(Autodesk.Revit.DB.BuiltInCategory.OST_Windows)
door_types_ex = list()
door_type_ids = list()
for door in doors:
    if door.GetTypeId() not in door_type_ids:
        door_types_ex.append(door)
        door_type_ids.append(door.GetTypeId())
window_types_ex = list()
window_type_ids = list()
for window in windows:
    if window.GetTypeId() not in window_type_ids:
        window_types_ex.append(window)
        window_type_ids.append(window.GetTypeId())

instances = door_types_ex + window_types_ex



def inst_width(instance):
    valid = ["Width", "Anchura"] #TEMA IDIOMA! USA ESTE MÉTODO LOS PARÁMETROS DE LA API?
    if len(instance.GetParameters("Width")) == 1:
        return instance.GetParameters("Width")[0].AsDouble()
    elif len(instance.GetParameters("Width")) != 1:
        if len(doc.GetElement(instance.GetTypeId()).GetParameters("Width")) == 1:
            return doc.GetElement(instance.GetTypeId()).GetParameters("Width")[0].AsDouble()
        elif len(doc.GetElement(instance.GetTypeId()).GetParameters("Width")) > 1:
            return doc.GetElement(instance.GetTypeId()).GetParameters("Width")[0].AsDouble()
        else:
            return 6.56168

mag = list()

for element in instances:
    bb = element.get_BoundingBox(None)
    minZ = bb.Min.Z
    maxZ = bb.Max.Z
    width = inst_width(element)
    height = maxZ - minZ
    distance = 4
    offset = 1

    min = XYZ( -width/2 - offset, minZ - offset, -offset)
    max = XYZ( width/2 + offset, maxZ + offset, offset)

    midpoint = element.Location.Point
    normal = element.FacingOrientation
    up = XYZ.BasisZ
    viewdir = normal.Negate()

    transform = Transform.Identity
    transform.Origin = midpoint
    transform.BasisX = normal.CrossProduct(up)
    transform.BasisY = up
    transform.BasisZ = viewdir

    new_bb = BoundingBoxXYZ()
    new_bb.Transform = transform
    new_bb.Min = min
    new_bb.Max = max

    mag.append([new_bb, "MC-" + element.Id.ToString()])

t = Transaction(doc,"Vistas Memoria Carpintería")
t.Start()
for bb in mag:
    section = ViewSection.CreateSection(doc, vft, bb[0])
    section.GetParameters("View Name")[0].Set(bb[1])
t.Commit()
