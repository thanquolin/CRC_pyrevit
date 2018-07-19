# coding: utf8
"""Borra todos los filtros de fase y deja uno llamado Coordinación, donde se muestra todo con Overrides. Si ya existe, deja el existente tal y como estaba y no crea ninguno."""
__title__ = 'Reset Filtros\nde Fase'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
import pyrevit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

default_filter_name = "Coordinación"

#Se crea el colector antes que el nuevo filtro, pero se borran cuando éste ya está creado y puede quedarse como default
old_filters = FilteredElementCollector(doc).OfClass(PhaseFilter).ToElements()
old_filters_names = [filter.Name for filter in old_filters]
t = Transaction(doc,"Reset Filtros de Fase")
t.Start()
if default_filter_name in old_filters_names:
    filters_to_delete = list()
    for filter in old_filters:
        if filter.Name == default_filter_name:
            pass
        else:
            filters_to_delete.append(filter)
    for filter in filters_to_delete:
        doc.Delete(filter.Id)
else:
    new_filter = PhaseFilter.Create(doc,default_filter_name)
    new_filter.SetPhaseStatusPresentation(ElementOnPhaseStatus.New,PhaseStatusPresentation.ShowOverriden)
    new_filter.SetPhaseStatusPresentation(ElementOnPhaseStatus.Existing,PhaseStatusPresentation.ShowOverriden)
    new_filter.SetPhaseStatusPresentation(ElementOnPhaseStatus.Demolished,PhaseStatusPresentation.ShowOverriden)
    new_filter.SetPhaseStatusPresentation(ElementOnPhaseStatus.Temporary,PhaseStatusPresentation.ShowOverriden)
    for filter in old_filters:
        doc.Delete(filter.Id)
t.Commit()
