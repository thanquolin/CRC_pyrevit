# coding: utf8
"""Alinea scope boxes, section boxes, secciones y alzados a muros."""

#pyRevit info
__title__ = 'Ninja\nAlign'
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
clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)

import Autodesk.Revit.UI.Selection

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

one = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)
two = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element)
first = doc.GetElement(one)
second = doc.GetElement(two)
wall_normal = first.Orientation

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
angle = wall_normal.AngleOnPlaneTo(prev_vector,axis.Direction)

t = Transaction(doc,"SBox Align")
t.Start()
ElementTransformUtils.RotateElement(doc, second.Id, axis, -angle)
t.Commit()
