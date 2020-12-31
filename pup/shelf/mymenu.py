
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import os

from ..library import utilsLib
from ..library import coreLib
from ..library import geometryLib
from ..library import kinematicsLib
from ..library import transformLib

MENU_NAME = "markingMenu"

delete_path = "C:/Users/Leo/Desktop/delete"



# ================================================
#                   marking menu
# ================================================


class MarkingMenu():


    def __init__(self):

        self._removeOld()
        self._build()

    def _removeOld(self):
        if cmds.popupMenu(MENU_NAME, ex=1):
            cmds.deleteUI(MENU_NAME)

    def _build(self):
        menu = cmds.popupMenu(MENU_NAME, mm = 1, b = 3, aob = 1, ctl = 1, alt=1, sh=0, p = "viewPanes", pmo=1, pmc = self._buildMarkingMenu)

    def _buildMarkingMenu(self, menu, parent):
        ## Radial positioned
        cmds.menuItem(p=menu, l="drawStyle_on", rp="SE", c=drawStyleSelOn)
        cmds.menuItem(p=menu, ob=1, c=drawStyleSelOff)

        cmds.menuItem(p=menu, l="snap", rp="E", c=snapTo, i="pointConstraint.svg")
        # cmds.menuItem(p=menu, ob=1, c=pointConOffset)

        cmds.menuItem(p=menu, l="save_selection", rp="NE", c=saveSelection)
        cmds.menuItem(p=menu, ob=1, c=loadSelection)


        # CONSTRAINTS
        cmds.menuItem(p=menu, l="parentConstraint", rp="NW", c=parentCon, i="parentConstraint.png")
        cmds.menuItem(p=menu, ob=1, c=parentConOffset)
        cmds.menuItem(p=menu, l="pointConstraint", rp="W", c=pointCon, i="pointConstraint.svg")
        cmds.menuItem(p=menu, ob=1, c=pointConOffset)
        cmds.menuItem(p=menu, l="scaleConstraint", rp="SW", c=scaleCon, i="scaleConstraint.png")
        cmds.menuItem(p=menu, ob=1, c=scaleConOffset)


        subMenu = cmds.menuItem(p=menu, l="North Sub Menu", rp="N", subMenu=1)
        cmds.menuItem(p=subMenu, l="North Sub Menu Item 1")
        cmds.menuItem(p=subMenu, l="North Sub Menu Item 2")

        cmds.menuItem(p=menu, l="save_geo", rp="S", c=save_geo)
        cmds.menuItem(p=menu, ob=1, c=load_geo)

        ## List
        cmds.menuItem(p=menu, l="select skin joints", c=selectSkinJoint, i="joint.svg")
        cmds.menuItem(p=menu, l="Follicle from point", c=follicleFromPoint, i="follicle.svg")
        cmds.menuItem(p=menu, l="Follicle from point CPS", c=follicleFromPointCPS, i="follicle.svg")


        cmds.menuItem(p=menu, l="Third menu item")
        cmds.menuItem(p=menu, l="Create poly cube", c="mc.polyCube()")





# ================================================
#                   FUNCTIONS
# ================================================


# ================================================
#                  RADIAL


def parentCon(*args):
    sel = pm.selected()
    pm.parentConstraint(sel[0], sel[1], n=str(sel[0] ) +"_PAC")
def parentConOffset(*args):
    sel = pm.selected()
    pm.parentConstraint(sel[0], sel[1], mo=True, n=str(sel[0] ) +"_PAC")


def pointCon(*args):
    sel = pm.selected()
    pm.pointConstraint(sel[0], sel[1], n=str(sel[0] ) +"_POC")
def pointConOffset(*args):
    sel = pm.selected()
    pm.pointConstraint(sel[0], sel[1], mo=True, n=str(sel[0] ) +"_POC")


def scaleCon(*args):
    sel = pm.selected()
    pm.scaleConstraint(sel[0], sel[1], n=str(sel[0] ) +"_SCC")
def scaleConOffset(*args):
    sel = pm.selected()
    pm.scaleConstraint(sel[0], sel[1], mo=True, n=str(sel[0] ) +"_SCC")


def selectSkinJoint(*args):
    selection = pm.selected()[0]
    objectSkin = mel.eval('findRelatedSkinCluster  ' +selection)
    joints = pm.skinCluster(objectSkin ,query=True ,inf=True)
    pm.select(joints)


def drawStyleSelOn(*args):
    [x.drawStyle.set(0) for x in pm.ls(selection=True ,type="joint")]


def drawStyleSelOff(*args):
    [x.drawStyle.set(2) for x in pm.ls(selection=True ,type="joint")]


Save__Selection = None
def saveSelection(*args):
    global Save__Selection
    if pm.selected():
        Save__Selection = pm.selected()


def loadSelection(*args):
    pm.select(Save__Selection)


# ================================================
#               LIST
def snapTo(*args):
    # from -- to
    sel = pm.selected()
    from_ = sel[:-1]
    to = sel[-1]
    if len(sel) > 1:
        for obj in from_:
            pm.delete(pm.parentConstraint(to ,obj))
    else:
        pm.delete(pm.parentConstraint(to ,from_))
        pm.select(from_)

def follicleFromPoint(*args):
    # surface first
    SRF = pm.selected()[-1]
    points = pm.selected()[:-1]

    kinematicsLib.follicle_from_position(SRF, points, cps=False, name=SRF)

def follicleFromPointCPS(*args):
    # surface first
    SRF = pm.selected()[-1]
    points = pm.selected()[:-1]

    kinematicsLib.follicle_from_position(SRF, points, cps=True, name=SRF)


def save_geo(*args):

    """

    :param args:
    :return:
    """
    path_geo = delete_path+"/saved_geo.obj"
    cmds.file(path_geo, pr=1, typ="OBJexport", es=1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")

def load_geo(*args):

    path_geo = delete_path+"/saved_geo.obj"
    if os.path.isfile(path_geo):
        cmds.file(path_geo, i=True)







