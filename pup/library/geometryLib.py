import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os
import json

from . import transformLib
from . import constraintsLib
from . import utilsLib


colourIndexDict = {'grey': 0, 'black': 1, 'darkgrey': 2, 'lightgrey': 3, 'plum': 4, 'darkblue': 5, 'blue': 6,
                   'darkgreen': 7, 'darkpurple': 8, 'brightpink': 9, 'darkorange': 10, 'darkred': 11, 'mediumred': 12,
                   'red': 13, 'green': 14, 'mediumblue': 15, 'white': 16, 'yellow': 17, 'lightblue': 18,
                   'lightgreen': 19, 'pink': 20, 'tan': 21, 'lightyellow': 22, 'mediumgreen': 23,
                   'brown': 24, 'darkyellow': 25, 'leafgreen': 26, 'mintgreen': 27, 'turquoise': 28,
                   'navyblue': 29, 'purple': 30, 'winered': 31,

                   'left': 6,
                   'L': 6,
                   'l': 18,

                   'right': 13,
                   'R': 13,
                   'r': 20,

                   'center': 17,
                   'C': 17,
                   'c': 25,
                   'offset': 18}

rotation_axis_dict = {'xyz':0, 'yzx':1, 'zxy':2, 'xzy':3, 'yxz':4, 'zyx':5}

shape_path = os.path.sep.join((os.path.dirname(__file__)).split(os.path.sep)[:-1])+"{0}assets{0}shapes{0}".format(os.path.sep)
shapes_json = utilsLib.import_latest(shape_path, "shapes_dict_v*.json")
def make_control_shape(shapeType=None,
                       name='temp',
                       position=None,
                       rotation=True,
                       scale=1.0,
                       offsets=1,
                       rotate_order="xyz",
                       colour=None,
                       replaceThisNode=None,
                       referenceNode=None,
                       addOffsetGroup=True):
    """

        Description:
            Creates a shaped control curve.

        Flags:
            shapeType (string): What type of shape to create, sphere, locator, arrow etc...
                                use "list=True" to see options.
            name (string): A name for the control.
            position (string): A node to use to place the control
            rotation (bool): use the rotation of the "position" node to align it
            scale (float): A value that sets the size in XYZ. The natural build state of the control at 1.0, is also
                            one unit in Maya.
            colour (string): A colour to give the control. You can also give it a side like, "left" or "right",
                            or the value of "self.side" from a pac part file (L, R, or C) which will auto-colour it.
            replaceThisNode (string): If specified, the new control shape will replace the given one.
            addOffsetGroup (bool): Put the new control under a zeroing grouop node.
            listShapes (bool): If True, prints and returns the shape types as a list. These represent the
                                dictionary keys.
            listColours (bool): Similarly, will print out the colour key options.

        Returns:
            list=True: returns the list of json dictionary keys and nothing else, otherwise the name of the new control.

    """

    pm.select(clear=True)

    if shapeType is not 'circle':
        with open(shapes_json) as json_file:
            data = json.load(json_file)
        theControl = pm.curve(name=name, p=data[shapeType][2], degree=data[shapeType][0], per=data[shapeType][1])
    else:
        theControl = pm.circle(name=name, degree=3, tol=0.01, sections=8, ch=False, sw=360, nr=(0, 1, 0), radius=1)[0]

    pm.select(clear=True)

    pm.setAttr('{0}.scale'.format(theControl), scale, scale, scale)
    pm.setAttr(theControl+".rotateOrder", k=True)
    pm.setAttr(theControl+".rotateOrder", rotation_axis_dict[rotate_order.lower()])
    pm.makeIdentity(theControl, apply=True, t=True, s=True, r=True)

    theControlShape = pm.listRelatives(theControl, shapes=True)[0]

    theControlShape = pm.rename(theControlShape, '{0}Shape'.format(theControl))

    if colour:
        # colour = colour.lower()

        if colour in colourIndexDict.keys():
            pm.setAttr('{0}.overrideEnabled'.format(theControlShape), 1)
            pm.setAttr('{0}.overrideColor'.format(theControlShape), colourIndexDict[colour])

    scalePosition = (0, 0, 0)

    if position and pm.objExists(position):
        scalePosition = pm.xform(position, query=True, t=True, ws=True)

        if not rotation:
            pm.delete(pm.parentConstraint(position, theControl, skipRotate=('x', 'y', 'z'), maintainOffset=False))
        else:
            pm.delete(pm.parentConstraint(position, theControl, maintainOffset=False))

    # cmds.scale(scale, scale, scale, str(theControlShape.cv[:]), relative=True, pivot=scalePosition, scaleXYZ=True)

    pm.select(clear=True)

    if addOffsetGroup:
        if referenceNode:
            transformLib.null_grps(node=theControl, referenceNode=referenceNode)
        else:
            for itr in range(offsets):
                if itr == 0:
                    transformLib.null_grps(node=theControl)
                else:
                    parent = [pm.listRelatives(theControl, p=True)[0] for x in range(itr)][-1]
                    transformLib.null_grps(node=parent, name=(pm.listRelatives(theControl, p=True)[0])[:-3]+"offset%s_GRP"%itr)

        pm.makeIdentity(theControl, apply=True, t=True, s=True, r=True)

    pm.setAttr('{0}.isHistoricallyInteresting'.format(theControlShape), False)

    pm.select(clear=True)

    if replaceThisNode:
        pm.delete(pm.pointConstraint(replaceThisNode, theControl, maintainOffset=False))

        controlShape = pm.listRelatives(theControl, shapes=True)
        oldShapes = pm.listRelatives(replaceThisNode, shapes=True)

        pm.delete(oldShapes)

        resultingShape = pm.rename(controlShape[0], oldShapes[0])

        pm.parent(resultingShape, replaceThisNode, shape=True, relative=True)

        pm.delete(theControl)

    pm.select(clear=True)

    return theControl

