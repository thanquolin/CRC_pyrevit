import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('DSCoreNodes')
import DSCore
from DSCore import *

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument


#Casting en python para sólidos (no podemos usar "as").
solids = [solid for solid in el.get_Geometry(Options())]

#Para utilizar un overload concreto de un método de la api, hay que especificarlo en el índice.
#Elemento.Método.Overloads.Functions[index](resto de variables)
