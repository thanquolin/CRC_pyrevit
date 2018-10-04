# coding: utf8
"""Crea una vista sección para cada tipo de puerta y ventana en el proyecto, desde el exterior, con el nombre del tipo, y alberga estas secciones en la Sheet 999-Memoria Carpintería."""

#pyRevit info
__title__ = 'Memoria\nCarpintería'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import List
import Autodesk.Revit.UI
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
language = uidoc.Application.Application.Language

#Lenguaje
def par_get(parameter):
    idx = 0 if language == Autodesk.Revit.ApplicationServices.LanguageType.English_USA else 1
    parameters = {"Width":["Width","Anchura"], "Height":["Height","Altura"], "Family Name":["Family Name","Nombre de familia"], "Section":["Section","Sección"], "Type Name":["Type Name","Nombre de tipo"], "View Name":["View Name","Nombre de vista"]  }
    return parameters[parameter][idx]

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
    if len(instance.GetParameters(par_get("Width"))) == 1:
        return instance.GetParameters(par_get("Width"))[0].AsDouble()
    else:
        return doc.GetElement(instance.GetTypeId()).GetParameters(par_get("Width"))[0].AsDouble()
def inst_height(instance):
    if len(instance.GetParameters(par_get("Height"))) == 1:
        return instance.GetParameters(par_get("Height"))[0].AsDouble()
    else:
        return doc.GetElement(instance.GetTypeId()).GetParameters(par_get("Height"))[0].AsDouble()


boxes = list()
plan_boxes = list()
for element in carp_list:
    width = inst_width(element)
    height = inst_height(element)

    #Se ha fijado el offset a 1 pie. Afecta también al espacio entre secciones en la sheet
    offset = 1
    midpoint = element.Location.Point
    #PARA ALZADOS SE DEBERÍA METER MÁS OFFSET POR LA PARTE INTERIOR, PARA MOSTRAR LA APERTURA DE LA PUERTA O LA VENTANA
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
    ###FALLA
    new_bb.Transform = transform
    new_bb.Min = min
    new_bb.Max = max
    #box, view name, height, width
    boxes.append([new_bb, "MC-" + element.Symbol.Family.Name + "-" + element.Name, element.Id, section_height, section_width])

    #plan boxes
    plan_min = XYZ( -width/2 - offset, - offset , 0)
    plan_max = XYZ( width/2 + offset, offset , height/2 + offset)

    plan_transform = Transform.Identity
    plan_transform.Origin = XYZ(midpoint.X, midpoint.Y, height/2 + midpoint.Z)
    plan_transform.BasisX = normal.CrossProduct(up)
    plan_transform.BasisY = normal.Negate()
    plan_transform.BasisZ = up.Negate()

    plan_bb = BoundingBoxXYZ()
    ##### FALLA
    plan_bb.Transform = plan_transform
    plan_bb.Min = plan_min
    plan_bb.Max = plan_max
    plan_boxes.append([plan_bb, "PC-" + element.Symbol.Family.Name + "-" + element.Name, element.Id])

#Transacción para la creación de secciones y sheet, y la colocación de las primeras en la segunda
t = Transaction(doc,"Vistas Memoria Carpintería")
t.Start()

###### ESTO VARÍA PARA CADA ARCHIVO!!!"
#Creación de tipo de secciones "Memoria Carpintería" (para separar las nuevas secciones en el navegador de proyecto)
fec= FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
#Section "Building Section"
building_section = "Building Section" if "Building Section" in [f.GetParameters(par_get("Type Name"))[0].AsString() for f in fec] else "Sección"
for famtype in fec:
	if famtype.GetParameters(par_get("Family Name"))[0].AsString() == par_get("Section") and famtype.GetParameters(par_get("Type Name"))[0].AsString() == building_section:
		viewtype = famtype
		break
mc = viewtype.Duplicate("Memoria Carpintería")

new_views = list()
for line in boxes:
    section = ViewSection.CreateSection(doc, vft, line[0])
    section.GetParameters(par_get("View Name"))[0].Set(line[1])
    section.ChangeTypeId(mc.Id)
    #Se ha fijado la escala a 1:10
    scale = 10
    section.Scale = scale
    new_views.append([section, line[2], line[3], line[4]])

#cortes de planta
new_plans = list()
for line in plan_boxes:
    section = ViewSection.CreateSection(doc,vft,line[0])
    section.GetParameters(par_get("View Name"))[0].Set(line[1])
    section.ChangeTypeId(mc.Id)
    section.Scale = scale
    new_plans.append([section,line[2]])

#Creación de sheet
invalid_el_id = ElementId.InvalidElementId
sheet = ViewSheet.Create(doc, invalid_el_id)
sheet.Name = "Memoria Carpintería"
sheet.SheetNumber = "A999"

#Colocación de secciones en sheet
coord = 0
prev = 0
for view, plan in zip(new_views, new_plans):
    coord = prev + offset + view[3]
    Viewport.Create(doc, sheet.Id, view[0].Id, XYZ(coord/scale,view[2]/scale/2,0))
    Viewport.Create(doc, sheet.Id, plan[0].Id, XYZ(coord/scale,-offset/scale,0))
    prev = coord

t.Commit()

#Transacciones para aislar la carpintería en cada sección - ALTERNATIVA: CREAR UNA VIEW TEMPLATE Y ASIGNARLA A LAS SECCIONES
for view, plan in zip(new_views, new_plans):
    tra = Transaction(doc, "Aislar Carpinterías")
    uidoc.ActiveView = view[0]
    tra.Start()
    view[0].IsolateElementTemporary(view[1])
    view[0].ConvertTemporaryHideIsolateToPermanent()
    tra.Commit()
    Autodesk.Revit.UI.UIView.Close(uidoc.GetOpenUIViews()[0])
    tra2 = Transaction(doc, "Aislar Carpinterías")
    uidoc.ActiveView = plan[0]
    tra2.Start()
    ####### ELEMENTOS SIN HOST
    plan[0].IsolateElementsTemporary(List[ElementId]([plan[1],doc.GetElement(plan[1]).Host.Id]))
    plan[0].ConvertTemporaryHideIsolateToPermanent()
    tra2.Commit()
    Autodesk.Revit.UI.UIView.Close(uidoc.GetOpenUIViews()[0])


#Cambia la activeview para mostrar la memoria de carpintería creada
uidoc.ActiveView = sheet
