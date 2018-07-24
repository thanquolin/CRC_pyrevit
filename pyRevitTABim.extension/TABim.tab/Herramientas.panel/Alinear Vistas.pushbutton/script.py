# coding: utf8
"""Alinea scope boxes, secciones y alzados a muros, model lines y rejillas. Se selecciona primero la referencia y luego la vista o scope box."""

#pyRevit info
__title__ = 'Alinear Vistas\ny Scope Boxes'
__author__  = 'Carlos Romero Carballo'

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

from pyrevit.coreutils import Timer
timer = Timer()

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

import Autodesk
from Autodesk import Revit

import Autodesk.Revit.UI.Selection

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

try:
    one = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)
    two = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)


    first = doc.GetElement(one)
    second = doc.GetElement(two)

    # normal of wall, line or grid
    if first.Category.Name == "Walls":
        normal = first.Orientation
    elif first.Category.Name == "Grids":
        normal = XYZ(first.Curve.Direction[1], -first.Curve.Direction[0], first.Curve.Direction[2])
    else:
        try:
            normal = XYZ(first.GeometryCurve.Direction[1],-first.GeometryCurve.Direction[0],first.GeometryCurve.Direction[2])
        except:
            print("Por favor, selecciona como primer elemento un muro, una línea de modelo o una rejilla.")


    # process for Scope Boxes, Sections or Elevations
    if second.Category.Name == "Scope Boxes":
        app = doc.Application
        opt = app.Create.NewGeometryOptions()
        geo = second.get_Geometry(opt)
        lines = [line for line in geo]
        points = [[line.GetEndPoint(0), line.GetEndPoint(1)] for line in lines]
        f_points = [point for sublist in points for point in sublist]
        x = [coord[0] for coord in f_points]
        y = [coord[1] for coord in f_points]
        z = [coord[2] for coord in f_points]
        centroid = (sum(x) / len(f_points), sum(y) / len(f_points), sum(z) / len(f_points))

        for line in geo:
            if line.Direction[2] == 0:
                prev_vector = line.Direction
                break

        axis = Line.CreateBound(XYZ(centroid[0],centroid[1],centroid[2]),XYZ(centroid[0],centroid[1],centroid[2]+1))
        angle = normal.AngleOnPlaneTo(prev_vector,axis.Direction)

        t = Transaction(doc,"SBox Align")
        t.Start()
        ElementTransformUtils.RotateElement(doc, second.Id, axis, -angle)
        t.Commit()

    elif second.Category.Name == "Views":

        if second.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Section":
            sections = [view for view in FilteredElementCollector(doc).OfClass(View).ToElements() if view.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Section"]
            section = [section for section in sections if second.Name == section.Name][0]
            axis = Line.CreateBound(section.Origin,XYZ(section.Origin[0], section.Origin[1], section.Origin[2]+1))
            angle = normal.AngleOnPlaneTo(section.ViewDirection, axis.Direction)
            t = Transaction(doc,"Section Align")
            t.Start()
            second.Location.Rotate(axis, -angle)
            t.Commit()

        elif second.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Elevation":
            elevations = [view for view in FilteredElementCollector(doc).OfClass(View).ToElements() if view.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Elevation"]
            elevation = [elevation for elevation in elevations if second.Name == elevation.Name][0]
            markers = FilteredElementCollector(doc).OfClass(ElevationMarker).ToElements()

            def m_view_ids(marker):
                view_ids = list()
                for index in range(0,4):
                    if marker.GetViewId(index).ToString() != "-1":
                        view_ids.append(marker.GetViewId(index))
                return(view_ids)

            for marker in markers:
                if elevation.Id in m_view_ids(marker):
                    ok_marker = marker
                    break
            t = Transaction(doc,"Elevation Align")
            t.Start()
            axis = Line.CreateBound(elevation.Origin,XYZ(elevation.Origin[0], elevation.Origin[1], elevation.Origin[2]+1))
            angle = normal.AngleOnPlaneTo(elevation.ViewDirection, axis.Direction)
            ok_marker.Location.Rotate(axis, -angle)
            t.Commit()
    else:
        print("Por favor, selecciona como segundo elemento una Scope Box, Sección o Alzado.")

except Autodesk.Revit.Exceptions.OperationCanceledException:
    pass
