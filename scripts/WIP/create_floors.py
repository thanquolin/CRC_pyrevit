# coding: utf8
"""Crea suelos del tipo elegido en las habitaciones del nivel de la planta actual."""
#pyRevit info
__title__ = 'Crear Suelos\nen Habitaciones'
__author__  = 'Carlos Romero Carballo'

from pyrevit.coreutils import Timer
timer = Timer()

import clr
import Autodesk
from Autodesk.Revit.DB import *
from pyrevit import revit, DB, UI
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def fp_active_view(document):
    for parameter in document.ActiveView.Parameters:
        if parameter.Definition.Name == "Floor Plan" or parameter.Definition.Name == "Floor Plans" or parameter.Definition.Name == "Plano de Planta":
            return True
    return False

if not fp_active_view(doc):
    print("La vista activa debe ser un plano de planta.")
else:
    current_view_level = doc.ActiveView.GenLevel
    current_view_phase = doc.GetElement(doc.ActiveView.LookupParameter("Phase").AsElementId())
    current_view_rooms = FilteredElementCollector(doc,doc.ActiveView.Id).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Rooms).ToElements()
    current_view_floors_ids = FilteredElementCollector(doc,doc.ActiveView.Id).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Floors).ToElementIds()

    calculator = SpatialElementGeometryCalculator(doc)
    options = Autodesk.Revit.DB.SpatialElementBoundaryOptions()
    boundloc = Autodesk.Revit.DB.AreaVolumeSettings.GetAreaVolumeSettings(doc).GetSpatialElementBoundaryLocation(SpatialElementType.Room)
    options.SpatialElementBoundaryLocation = boundloc

    curve_arrays = list()
    for room in current_view_rooms:
        ca = CurveArray()
        for group in room.GetBoundarySegments(options):
            for segment in group:
                ca.Append(segment.GetCurve())
                curve_arrays.append(ca)

    t = Transaction(doc,"Creación Suelos")
    t.Start()
    for array in curve_arrays:
        doc.Create.NewFloor(array, False)
    t.Commit()

    current_view__final_floors = FilteredElementCollector(doc,doc.ActiveView.Id).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Floors).ToElements()
    if current_view_floors_ids:
        highlight = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Floors).Excluding(current_view_floors_ids).ToElementIds()
    else:
        highlight = FilteredElementCollector(doc).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Floors).ToElementIds()
    uidoc.Selection.SetElementIds(highlight)

endtime ="\nHe tardado " + str(timer.get_time()) + " segundos en llevar a cabo esta tarea."
print(endtime)
