# -*- coding: utf-8 -*-
"""Aligns scope boxes, sections and elevations to walls, model lines and grids. Select the reference first, and then the scope box or view."""

__title__ = 'View/ScopeBox\nAlign'
__author__  = 'Carlos Romero Carballo'

# import sys
# pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
# sys.path.append(pyt_path)

import clr
clr.AddReference('RevitAPI')

#Why does 'RevitNodes' allow to import Revit, which allow to import Revit.GeometryConversion?
clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)

from Autodesk.Revit.DB import *
import Autodesk.Revit.UI.Selection

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

try:
    #PickObject returns a Reference, GetElement gets the Element from the Reference
    pick_one = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)
    pick_two = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)
    first = doc.GetElement(pick_one)
    second = doc.GetElement(pick_two)

    #First element selection
    #Is it a Wall?
    if first.Category.Name == "Walls":
        normal = first.Orientation
    #Is it a Grid?:
    elif first.Category.Name == "Grids":
        #(Y,-X,Z) is perpendicular to XYZ
        normal = XYZ(first.Curve.Direction[1], -first.Curve.Direction[0], first.Curve.Direction[2])
    else:
        #Is it a Line?
        try:
            normal = XYZ(first.GeometryCurve.Direction[1],-first.GeometryCurve.Direction[0],first.GeometryCurve.Direction[2])
        #If everything fails...
        except:
            print("Please, select a wall, model line or grid as first element.")

    #Second element selection and transactions
    #Is it a Scope Box?
    #Centroid of Scope Box
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
        #Sloppy way of getting Scope Box's orientation
        for line in geo:
            if line.Direction[2] == 0:
                prev_vector = line.Direction
                break

        axis = Line.CreateBound(XYZ(centroid[0],centroid[1],centroid[2]),XYZ(centroid[0],centroid[1],centroid[2]+1))
        angle = normal.AngleOnPlaneTo(prev_vector,axis.Direction)

        t = Transaction(doc,"Scope Box Align")
        t.Start()
        ElementTransformUtils.RotateElement(doc, second.Id, axis, -angle)
        t.Commit()
    #Is it a view?
    elif second.Category.Name == "Views":
        #Is it a section?
        if second.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Section":
            sections =  [view for view in FilteredElementCollector(doc).OfClass(View).ToElements() if view.get_Parameter(Autodesk.Revit.DB.BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == "Section"]
            section = [section for section in sections if second.Name == section.Name][0]
            axis = Line.CreateBound(section.Origin,XYZ(section.Origin[0], section.Origin[1], section.Origin[2]+1))
            angle = normal.AngleOnPlaneTo(section.ViewDirection, axis.Direction)
            #Transaction
            t = Transaction(doc,"Section Align")
            t.Start()
            second.Location.Rotate(axis, -angle)
            t.Commit()
        #Is it an Elevation?
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
            #Transaction
            t = Transaction(doc,"Elevation Align")
            t.Start()
            axis = Line.CreateBound(elevation.Origin,XYZ(elevation.Origin[0], elevation.Origin[1], elevation.Origin[2]+1))
            angle = normal.AngleOnPlaneTo(elevation.ViewDirection, axis.Direction)
            ok_marker.Location.Rotate(axis, -angle)
            t.Commit()
    #Is it something else?
    else:
        print("Please, select a Scope Box, Section or Elevation as second element.")
#What if the user cancels the operation?
except Autodesk.Revit.Exceptions.OperationCanceledException:
    pass
