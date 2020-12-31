import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from . import utilsLib







def null_grps(node=None, referenceNode=None, name=None, freeze=False, empty=False, amount=1):
    """
        Description:
            Places the object in "node" under a pivot matching group which absorbs the transform,
            setting the transform values to zero. AKA, pre-transform node, offset group etc...
            returned: PyNode in, PyNode out. String in, String out.

        Args:
            node: (string/PyNode) A single object.
            referenceNode: (string) By default, the pivot of the null group will match each node, however a different node can
                           be specified for the null group's pivot location.
            name: (string) The name for the null group. add ## for number padding - e.g my_###_GRP
                  Left as None, "_GRP" gets appended to the node name and used as the
                  new group's name.
            freeze: (boolean) Applies a freeze transform operation on the node.
            empty: (boolean) make the group node, but leave it empty... or not.
            amount: (int) amount of offset groups.
        Return:
            The new group/groups.

    """

    grps = []
    for itr in range(amount):
        # get name
        if name:
            if "#" in name:
                # get amount of "#" and use for padding amount then replace #'s
                count = name.count("#")
                nameGRP = name.replace(str("#" * count), str(itr + 1).zfill(count))
            else:
                nameGRP = name + str(itr + 1)
        elif node:
            if itr == 0 and not node.endswith("_GRP"):
                nameGRP = node + "_GRP"
            else:
                if node.endswith("_GRP"):
                    nameGRP = node[:-4] + "_offset%s_GRP" % str(itr + 1)
                else:
                    nameGRP = node + "_offset%s_GRP" % str(itr + 1)
        else:
            # if no node or name, eg. empty grp == True
            nameGRP = "null_%s_GRP" % (itr + 1)
        # create the group
        if isinstance(node, basestring):
            grp = pm.group(em=True, name=nameGRP)
        else:
            grp = pm.group(em=True, name=nameGRP)
        grps.append(grp)
        # parent the group
        if len(grps) > 1:
            pm.parent(grps[-2], grps[-1])

    if referenceNode:
        match([str(grps[-1])], str(referenceNode))
    else:
        match([str(grps[-1])], str(node))
    # if using a node and empty group, the empty group gets added to node parent
    if node:
        node_parent = pm.listRelatives(node, p=True)
        if node_parent:
            pm.parent(grps[-1], node_parent[0])
    else:
        pass
    # freeze
    if freeze:
        pm.makeIdentity(grps[-1], apply=True)
    if node and not empty:
        pm.parent(node, grps[0])
    else:
        pass
    return grps


def match(nodes_to_move=None, target_node=None, translate=True, rotate=True, scale=False, pivot=False):
    """
        Updated March 2019

        Description:
            match the transformation from nodes_to_move to node_to_match in world space.

        Args:
            nodes_to_move (list): a maya node/component, or list of nodes/components which you want to match to node_to_match
            target_node (string): a maya node/component you want nodes_to_move to be placed at.
            translate (bool): do match translates of objects
            rotate (bool): do match rotates of objects
            scale (bool): do match scales of objects
            pivot (bool): if this flag is set, it will match the object's pivot rather than it's translate

        Return:
            Returns the xforms of the match

    """

    node_translate = pm.xform(target_node, query=True, translation=True, worldSpace=True)
    node_pivot = pm.xform(target_node, query=True, rotatePivot=True, worldSpace=True)
    node_rotate = pm.xform(target_node, query=True, rotation=True, worldSpace=True)
    node_scale = pm.xform(target_node, query=True, scale=True, worldSpace=True)

    if nodes_to_move:
        for node in nodes_to_move:
            if translate and not pivot and node_translate != [0, 0, 0]:
                pm.xform(node, translation=node_pivot, worldSpace=True)

            if translate and not pivot:
                pm.xform(node, translation=node_translate, worldSpace=True)

            elif translate and pivot:
                pm.xform(node, translation=node_pivot, worldSpace=True)

            if rotate:
                pm.xform(node, rotation=node_rotate, worldSpace=True)

            if scale:
                pm.xform(node, scale=node_scale, worldSpace=True)

    return [node_pivot if pivot else node_translate, node_rotate, node_scale]


def get_distance(startPoint, endPoint, keepNode=False):
    """
        Description:
            Returns the distance between the given start and end points, with an option to keep or delete
            the distance node.

            Converts the startPoint and endPoint string nodes to PyNodes, but the returned data is regular strings.

        Args:
            startPoint: an object defining the one end of the measurement.
            endPoint: an object defining the other end of the measurement.
            keepNode: Will either delete the node after the distance has been measured, or return it.

        Return:
            The distance as a float and/or the distance node.
        keepNode Return:
            start_LOC, end_LOC, distance
    """

    if startPoint and endPoint:
        start_name = pm.ls(startPoint+"_DST_LOC")
        end_name = pm.ls(endPoint+"_DST_LOC")
        if start_name:
            startPoint_LOC = startPoint+"_DST_LOC"
        else:
            startPoint_LOC = pm.spaceLocator(name=startPoint+"_DST_LOC")
            match([startPoint_LOC], startPoint)
        if end_name:
            endPoint_LOC = endPoint+"_DST_LOC"
        else:
            endPoint_LOC = pm.spaceLocator(name=endPoint+"_DST_LOC")
            match([endPoint_LOC], endPoint)


        distanceNode = pm.createNode('distanceBetween', name=endPoint+"_DST")
        pm.connectAttr(startPoint_LOC+".worldMatrix", distanceNode+".inMatrix1")
        pm.connectAttr(endPoint_LOC+".worldMatrix", distanceNode+".inMatrix2")


        theDistance = pm.getAttr(distanceNode+".distance")

        if keepNode:
            return startPoint_LOC,endPoint_LOC,distanceNode
        else:
            pm.delete(startPoint_LOC,endPoint_LOC,distanceNode)

            return theDistance