def makeLine(points, degree=1, name="created_CRV", template=True, keep_LOC=True):
    """
    makes a line between objects/components

    """

    pos = (0, 0, 0)
    position = []
    locs = []

    for itr, point in enumerate(points):
        position.append(pos)

        loc = pm.spaceLocator(name=point + name + "_LOC")
        pm.delete(pm.parentConstraint(point, loc))

        locs.append(loc)

        pm.parent(loc, point)
        pm.setAttr(loc + ".visibility", 0)

    created_CRV = pm.curve(name=name, d=degree, p=position)

    [pm.connectAttr(pm.listRelatives(x, s=True)[0] + ".worldPosition", created_CRV + ".controlPoints[%s]" % itr) for
     itr, x in enumerate(locs)]

    if template:
        pm.setAttr(pm.listRelatives(created_CRV, s=True)[0] + ".overrideEnabled", 1)
        pm.setAttr(pm.listRelatives(created_CRV, s=True)[0] + ".overrideDisplayType", 1)

    if not keep_LOC:
        pm.delete(locs)

    return created_CRV


def sets_manager(set_name=None, objects=None, set_parent=None):

    """

    :param set_name: name of set, if it exists then it adds objects to existing
    :param objects: objects to add
    :param set_parent: parent to add set to
    :return:
    """

    pm.select(cl=True)

    new_set = pm.ls(set_name)
    if new_set:
        pm.sets(new_set[0], add=objects)
    else:
        new_set = pm.sets(name=set_name)
        if set_parent:
            pm.sets(set_parent, add=new_set)
        pm.sets(new_set, add=objects)


def create_nurbs_from_points(points, degree=3, name="yourSRF"):
    # get ribbon width
    loc1 = pm.spaceLocator()
    loc2 = pm.spaceLocator()
    [pm.pointConstraint(x, y) for x, y in zip([points[0], points[1]], [loc1, loc2])]
    pm.select([loc1, loc2])
    dist = pm.distanceDimension()

    #create surface
    SRF = pm.nurbsPlane(d=degree, u=(len(points) - 1), v=1,
                                        w=pm.getAttr("{0}.distance".format(dist)),
                                        ax=[0, 1, 0], ch=False,
                                        name="{0}_SRF".format(name))[0]
    pm.delete([loc1, loc2, pm.listRelatives(dist, p=True)[0]])

    # cluster surface
    clusters = constraintsLib.cluster_nurbs_CVs(SRF)
    [pm.delete(pm.parentConstraint(x, y)) for x, y in zip(points, clusters)]
    pm.delete(SRF, ch=True)

    return SRF


