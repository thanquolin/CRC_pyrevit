# coding: utf8
"""Añade o actualiza la combinación de parámetros 'Tipo de Carpintería' y 'Código Carpintería' delante del nombre de los tipos de Puertas o Ventanas que tengan instancias
modeladas. No usar dobles guiones en ninguno de los dos parámetros ni en los nombres de tipo."""
#pyRevit info
__title__ = 'Añadir/Actualizar\nCodificación\nCarpinterías'
__author__  = 'Carlos Romero Carballo'

import clr
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#Selection of family types of selected element category.
#We select all model instances instead of types to affect only types of modelled instances.
window_type_ids = list({ id.GetTypeId() for id in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType()})
door_type_ids = list({ id.GetTypeId() for id in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()})
type_ids = window_type_ids + door_type_ids

type_names = ["" if type(doc.GetElement(id).get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()) != type("a") else doc.GetElement(id).get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for id in type_ids]
type_cod_carp = ["" if type(doc.GetElement(id).LookupParameter("Código Carpintería").AsString()) != type("a") else doc.GetElement(id).LookupParameter("Código Carpintería").AsString() for id in type_ids]
type_tipo_carp = ["" if type(doc.GetElement(id).LookupParameter("Tipo de Carpinteria").AsString()) != type("a") else doc.GetElement(id).LookupParameter("Tipo de Carpinteria").AsString() for id in type_ids]

if len(type_ids) == 0:
    print("No hay instancias de ventanas o puertas en el modelo")
else:
    t = Transaction(doc,"Codificación Carpinterías")
    t.Start()
    for id, cod, type, name in zip(type_ids, type_cod_carp, type_tipo_carp, type_names):
        if "--" not in name:
            new_name = type + cod + "--" + name
            doc.GetElement(id).Name = new_name
            print("Tipo '" + name + "' cambiado a '" + new_name + "'.")
        else:
            updated_name = type + cod + name[name.index("--")-1:]
            doc.GetElement(id).Name = updated_name
            print("Tipo '" + name + "' actualizado a '" + updated_name + "'.")
    t.Commit()
