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


#Casting en python para sólidos (no podemos usar "as").

solids = [solid for solid in el.get_Geometry(Options())]

#Para utilizar un overload concreto de un método de la api, especificando índice del overload.
#Elemento.Método.Overloads.Functions[índice](resto de variables)

solid_A.Intersect.Overloads.Functions[2](solid_B)
