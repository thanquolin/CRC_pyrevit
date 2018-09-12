# coding: utf8
"""Crea una sección para cada tipo de puerta y ventana en el proyecto, desde el exterior, con el nombre del tipo, y alberga estas secciones en la Sheet 999-Memoria Carpintería."""

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
    if len(instance.GetParameters("Width")) == 1:
        return instance.GetParameters("Width")[0].AsDouble()
    else:
        return doc.GetElement(instance.GetTypeId()).GetParameters("Width")[0].AsDouble()

def inst_height(instance):
    if len(instance.GetParameters("Height")) == 1:
        return instance.GetParameters("Height")[0].AsDouble()
    else:
        return doc.GetElement(instance.GetTypeId()).GetParameters("Height")[0].AsDouble()


mag = list()


for element in instances:
    bb = element.get_BoundingBox(None) if element.get_BoundingBox(None) != None else BoundingBoxXYZ()
    minZ = bb.Min.Z
    maxZ = bb.Max.Z
    width = inst_width(element)
    offset = 1
    height = inst_height(element)
    min = XYZ( -width/2 - offset, -(height/2 + element.Location.Point.Z - doc.GetElement(element.LevelId).Elevation) - offset , -offset)
    max = XYZ( width/2 + offset, (height)/2 + offset , offset)
    section_height = - min.Y + max.Y
    section_width = width + 2*offset
    midpoint = element.Location.Point if element.Location != None else XYZ(0,0,0)
    normal = element.FacingOrientation
    up = XYZ.BasisZ
    viewdir = normal.Negate()

    transform = Transform.Identity
    transform.Origin = XYZ(midpoint.X, midpoint.Y, height/2 + element.Location.Point.Z)
    transform.BasisX = normal.CrossProduct(up)
    transform.BasisY = up
    transform.BasisZ = viewdir

    new_bb = BoundingBoxXYZ()
    new_bb.Transform = transform
    new_bb.Min = min
    new_bb.Max = max
    mag.append([new_bb, "MC-" + element.Symbol.Family.Name + "-" + element.Name, element.Id, section_height, section_width])

t = Transaction(doc,"Vistas Memoria Carpintería")
t.Start()
fec= FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
for famtype in fec:
	if famtype.GetParameters("Family Name")[0].AsString() == "Section" and famtype.GetParameters("Type Name")[0].AsString() == "Building Section":
		viewtype = famtype
		break
mc = viewtype.Duplicate("Memoria Carpintería")
new_views = list()
for bb in mag:
    section = ViewSection.CreateSection(doc, vft, bb[0])
    section.GetParameters("View Name")[0].Set(bb[1])
    section.ChangeTypeId(mc.Id)
    scale = 10
    section.Scale = scale
    new_views.append([section, bb[2], bb[3], bb[4]])
invalid_el_id = ElementId.InvalidElementId
sheet = ViewSheet.Create(doc, invalid_el_id)
sheet.Name = "Memoria Carpintería"
sheet.SheetNumber = "A999"
coord = 0
prev = 0
for view in new_views:
    coord = prev + offset + view[3]
    Viewport.Create(doc, sheet.Id, view[0].Id, XYZ(coord/scale,view[2]/scale/2,0))
    prev = coord
t.Commit()


for view in new_views:
    tra = Transaction(doc, "Aislar Carpinterías")
    uidoc.ActiveView = view[0]
    tra.Start()
    view[0].IsolateElementTemporary(view[1])
    view[0].ConvertTemporaryHideIsolateToPermanent()
    tra.Commit()

uidoc.ActiveView = sheet
