"""Adds correspondent Mark Type (and a double hyphen) at the beginning of type names of all families of the category of the selected item which have modelled instances. Available categories are Doors, Windows and Walls. Do not use double hyphens in Mark Type or Type Names."""
#pyRevit info
__title__ = 'Add Mark Type\nto Type Name'
__author__  = 'Carlos Romero Carballo'


# Tool activates when at least one element is selected
__context__ = 'Selection'

#IMPORTS

#for timing
from pyrevit.coreutils import Timer
timer = Timer()

#for the script to work
import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

#VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

available_categories = ["Windows","Doors","Walls"]

#Selection of family types of selected element category.
#We select all model instances instead of types to affect only types of modelled instances.
selection = [ doc.GetElement( elId ) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds() ]
if len(selection) > 1:
    print("You have selected more than one element. Please select only one element of one of the available categories.")
elif doc.GetElement(selection[0].GetTypeId()).Category.Name not in available_categories:
    print("You have selected an instance of an unavailable category, please select an instance of an available category (" + ",".join(available_categories) + ").")
else:
    instances = FilteredElementCollector(doc).OfCategory(eval("BuiltInCategory.OST_"+str(selection[0].Category.Name))).WhereElementIsNotElementType()
    types_ids = list({ id.GetTypeId() for id in instances})
    type_names = ["" if type(doc.GetElement(id).LookupParameter("Type Name").AsString()) != type("a") else doc.GetElement(id).LookupParameter("Type Name").AsString() for id in types_ids]
    type_marks = ["" if type(doc.GetElement(id).LookupParameter("Type Mark").AsString()) != type("a") else doc.GetElement(id).LookupParameter("Type Mark").AsString() for id in types_ids]

    t = Transaction(doc,"Type Names Change")
    t.Start()

    for id, mark, name in zip(types_ids, type_marks, type_names):
        if "--" not in name:
            new_name = mark + "--" + name
            doc.GetElement(id).Name = new_name
            print("Type '" + name + "' changed to '" + new_name + "'.")
        else:
            updated_name = mark + name[name.index("--")-1:]
            doc.GetElement(id).Name = updated_name
            print("Type '" + name + "' updated to '" + updated_name + "'.")
    t.Commit()

#report time
endtime ="\nIt took me: " + str(timer.get_time()) + " seconds to perform this task."
print(endtime)
