#Work in progress!!

"""Inscribe en el parametro "MED_Net vertical finish room area" de todas las habitaciones del modelo el area neta de acabados verticales."""
"""Se cruzan las caras verticales de la geometria de la habitacion con las caras verticales de los muros que forman sus boundaries. No funciona para habitaciones para las que Revit no puede crear geometria."""

__title__ = 'Net Room Vertical\nFinish Calculation'
__author__ = 'Carlos Romero'

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

#from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory
import Autodesk.Revit.DB as DB
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
clr.AddReference('DSCoreNodes')
import DSCore
from DSCore import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#imports para la funcion de Clockwork (ver abajo), no estoy seguro de cuales se usan
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager



rooms = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

#Metodos del nodo de dynamo (por si hubiese que usar la segunda)
"""#method #1 - get boundary segments
    try:
		for boundarylist in item.GetBoundarySegments(options):
			for boundary in boundarylist:
				blist.append(doc.GetElement(boundary.ElementId))
				if version > 2016:
					clist.append(boundary.GetCurve().ToProtoType())
				else:
					clist.append(boundary.Curve.ToProtoType())
	except:
		pass
	#method #2 - spatial element geometry calculator
	try:
		results = calculator.CalculateSpatialElementGeometry(item)
		for face in results.GetGeometry().Faces:
			for bface in results.GetBoundaryFaceInfo(face):
				blist.append(doc.GetElement(bface.SpatialBoundaryElement.HostElementId))"""

for room in rooms:
    #primero obtenemos las caras verticales de la habitacion
    room_faces = SpatialElementGeometryCalculator(doc).CalculateSpatialElementGeometry(room).GetGeometry().Faces
    room_vertical_faces = list()
    for face in room_faces:
        if face.ComputeNormal(UV())[2] == 0:
            room_vertical_faces.append(face)
        else:
            pass

    #despues obtenemos las caras verticales de los muros que son boundary de la habitacion
    #para obtener los solidos de los muros, utilizamos una funcion sacada del nodo "Geometry+" de Clockwork, dynamo

    def convert_geometry_instance(geo, elementlist):
	for g in geo:
		if str(g.GetType()) == 'Autodesk.Revit.DB.GeometryInstance':
			elementlist = convert_geometry_instance(g.GetInstanceGeometry(), elementlist)
		else:
			try:
				if g.Volume != 0:
					elementlist.append(g)
			except:
				pass
	return elementlist

    room_walls = list()
    bound_list = room.GetBoundarySegments(SpatialElementBoundaryOptions())
    for grupo in bound_list:
        for boundary_element in grupo:
            if doc.GetElement(boundary_element.ElementId).Category.Name == "Walls":
                room_walls.append(doc.GetElement(boundary_element.ElementId))
            else:
                pass
    wall_faces = list()
    for wall in room_walls:
        wall_solid = convert_geometry_instance(wall.get_Geometry(Options()),list())
        for solid in wall_solid:
                wall_faces.append(solid.Faces)
    wall_vertical_faces = list()
    for wall_array in wall_faces:
        for wall_face in wall_array:
            if wall_face.ComputeNormal(UV())[2] == 0:
                wall_vertical_faces.append(face)
            else:
                pass
    #cruzamos las caras (teniendo en cuenta sus normales)
    def normals_opposed(vector1, vector2):
        if vector1[0] == -1*vector2[0] and vector1[1] == -1*vector2[1] and vector1[2] == -1*vector2[2]:
            print (str(vector1)+" , "+str(vector2) +".")
            print("True")
            return True
        else:
            print (str(vector1)+" , "+str(vector2) +".")
            print("False")
            return False


    intersections = list()
    for rface in room_vertical_faces:
        for wface in wall_vertical_faces:
            intersections.append(Geometry.Intersect(rface.get_Geometry(Options())),wface.get_Geometry(Options()))
            """if normals_opposed(rface.ComputeNormal(UV()),wface.ComputeNormal(UV())):
                intersections.append(rface.Intersect(wface))
            else:
                pass"""
    print(intersections)
    results = list()
    for i in intersections:
        if str(i) == "Autodesk.Revit.DB.FaceIntersectionFaceResult.Intersecting":
            results.append(i)
            print(str(i))

#for timing
endtime ="It took me " + str(timer.get_time()) + " seconds to calculate this."
print(endtime)
