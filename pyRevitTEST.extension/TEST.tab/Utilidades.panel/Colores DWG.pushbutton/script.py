# -*- coding: utf-8 -*-
"""Modifica los colores de las capas de los DWG importados
 si sus nombres están en la plantilla "plantilla_capas.csv"
 (primera columna nombres, segunda columna código 0-255 de color)
 incluida en la misma carpeta que el script."""

__title__ = 'Aplicar Colores de\nPlantilla a DWG'
__author__  = 'Carlos Romero Carballo'

from pyrevit.coreutils import Timer
timer = Timer()
import csv
import clr
import os.path
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
plantilla_dwg_path = "C:\ProgramData\pyRevit\pyRevit-v45\pyRevit\extensions\pyRevitTABim.extension\TABim.tab\Utilidades.panel\Colores DWG.pushbutton\dwg_to_rgb.csv"
plantilla_capas_path = "C:\ProgramData\pyRevit\pyRevit-v45\pyRevit\extensions\pyRevitTABim.extension\TABim.tab\Utilidades.panel\Colores DWG.pushbutton\plantilla_capas.csv"
cads_categories = [cat for cat in doc.Settings.Categories if cat.Name.ToString().endswith(".dwg")]
capas_dwg = [item for sublist in [cat.SubCategories for cat in doc.Settings.Categories if cat.Name.ToString().endswith(".dwg")] for item in sublist]

if len(capas_dwg) == 0:
    print("No hay .dwg importados en el modelo. Ningún cambio que hacer.")
elif not os.path.exists(plantilla_dwg_path):
    print("No se encuentra 'dwg_to_rgb.csv' en el directorio del script.")
elif not os.path.exists(plantilla_capas_path):
    print("No se encuentra 'plantilla_capas.csv' en el directorio del script.\nPara abrir el directorio,\
     hacer click en el botón del script mientras se pulsa la tecla ALT.\nMás información en el tooltip del script.")

else:
    plantilla_dwg = {}
    with open(plantilla_dwg_path) as csvfile:
        reader = csv.reader(csvfile, delimiter = " ", quotechar = "|")
        for row in reader:
            decomp = row[0].split(";")
            plantilla_dwg[decomp[0]] = [decomp[1], decomp[2], decomp[3]]

    plantilla_capas = {}
    with open(plantilla_capas_path) as csvfile:
        reader = csv.reader(csvfile, delimiter = " ", quotechar = "|")
        for row in reader:
            decomp = row[0].split(";")
            plantilla_capas[decomp[0]] = decomp[1]

    plantilla_colores = {}
    for key in plantilla_capas.keys():
        code = plantilla_dwg[plantilla_capas[key]]
        plantilla_colores[key] = Color(int(code[0]),int(code[1]),int(code[2]))

    t = Transaction(doc,"Cambio Colores DWG")
    t.Start()
    for capa in capas_dwg:
        if capa.Name in plantilla_colores.keys():
            capa.LineColor = plantilla_colores[capa.Name]
            print("Color de Capa '{}' cambiado en '{}'.".format(capa.Name,capa.Parent.Name))
    #Movemos los cad para que se recarguen, mostrando los cambios en color.
    for cad in [item for sublist in [FilteredElementCollector(doc).OfCategoryId(cat.Id).WhereElementIsNotElementType().ToElements()\
     for cat in doc.Settings.Categories if cat.Name.ToString()[-4:] == ".dwg"] for item in sublist]:
        if cad.Pinned == False:
            ElementTransformUtils.MoveElement(doc, cad.Id, XYZ.BasisX)
            ElementTransformUtils.MoveElement(doc, cad.Id, XYZ.BasisX.Negate())
        else:
            cad.Pinned = False
            ElementTransformUtils.MoveElement(doc, cad.Id, XYZ.BasisX)
            ElementTransformUtils.MoveElement(doc, cad.Id, XYZ.BasisX.Negate())
            cad.Pinned = True
    t.Commit()

endtime ="\nHe tardado " + str(round(timer.get_time(),2)) + " segundos en llevar a cabo esta tarea."
print(endtime)
