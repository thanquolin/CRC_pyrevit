"""Collection of python Revit API notes""" 

#Dynamo and Designscript python script node imports
import clr

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('DSCoreNodes')
from DSCore import *

#To work with Revit API classes and do transactions inside the script node
#Better to use TransactionManager than Revit API Transactions in dynamo scripts
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
doc = DocumentManager.Instance.CurrentDBDocument
from RevitServices.Transactions import TransactionManager
TransactionManager.Instance.EnsureInTransaction(doc)
#Do stuff
TransactionManager.Instance.TransactionTaskDone()


#Obtain solids inside an Element's Geometry
#We can't use "as" with python, as in "item as solid"
solids = [solid for solid in el.get_Geometry(Options())]

#Also 
options = Options()
geom = foo.Geometry[options]


#Get Element's Workset
def GetWorkset(item):
	if hasattr(item, "WorksetId"): return item.Document.GetWorksetTable().GetWorkset(item.WorksetId)
	else: return None


#To use a specific overload of an API method
#Element.Method.Overloads.Functions[index](rest of arguments)
solid_A.Intersect.Overloads.Functions[2](solid_B)


#To import .Net Collections to use when the Revit API ask for types we don't have in python
#In this example, we need a .NET ElementId List, and not a python list, for this delete overload
import System.Collections.Generic as col
doc.Delete(col.List[ElementId]([ElementId(1234),ElementId(3456]))

				
#Functions				
def lenPar(element, parameterName):
	"""Gets the element parameter value as a double in meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_METERS)

def areaPar(element, parameterName):
	"""Gets the element parameter value as a double in square meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_SQUARE_METERS)
				
def volPar(element, parameterName):
	"""Gets the element parameter value as a double in cubic meters"""
	return UnitUtils.ConvertFromInternalUnits(element.GetParameters(parameterName)[0].AsDouble(), DisplayUnitType.DUT_CUBIC_METERS)
				
def catElements(catName):
	"""Returns the instance (no type objects) filtered element collector of a category. Assumes "doc" as the current document variable"""
	return eval("FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_" + catName + ").WhereElementIsNotElementType().ToElements()")


				
	
