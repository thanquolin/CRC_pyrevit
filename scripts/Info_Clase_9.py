# A)

#--Importaciones en Dynamo--
import clr
# Librería con la mayoría de nodos de geometría de Dynamo
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
# Otras librerías:
# Color, Color Range 2D, Date Time, Time Span, IO, Formula, Logic, List, Math, Quadtree, String, Thread.
clr.AddReference('DSCoreNodes')
import DSCore
# Excel
clr.AddReference('DSOffice')
import DSOffice
# Para hacer referencia al documento actual
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
doc = DocumentManager.Instance.CurrentDBDocument
# Importar la API de Revit
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# --Comprehensions--
a = [e*2 for e in lista]
b = [e for e in lista if e > 2]
c = [e if e > 2 else 0 for e in lista]


# --TransacionManager vs Transactions en Dynamo. Subtransactions y Rollbacks--
# TransactionManager: Recomendado en Dynamo
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
TransactionManager.Instance.EnsureInTransaction(doc)
# Hacer cosas aquí
TransactionManager.Instance.TransactionTaskDone()


# B)

# --Clases y Métodos de interés (fuera de ejemplos)--
# Repasando opciones de métodos vistos ayer
# Podemos recoger elemenos por clase, además de por categoría
FilteredElementCollector.OfClass("clase")
# Nos devuelve el primer parámetro que encuentre con ese nombre
LookupParameter("Parámetro")
# Modo independiente del idioma de Revit
get_Parameter(BuiltInParameter)
# Modificar el Tipo de un Elemento
Element.ChangeTypeId()
# Vista actual
doc.ActiveView
# Cómo obtener el número detrás de un ElementId
ElementId.IntegerValue
# Mover un Elemento en el Modelo
ElementTransformUtils.MoveElement(doc,ElementId,XYZ)
ElementTransformUtils.Rotate(doc,ElementId,XYZ)
# Crear un Elemento en el Modelo
doc.Create.NewFamilyInstance(...)
Wall.Create(...)

# --Métodos destacados de ejemplos--
# -PYREVIT: INTRODUCCIÓN-
https://www.notion.so/Developer-Docs-2c88f3ecccde422d9504e20b6b9e04f8

# -Reset Filtros de Fase-
# Fases del modelo
doc.phases
# Eliminar un Elemento del Modelo
doc.Delete(ElementId)
# Importar clases de .NET
import System.Collections.Generic as Colecciones
# Overload/Sobrecarga en funciones. Elegir "versión" de la función
Función.Overloads.Functions[Índice](Argumentos)

# -Localización de Elementos en Habitaciones. La montamos con pyRevit-
# Métodos de localización de elementos
# Ojo con este. La location de un wall es una línea, por ejemplo
Element.Location.Point
# Para puntos de cálculo de habitación
FamilyInstance.HasSpatialElementCalculationPoint
FamilyInstance.GetSpatialElementCalculationPoint()
FamilyInstance.GetSpatialElementFromToCalculationPoint()
doc.GetRoomAtPoint(XYZ)
# Métodos que usan Inserción o RCP
Silla.Room[phase]
Puerta.FromRoom[phase]
# Más información de FamilyInstances
FamilyInstance.FacingOrientation
FamilyInstance.LevelId
FamilyInstance.UniqueId

# -Alinear Vistas-
# Selecciones
Selection
# Mostrar Ventanas de Aviso de Revit
Autodesk.Revit.UI.TaskDialog

# -Creación Muros de Carpintería-
# Analizamos los dos métodos

# -Colores DWG - Orientación-
# Los DWG son categorías en nuestro modelo
# Movemos el dwg para regenerarlo

# -Ejemplo de uso de clases-
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

class pmaRoom:
	"""
		Habitación obtenida a partir del PMA. Para crear un ejemplar hay que dar una lista de líneas del Excel del PMA:

	"""

	def __init__(self, pars):
		self.code = pars[0]
		self.uFuncional = pars[2]
		self.aFuncional = pars[4]
		self.subarea = pars[6]
		self.departamento = pars[8]
		self.nombre = pars[10]
		self.numEjemplar = pars[11]
		self.numTotalEjemplares = pars[12]
		self.aEjemplar = pars[13]
		self.aTotalEjemplares = pars[14]
		self.observaciones = pars[15]
		self.gCode = pars[0].split("-")[0]

	def genList(self):
		return self.aTotalEjemplares

#Filtramos líneas vacías
elements = [e for e in IN[0] if e[0]]

res = list()
for element in elements:
	res.append(pmaRoom(element))

OUT = res

# -Acabados Verticales de Habitaciones-
# Veremos cómo obtener room boundaries
# Métodos para localizar anfitriones e inserciones
Wall.FindInserts(Argumentos)
FamilyInstance.Host