def control_shapes_from_file(mode=None, selectionMask=None, controlShapeFile=None, hideShapeChannels=True):
    """
    Description:
        Save and replace controls curve shapes with the ones contained in a file. It extracts the
        shape of each control leaving the DAG behind - and in its place in the rig - so the shape can be
        re-parented to its original DAG later.

    Args:
        mode: Either 'load' or 'save'
        selectionMask: Is the wildcard name search for the things to export. Leaving this blank will
                        use the current selection - so it can be used in-scene or in-code. Has no effect
                        in "load" mode.
        controlShapeFile: Full path to the mayaAscii file that contains the control curves
        hideShapeChannels: Set to True, will make the attributes on the shape nodes invisible and un-keyable by
                            setting the "isHistroricallyInteresting" flag to False.

    Examples:
        1. This will save out every thing with "_CTL" at the end to a file called controlShapes.ma:

                control_shapes_from_file(mode='save',
                                         selectionMask='*_CTL',
                                         controlShapeFile='/tmp/controlShapes.ma')

        2. Leaving "selectionMask" out will only export what you have selected:

                control_shapes_from_file(mode='save', controlShapeFile='/tmp/controlShapes.ma')

        3. Loads the shape file. There doesn't need to be any pre-selected stuff in the scene:

                control_shapes_from_file(mode='load', controlShapeFile='/tmp/controlShapes.ma')

    Returns:
        None

    """

    shapeGroup = 'CONTROL_SHAPE_GRP'

    if mode == 'save' and controlShapeFile:
        if not controlShapeFile.endswith('.ma'):
            controlShapeFile = '{0}.ma'.format(controlShapeFile)

        controlFolder = os.path.dirname(controlShapeFile)

        print controlFolder

        if not selectionMask:
            selected = cmds.ls(sl=True, type='transform')
        else:
            cmds.select(clear=True)

            selected = cmds.ls(selectionMask, type='transform')

        if selected:
            print selected
            # make the folder if it doesnt exists:
            if not os.path.isdir(controlFolder):
                os.makedirs(controlFolder)

            if cmds.objExists(shapeGroup):
                cmds.delete(shapeGroup)

            cmds.group(name=shapeGroup, empty=True)

            for sel in selected:
                theShapes = cmds.listRelatives(sel, shapes=True)

                if theShapes:
                    colourIndex = cmds.getAttr('{0}.overrideColor'.format(theShapes[0]))  # store control colour
                    shapeLocator = cmds.spaceLocator(name='{0}_SHAPE'.format(sel))

                    locatorShapes = cmds.listRelatives(shapeLocator, shapes=True)

                    cmds.delete(cmds.parentConstraint(sel, shapeLocator, maintainOffset=False), locatorShapes)

                    cmds.parent(shapeLocator, shapeGroup)

                    for shape in theShapes:
                        if hideShapeChannels:
                            cmds.setAttr('{0}.isHistoricallyInteresting'.format(shape), False)

                        if cmds.objectType(shape) == 'nurbsCurve':
                            cmds.parent(shape, shapeLocator, shape=True, relative=True)

                            # transfer the colour index to the shape:
                            cmds.setAttr('{0}.overrideEnabled'.format(shape), edit=True, lock=False, keyable=True)
                            cmds.setAttr('{0}.overrideColor'.format(shape), edit=True, lock=False, keyable=True)

                            cmds.setAttr('{0}.overrideEnabled'.format(shape), True)
                            cmds.setAttr('{0}.overrideColor'.format(shape), colourIndex)

            cmds.select(shapeGroup, replace=True)

            cmds.file(controlShapeFile,
                      type='mayaBinary',
                      exportSelected=True,
                      constructionHistory=False,
                      constraints=False,
                      expressions=False,
                      force=True)

            # replace:
            cmds.delete(shapeGroup)

            control_shapes_from_file(mode='load', controlShapeFile=controlShapeFile)

    if mode == 'load':
        cmds.select(clear=True)

        deleteThese = []

        if controlShapeFile and os.path.isfile(controlShapeFile):
            cmds.file(controlShapeFile, i=True)

            if cmds.objExists(shapeGroup):
                newShapeDags = cmds.listRelatives(shapeGroup, children=True, type='transform')

                for newShape in newShapeDags:
                    targetDAGString = newShape.replace('_SHAPE', '')

                    if cmds.objExists(targetDAGString):
                        theShapes = cmds.listRelatives(newShape, shapes=True)

                        if targetDAGString and cmds.objExists(targetDAGString):
                            oldShapes = cmds.listRelatives(targetDAGString, fullPath=True, shapes=True)

                            visibilityCon = []

                            if oldShapes:
                                visibilityCon = cmds.listConnections("{0}.visibility".format(oldShapes[0]), plugs=True)

                                cmds.delete(oldShapes)

                            for shape in theShapes:
                                if visibilityCon:
                                    cmds.connectAttr(str(visibilityCon[0]), "{0}.visibility".format(shape))

                                shapeParent = cmds.listRelatives(shape, parent=True)

                                deleteThese.append(shapeParent[0])

                                cmds.parent(shape, targetDAGString, shape=True, relative=True)

            cmds.delete(deleteThese, shapeGroup)

    cmds.select(clear=True)


