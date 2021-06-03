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

				
#Open, save and close a Revit file 
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document
app = doc.Application
path = "C:\\Users\\Carlos\\Desktop\\Project1.rvt"
open_options = OpenOptions()
filepath = FilePath(path)
newdoc = app.OpenDocumentFile(filepath,open_options)
#Do stuff
#Close() saves the file if there were any changes
newdoc.Close()

# Getting linked documents
fec = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements()			
link = fec[0]
linkDoc = lik.GetLinkDocument()
				
#Get current selection
from Autodesk.Revit.UI import UIApplication
__revit__.ActiveUIDocument.Selection.GetElementIds()

				
#Purge unused elements
doc = __revit__.ActiveUIDocument.Document
purgeGuid = 'e8c63650-70b7-435a-9010-ec97660c1bda'
purgableElementIds = []
performanceAdviser = PerformanceAdviser.GetPerformanceAdviser()
ruleId = None
allRuleIds = performanceAdviser.GetAllRuleIds()
for rule in allRuleIds:
    if str(rule.Guid) == purgeGuid:
        ruleId = rule
        break
import System.Collections.Generic as col
ruleIds = col.List[PerformanceAdviserRuleId]([ruleId])
for i in range(4):
    # Executes the purge
    failureMessages = performanceAdviser.ExecuteRules(doc, ruleIds)
    if failureMessages.Count > 0:
        # Retrieves the elements
        purgableElementIds = failureMessages[0].GetFailingElements()
# Deletes the elements
t = Transaction(doc,"Purge")
t.Start()
try:
    doc.Delete(purgableElementIds)
except:
    for e in purgableElementIds:
        try:
            doc.Delete(e)
        except:
            pass
t.Commit()
				

#Distinguishing between "wrong" rooms
#Redundant Rooms have Location and Boundary Segments
#Not enclosed Rooms do not have Boundary Segments
#Not placed Rooms do not have Location
#None of the three have Area
				
				
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
				
#Renaming files with python
import os
os.rename(r'previous path', r'new path')
				
#Changing current working directory in python
os.chdir(r'dir path')
				
#Working with utf8 csv
import codecs
import csv
#When opening, 'w' to write, 'r' to read, 'w+' to read and write used as mode= argument
file = codecs.open(r'file path', encoding = 'utf8', errors = 'replace')
#Reading				
reader = csv.reader(file)
for row in reader:
	print(row)
#Writing
writer = csv.writer(file)
for row in whatever:
	writer.writerow(row)
				
#If \ufeff appears at the beginning of the file, we have to use the right encoding
f = open('file', mode='r', encoding='utf-8-sig')
