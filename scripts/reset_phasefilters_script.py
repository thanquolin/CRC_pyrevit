# -*- coding: utf-8 -*-
"""Deletes all phase filters but one, renamed as you please, where all is shown and overrriden.\
If such filter name already exists, it is left as is, without creating another one."""
__title__ = 'Phase Filters\nReset'
__author__  = 'Carlos Romero Carballo'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument



default_filter_name = forms.ask_for_string(
    default='View All',
    prompt='Enter Phase Filter name:',
    title='Phase Filter Reset'
)

old_filters = FilteredElementCollector(doc).OfClass(PhaseFilter).ToElements()
old_filters_names = [filter.Name for filter in old_filters]

t = Transaction(doc,"Phase Filter Reset")
t.Start()
if default_filter_name in old_filters_names:
    [doc.Delete(filter.Id) for filter in old_filters if filter.Name != default_filter_name]
else:
    new_filter = PhaseFilter.Create(doc,default_filter_name)
    [new_filter.SetPhaseStatusPresentation(eval("ElementOnPhaseStatus." + categ),PhaseStatusPresentation.ShowOverriden)\
     for categ in ["New","Existing","Demolished","Temporary"]]
    [doc.Delete(filter.Id) for filter in old_filters]
t.Commit()
