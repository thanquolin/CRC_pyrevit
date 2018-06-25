# coding: utf8
"""Elimina la combinación de parámetros 'Tipo de Carpintería' y 'Código Carpintería' del inicio del nombre de los tipos de Puertas o Ventanas cargados en el modelo.
No usar dobles guiones en ninguno de los dos parámetros ni en los nombres de tipo."""
#pyRevit info
__title__ = 'Limpiar\nCodificación\nCarpinterías'
__author__  = 'Carlos Romero Carballo'


from pyrevit.coreutils import Timer
timer = Timer()

import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


window_types = list({ type for type in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsElementType()})
door_types = list({ type for type in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsElementType()})
types = window_types + door_types
type_names = [type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for type in types]

if len(types) == 0:
    print("No hay familias de ventanas o puertas cargadas en el modelo.")
else:
    t = Transaction(doc,"Eliminación Codificación Carpinterías")
    t.Start()
    for type, name in zip(types, type_names):
        if "--" not in name:
            pass
        else:
            clean_name = name[name.index("--")+2:]
            type.Name = clean_name
            print("Tipo '" + name + "' actualizado a '" + clean_name + "'.")
    t.Commit()

#report time
endtime ="\nHe tardado: " + str(timer.get_time()) + " segundos en llevar a cabo esta tarea."
print(endtime)
