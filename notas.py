import clr

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('DSCoreNodes')
from DSCore import *

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument


#Sólidos con python (no podemos usar "as").

solids = [solid for solid in el.get_Geometry(Options())]

#O bien
options = Options()
geom = foo.Geometry[options]

#Obtener el Workset de un Elemento, de Andreas Dieckmann
def GetWorkset(item):
	if hasattr(item, "WorksetId"): return item.Document.GetWorksetTable().GetWorkset(item.WorksetId)
	else: return None

#Para utilizar un overload concreto de un método de la api, especificando índice del overload.
#Elemento.Método.Overloads.Functions[índice](resto de variables)

solid_A.Intersect.Overloads.Functions[2](solid_B)

#Para importar las colecciones de .Net y poder darle a la api ICollections

import System.Collections.Generic as col
doc.Delete(col.List[ElementId]([ElementId(1234),ElementId(3456]))

				
# Funciones para ahorrar tiempo
				
def parFtM(element, parameterName):
	"""Gets the element parameter value as a double in meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_METERS)

def parSFtSM(element, parameterName):
	"""Gets the element parameter value as a double in square meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_SQUARE_METERS)
				
def parCFtCM(element, parameterName):
	"""Gets the element parameter value as a double in cubic meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_CUBIC_METERS)
				
def elFec(catName):
	"""Returns the instance (no type objects) filtered element collector of a category. Assumes "doc" as the current document variable"""
	return eval("FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_" + catName + ").WhereElementIsNotElementType().ToElements()")


				
	
