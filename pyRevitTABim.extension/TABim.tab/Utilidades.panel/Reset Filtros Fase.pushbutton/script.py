# coding: utf8
"""Borra todos los filtros de fase y deja uno llamado Coordinación, donde se muestra todo con Overrides. Si ya existe, deja el existente tal y como estaba y no crea ninguno."""
__title__ = 'Reset Filtros\nde Fase'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

default_filter_name = "Coordinación"
old_filters = FilteredElementCollector(doc).OfClass(PhaseFilter).ToElements()
old_filters_names = [filter.Name for filter in old_filters]

t = Transaction(doc,"Reset Filtros de Fase")
t.Start()
if default_filter_name in old_filters_names:
    [doc.Delete(filter.Id) for filter in old_filters if filter.Name != default_filter_name]
else:
    new_filter = PhaseFilter.Create(doc,default_filter_name)
    [new_filter.SetPhaseStatusPresentation(eval("ElementOnPhaseStatus." + categ),PhaseStatusPresentation.ShowOverriden) for categ in ["New","Existing","Demolished","Temporary"]]
    [doc.Delete(filter.Id) for filter in old_filters]
t.Commit()