def get_rotate_difference(start, end, axis="X", name=None):

    """
    Finds the rotation differnce between two points through Matrices and quat nodes for a single axis
    works best when nodes are of the same orientation

    :param start: start obj
    :param end: end obj
    :param axis: axis to track (normally downfaceing axis)
    :param name: name to make names unique
    :return: PMA_node.output1D
    """

    #check if correct plugins are loaded
    utilsLib.load_plugin("matrixNodes")
    utilsLib.load_plugin("quatNodes")

    name = name if name else start

    # set up foreArm
    multNode = pm.createNode('multMatrix', name=name+'_QTwist_MUM')
    dcompNode = pm.createNode('decomposeMatrix', name=name+'_QTwist_DCM')
    eulerNode = pm.createNode('quatToEuler', name=name+'_QTwist_QTE')

    pm.connectAttr('{0}.worldMatrix[0]'.format(end), '{0}.matrixIn[0]'.format(multNode))
    pm.connectAttr('{0}.worldInverseMatrix[0]'.format(start), '{0}.matrixIn[1]'.format(multNode))

    pm.connectAttr('{0}.matrixSum'.format(multNode), '{0}.inputMatrix'.format(dcompNode))

    pm.connectAttr('{0}.outputQuat{1}'.format(dcompNode, axis),
                     '{0}.inputQuat{1}'.format(eulerNode, axis))

    pm.connectAttr('{0}.outputQuatW'.format(dcompNode), '{0}.inputQuatW'.format(eulerNode))
    # edit output
    fixOutput_PMA = pm.createNode('plusMinusAverage', name=name+'_QTwist_PMA')
    pm.setAttr(fixOutput_PMA + ".operation", 2)
    pm.connectAttr(eulerNode + ".outputRotate.outputRotateX", fixOutput_PMA + ".input1D[0]")
    pm.setAttr(fixOutput_PMA + ".input1D[1]", pm.getAttr(eulerNode + ".outputRotate.outputRotateX"))
    return fixOutput_PMA + ".output1D"


def copy_attrs(from_node, to_node, t=True, r=True, s=True):

    if t:
        [pm.setAttr(to_node+".translate"+attr, pm.getAttr(from_node+".translate"+attr)) for attr in "XYZ"]

    if r:
        [pm.setAttr(to_node+".rotate"+attr, pm.getAttr(from_node+".rotate"+attr)) for attr in "XYZ"]

    if s:
        [pm.setAttr(to_node+".scale"+attr, pm.getAttr(from_node+".scale"+attr)) for attr in "XYZ"]


def limit_attr(node, attrs_list="", value_list=""):

    pm.transformLimits(node, tx = [-1, 1], etx= [1, 1])
    pm.transformLimits(node, ty = [-1, 1], ety= [1, 1])
    pm.transformLimits(node, tz = [-1, 1], etz= [1, 1])


def flip_without_orient(node):

    locator = pm.spaceLocator(name="flip_LOC")
    loc_x = pm.spaceLocator(name="loc_x")
    loc_y = pm.spaceLocator(name="loc_y")
    loc_z = pm.spaceLocator(name="loc_z")
    [pm.setAttr(loc + ".translate" + axis, 1) for loc, axis in zip([loc_x, loc_y, loc_z], "XYZ")]

    locMinus_x = pm.spaceLocator(name="locMinus_x")
    locMinus_y = pm.spaceLocator(name="locMinus_y")
    locMinus_z = pm.spaceLocator(name="locMinus_z")
    [pm.setAttr(loc + ".translate" + axis, -1) for loc, axis in zip([locMinus_x, locMinus_y, locMinus_z], "XYZ")]
    locs = [loc_x, loc_y, loc_z, locMinus_x, locMinus_y, locMinus_z]
    pm.parent(locs, locator)

    match([locator], node)
    loc_GRP = pm.group(em=True)
    locator.setParent(loc_GRP)

    # closest to z
    axisFinder_loc = pm.spaceLocator(name="axisFinder_loc")
    tmp = pm.spaceLocator(name="tmp")

    pm.delete(pm.pointConstraint(locator, tmp))
    pm.delete(pm.pointConstraint(tmp, axisFinder_loc, sk=["x"]))

    dict = {}
    for loc in locs:
        dist = get_distance(axisFinder_loc, loc)
        dict[loc] = dist

    lowest = (min(dict, key=dict.get))[-1]
    pm.delete(axisFinder_loc, tmp)

    loc_GRP.scaleX.set(-1)
    pm.setAttr(locator + ".scale" + lowest.upper(), -1)

    match([node], locator)
    pm.delete(pm.aimConstraint(loc_x, node, worldUpType="object", worldUpObject=loc_y))

    pm.delete(loc_GRP)


def top_parent(node):
    top_parent = node
    parents = node
    while parents:
        parents = pm.listRelatives(parents, p=True)
        if parents:
            top_parent = parents[0]

    return top_parent
