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

# Tipo de vista sección (para la creación de las secciones)
vft = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeSection)

# Lista del primer ejemplar de cada tipo de carpintería
def instance_collector(category):
    return FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()

cat_doors = Autodesk.Revit.DB.BuiltInCategory.OST_Doors
cat_windows = Autodesk.Revit.DB.BuiltInCategory.OST_Windows
all_doors = instance_collector(cat_doors)
all_windows = instance_collector(cat_windows)

door_types_ex = list()
door_type_ids = list()
for door in all_doors:
    if door.GetTypeId() not in door_type_ids:
        door_types_ex.append(door)
        door_type_ids.append(door.GetTypeId())
window_types_ex = list()
window_type_ids = list()
for window in all_windows:
    if window.GetTypeId() not in window_type_ids:
        window_types_ex.append(window)
        window_type_ids.append(window.GetTypeId())

carp_list = door_types_ex + window_types_ex

#Geometría de la sección
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

boxes = list()
for element in carp_list:
    width = inst_width(element)
    height = inst_height(element)
    #Se ha fijado el offset a 1 pie. Afecta también al espacio entre secciones en la sheet
    offset = 1

    midpoint = element.Location.Point
    min = XYZ( -width/2 - offset, -(height/2 + midpoint.Z - doc.GetElement(element.LevelId).Elevation) - offset , -offset)
    max = XYZ( width/2 + offset, (height)/2 + offset , offset)
    section_height = - min.Y + max.Y
    section_width = width + 2*offset
    normal = element.FacingOrientation
    up = XYZ.BasisZ
    viewdir = normal.Negate()

    transform = Transform.Identity
    transform.Origin = XYZ(midpoint.X, midpoint.Y, height/2 + midpoint.Z)
    transform.BasisX = normal.CrossProduct(up)
    transform.BasisY = up
    transform.BasisZ = viewdir

    new_bb = BoundingBoxXYZ()
    new_bb.Transform = transform
    new_bb.Min = min
    new_bb.Max = max
    #box, view name, height, width
    boxes.append([new_bb, "MC-" + element.Symbol.Family.Name + "-" + element.Name, element.Id, section_height, section_width])

#Transacción para la creación de secciones y sheet, y la colocación de las primeras en la segunda
t = Transaction(doc,"Vistas Memoria Carpintería")
t.Start()

#Creación de tipo de secciones "Memoria Carpintería" (para separar las nuevas secciones en el navegador de proyecto)
fec= FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
for famtype in fec:
	if famtype.GetParameters("Family Name")[0].AsString() == "Section" and famtype.GetParameters("Type Name")[0].AsString() == "Building Section":
		viewtype = famtype
		break
mc = viewtype.Duplicate("Memoria Carpintería")

new_views = list()
for line in boxes:
    section = ViewSection.CreateSection(doc, vft, line[0])
    section.GetParameters("View Name")[0].Set(line[1])
    section.ChangeTypeId(mc.Id)
    #Se ha fijado la escala a 1:10
    scale = 10
    section.Scale = scale
    new_views.append([section, line[2], line[3], line[4]])

#Creación de sheet
invalid_el_id = ElementId.InvalidElementId
sheet = ViewSheet.Create(doc, invalid_el_id)
sheet.Name = "Memoria Carpintería"
sheet.SheetNumber = "A999"

#Colocación de secciones en sheet
coord = 0
prev = 0
for view in new_views:
    coord = prev + offset + view[3]
    Viewport.Create(doc, sheet.Id, view[0].Id, XYZ(coord/scale,view[2]/scale/2,0))
    prev = coord

t.Commit()

#Transacción para aislar la carpintería en cada sección
for view in new_views:
    tra = Transaction(doc, "Aislar Carpinterías")
    uidoc.ActiveView = view[0]
    tra.Start()
    view[0].IsolateElementTemporary(view[1])
    view[0].ConvertTemporaryHideIsolateToPermanent()
    tra.Commit()

#Cambia la activeview para mostrar la memoria de carpintería creada
uidoc.ActiveView = sheet