def curve_from_surface(your_SRF, position=0.5, attach=True):

    """
    creates a curve from a surface
    :param your_SRF: surface
    :param position: 0.5=mid, 0 or 1 = either side
    :return:
    """

    curveFromSrf_CFS = pm.createNode("curveFromSurfaceIso", name=your_SRF + "_CFS")
    splineFK_CRV = pm.createNode("nurbsCurve", name=your_SRF + "_CRV")

    pm.connectAttr(your_SRF + ".worldSpace[0]", curveFromSrf_CFS + ".inputSurface")
    pm.connectAttr(curveFromSrf_CFS + ".outputCurve", splineFK_CRV + ".create")
    pm.setAttr(curveFromSrf_CFS + ".maxValue", 0)
    pm.setAttr(curveFromSrf_CFS + ".isoparmValue", position)

    if not attach:
        pm.delete(splineFK_CRV, ch=True)

    return splineFK_CRV


def decending_geo(grp=""):
    """
    gets all decending geo from a group
    :param grp: list relatives all decending from this group
    :return: shape.getParent() if shape
    """
    decending_geo = []
    meshes = [x.getShape() for x in pm.listRelatives(grp, ad=True, type="transform")]
    for mesh in meshes:
        if mesh:
            decending_geo.append(mesh.getParent())
    return decending_geo



# ============================================================ FOLICLES
def follicleRivetUI():
    if not pm.pluginInfo('matrixNodes.so', query=True, loaded=True):
        pm.loadPlugin('matrixNodes.so')

    size = [422, 125]

    frWindowHandle = 'follicleRivet'

    if pm.window(frWindowHandle, query=True, exists=True):
        pm.deleteUI(frWindowHandle)

    pm.window(frWindowHandle, title='Follicle Rivet')
    pm.frameLayout(lv=False, mw=5, mh=5)
    pm.columnLayout(adj=True)

    pm.textFieldButtonGrp('rivetMeshCtl', label='Mesh: ', bl=' < ', bc=follicleRivetUI_getMesh,
                          placeholderText='A poly mesh')

    pm.textFieldButtonGrp('rivetClosestCtl', label='Reference point: ', bl=' < ', bc=follicleRivetUI_getReferencePoint,
                          placeholderText='A node, like a locator, that is positioned close to where you want the rivet')

    pm.textFieldGrp('rivetNameCtl', label='Rivet name:', placeholderText='Name must not be empty')
    pm.checkBoxGrp('rivetDynamicCtl', label='Dynamic: ', ncb=1, enable=False)

    pm.button(label='Rivet', command=follicleRivetUI_doRivet)

    pm.window(frWindowHandle, edit=True, wh=size, sizeable=False)
    pm.showWindow(frWindowHandle)


def follicleRivetUI_getMesh(*args):
    pm.textFieldButtonGrp('rivetMeshCtl', edit=True, text='')

    selected = pm.ls(sl=True, type='transform')

    if selected:
        selType = pm.listRelatives(selected[0], shapes=True)

        if selType and pm.objectType(selType[0]) == 'mesh':
            pm.textFieldButtonGrp('rivetMeshCtl', edit=True, text=selected[0])


def follicleRivetUI_getReferencePoint(*args):
    pm.textFieldButtonGrp('rivetClosestCtl', edit=True, text='')

    selected = pm.ls(sl=True, type='transform')

    if selected:
        pm.textFieldButtonGrp('rivetClosestCtl', edit=True, text=selected[0])


def follicleRivetUI_doRivet(*args):
    mesh = pm.textFieldButtonGrp('rivetMeshCtl', query=True, text=True)
    referenceObject = pm.textFieldButtonGrp('rivetClosestCtl', query=True, text=True)
    name = pm.textFieldGrp('rivetNameCtl', query=True, text=True)
    dynamic = pm.checkBoxGrp('rivetDynamicCtl', query=True, value1=True)

    if mesh and referenceObject and name:
        follicleRivet(mesh=mesh, referenceObject=referenceObject, name=name, dynamic=dynamic)

        if pm.objExists('tmpCompRivLoc'):
            pm.delete('tmpCompRivLoc')


def follicleRivet(mesh=None, referenceObject=None, name=None, dynamic=0):
    if mesh and referenceObject and name:
        existing = pm.ls('{0}_RIV'.format(name), type='transform')

        if existing:
            nameIndex = len(existing) + 1
        else:
            nameIndex = 1

        objShape = pm.listRelatives(mesh, shapes=True)

        if objShape:
            aType = pm.objectType(objShape[0])

        if referenceObject and mesh:
            meshNode = pm.PyNode(mesh)

            # check for uv:
            pm.polyUVSet(meshNode, currentUVSet=True, uvSet='map1')

            uv = pm.ls('{0}.map[:]'.format(meshNode))[0]

            if uv and len(uv) <= 1:
                faceCount = pm.polyEvaluate(meshNode, f=True)

                pm.polyAutoProjection('{0}.f[0:{1}]'.format(mesh, faceCount-1),
                                      lm=0, pb=0, ibd=1, cm=0,
                                      l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

            tmpLoc = pm.spaceLocator(name="tmpCompRivLoc")

            pm.delete(pm.parentConstraint(referenceObject, tmpLoc, maintainOffset=False))

            if "mesh" in aType:
                tmpClo = pm.createNode("closestPointOnMesh", ss=True)

                pm.connectAttr(meshNode.outMesh, tmpClo.inMesh)
                pm.connectAttr(meshNode.worldMatrix, tmpClo.inputMatrix)
            else:
                tmpClo = pm.createNode("closestPointOnSurface", ss=True)

                pm.connectAttr(meshNode.worldSpace, tmpClo.inputSurface)

            pm.connectAttr(tmpLoc.getShape().worldPosition, tmpClo.inPosition)

            uv = [pm.getAttr(tmpClo.parameterU), pm.getAttr(tmpClo.parameterV)]

            if not dynamic:
                pm.delete(tmpLoc, tmpClo)
            else:
                pm.delete(tmpLoc)
        else:
            uv = [0.5, 0.5]

        rivShape = pm.createNode('follicle', name='{0}_{1:0>3}_RIVShape'.format(name, nameIndex), skipSelect=True)
        riv = pm.listRelatives(rivShape, parent=True)[0]

        pm.rename(riv, '{0}_{1:0>3}_RIV'.format(name, nameIndex))

        if "mesh" in aType:
            pm.connectAttr(meshNode.outMesh, rivShape.inputMesh)
            pm.connectAttr(meshNode.worldMatrix[0], rivShape.inputWorldMatrix)
        else:
            pm.connectAttr(meshNode.local, rivShape.inputSurface)
            pm.connectAttr(meshNode.worldMatrix, rivShape.inputWorldMatrix)

        pm.connectAttr(rivShape.outTranslate, riv.translate)
        pm.connectAttr(rivShape.outRotate, riv.rotate)

        if not dynamic:
            pm.setAttr(rivShape.parameterU, uv[0])
            pm.setAttr(rivShape.parameterV, uv[1])
        else:
            dcm = pm.createNode("decomposeMatrix", ss=True)

            pm.connectAttr(referenceObject.worldMatrix, dcm.inputMatrix)
            pm.connectAttr(dcm.outputTranslate, tmpClo.inPosition, f=1)

            pm.connectAttr(tmpClo.parameterU, rivShape.parameterU)
            pm.connectAttr(tmpClo.parameterV, rivShape.parameterV)

        return riv


#RIVIT WITH AIM CONSTRAINT
def rivit(refPoint, mesh, orient=True, name = "myRvt"):

    if refPoint and mesh:
        loc = pm.spaceLocator()
        pm.delete(pm.parentConstraint(refPoint, loc))

        CPOM = pm.createNode("closestPointOnMesh", name="delete_CPM")
        pm.connectAttr(mesh + ".outMesh", CPOM.inMesh)
        pm.connectAttr(loc.getShape() + ".parentInverseMatrix[0]", CPOM.inputMatrix)

        faceNumber = pm.getAttr(CPOM + ".closestFaceIndex")

        pm.select(mesh+".f[%s]" % faceNumber)

        mel.eval("ConvertSelectionToEdges;selectType -ocm -alc false;selectType -ocm -polymeshEdge true;")


        edges = pm.ls(selection=True)
        print edges
        if len(edges) == 1:
            e1 = int((edges[0].split("[")[1]).split(":")[0])
            e2 = int(((edges[0].split("[")[1]).split(":")[1])[:-1])

        elif len(edges) > 1:
            temp_edge = []
            for edge in edges:
                if ":" in str(edge):
                    temp_edge.append(int(((edge.split("[")[1]).split(":")[1])[:-1]))
                    print "double " + (((edge.split("[")[1]).split(":")[1])[:-1])
                else:
                    temp_edge.append(int((edge.split("[")[1])[:-1]))
                    print "double " + ((edge.split("[")[1])[:-1])

            e1 = temp_edge[0]
            e2 = temp_edge[-1]
        # elif len(edges) == 3:
        #     temp_edge = []
        #     for edge in edges:
        #         if ":" in str(edge):
        #             print "skipping " + edge
        #         else:
        #             temp_edge.append(edge)
        #     e1 = int((temp_edge[0].split("[")[1])[:-1])
        #     e2 = int((temp_edge[1].split("[")[1])[:-1])
        #
        # elif len(edges) == 4:
        #     e1 = int((edges[0].split("[")[1])[:-1])
        #     e2 = int((edges[-1].split("[")[1])[:-1])
        else:
            print "no edges"

        print e1, e2
        pm.delete(CPOM, loc)
    else:

        edges = pm.selected()
        mesh = edges[0].split(".")[0]
        e1 = int((edges[0].split("[")[1])[:-1])
        e2 = int((edges[1].split("[")[1])[:-1])


    print refPoint
    print e1
    print e2

    # nodes
    CFME1 = pm.createNode("curveFromMeshEdge", name=name + "1_CFME")
    pm.setAttr(CFME1.ihi, 1)
    pm.setAttr(CFME1.ei[0], e1)
    CFME2 = pm.createNode("curveFromMeshEdge", name=name + "2_CFME")
    pm.setAttr(CFME2.ihi, 1)
    pm.setAttr(CFME2.ei[0], e2)

    LOFT = pm.createNode("loft", name=name + "LOFT")
    pm.setAttr(LOFT.ic, s=2)
    pm.setAttr(LOFT.u, True)
    pm.setAttr(LOFT.rsn, True)

    POSI = pm.createNode("pointOnSurfaceInfo", name=name + "_POSI")
    pm.setAttr(POSI.turnOnPercentage, 1)
    pm.setAttr(POSI.parameterU, 0.5)
    pm.setAttr(POSI.parameterV, 0.5)

    pm.connectAttr(LOFT.outputSurface, POSI.inputSurface, f=True)
    pm.connectAttr(CFME1.outputCurve, LOFT.ic[0])
    pm.connectAttr(CFME2.outputCurve, LOFT.ic[1])
    pm.connectAttr(mesh + ".worldMesh", CFME1.inputMesh)
    pm.connectAttr(mesh + ".worldMesh", CFME2.inputMesh)

    # ====== rvt

    RVT = pm.createNode("transform", name=name + "_RVT")
    RVTShape = pm.createNode("locator", name=name + "_RVTShape", p=RVT)

    pm.connectAttr(POSI.position, RVT.translate)

    if orient:
        aimCon = pm.createNode("aimConstraint", p=RVT, name=name + "_ACON")
        pm.setAttr(aimCon.tg[0].tw, 1)
        pm.setAttr(aimCon.aimVector, [0, 1, 0], type="double3")
        pm.setAttr(aimCon.upVector, [0, 0, 1], type="double3")
        [pm.setAttr(aimCon + "." + attr, k=False) for attr in ["visibility", "rotate", "translate", "scale"]]

        pm.connectAttr(POSI.n, aimCon.tg[0].tt)
        pm.connectAttr(POSI.tv, aimCon.worldUpVector)


        pm.connectAttr(aimCon.constraintRotateX, RVT.rotateX)
        pm.connectAttr(aimCon.constraintRotateZ, RVT.rotateZ)

    return RVT






