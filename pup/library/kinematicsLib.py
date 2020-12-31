import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import math
import itertools
import os
import xml.etree.ElementTree as ET

from . import transformLib
from . import constraintsLib
from . import utilsLib

def create_chain(node=None, name="my_###_JNT"):
    """
        Description:
            create joints from the orientation of the objects given

        Flags:
            object (list): object to build from - must be in list for for loop
            name (string): assign name, ## represent padding


        Return:
             The chain as a list.

    """

    lastLink = None
    # thisLink = None
    chain = []

    for itr, obj in enumerate(node):
        pm.select(clear=True)

        if "#" in name:
            # get amount of "#" and use for padding amount then replace #'s
            count = name.count("#")
            thisLink = pm.joint(name=name.replace(str("#" * count), str(itr + 1).zfill(count)))

        else:
            thisLink = pm.joint(name=name)

        pm.select(clear=True)

        transformLib.match([thisLink], obj)
        pm.makeIdentity(thisLink, rotate=True, apply=True)

        if lastLink:
            pm.parent(thisLink, lastLink)

            lastLink = thisLink
        else:
            lastLink = thisLink

        chain.append(thisLink)

    return chain


def create_ikfk_switch(jointChain=None, ikChain=None, fkChain=None,
                       control=None,
                       attributeName='ikFk',
                       interpType=1,
                       connectScale=False,
                       defaultValue=0):
    """
        Description:
            Given three chains and a control curve, will make the connections required in order
            to blend the bind joint chain between the IK and FK chains. It does not create any additional
            controls for the chains.

        Flags:
            jointChain: The chain - usually the bind chain - that will move between the IK and FK chains.
            ikChain: THe IK chain.
            fkChain: The FK chain.
            control: The control - or node - that the attribute will appear on.
            attributeName: The name of the attribute can set here.
            interpType: As seen on the constraint node
            connectScale (bool): Connect the scale of the "jointChain" to the "ikChain" scale attribute.

        Return:
            The reverse node which handles the swap... which I've never needed afterwards.

    """

    allConstraints = []

    if jointChain and ikChain and fkChain:
        chainLengths = [len(jointChain), len(ikChain), len(fkChain)]

        chainLengths.sort()  # shortest [0] is the loop length in case you dont want the whole chain

        nameData = jointChain[0].split('_')
        reverseNodeName = '{0}_{1}IkFkBlend_REV'.format(nameData[0], nameData[1])

        # reverse node for the constraint 0/1 swap:
        reverseNode = pm.createNode('reverse', name=reverseNodeName)

        if not pm.attributeQuery(attributeName, node=control, exists=True):
            pm.addAttr(control,
                         longName=attributeName,
                         attributeType='double',
                         min=0.00,
                         max=1.00,
                         defaultValue=defaultValue,
                         keyable=True)

        pm.connectAttr('{0}.{1}'.format(control, attributeName), '{0}.inputX'.format(reverseNode), force=True)
        pm.connectAttr('{0}.{1}'.format(control, attributeName), '{0}.inputY'.format(reverseNode), force=True)

        # connect JNT chain to IK and FK chains:
        for jointIndex in range(0, chainLengths[0]):
            bindJoint = jointChain[jointIndex]
            ikJoint = ikChain[jointIndex]
            fkJoint = fkChain[jointIndex]

            # make the constraint:
            if jointIndex == 0:
                theConstraint = pm.parentConstraint(ikJoint,
                                                      fkJoint,
                                                      bindJoint,
                                                      name='{0}_PAC'.format(bindJoint),
                                                      maintainOffset=True)
            else:
                # may not need this "rotation only" constraint...
                theConstraint = pm.parentConstraint(ikJoint,
                                                      fkJoint,
                                                      bindJoint,
                                                      name='{0}_PAC'.format(bindJoint),
                                                      # skipTranslate=('x', 'y', 'z'),  # HERE, 10 arpril 2019
                                                      maintainOffset=True)

            if connectScale:
                # add option here...
                skipDict = {'x': ('y', 'z'), 'y': ('x', 'z'), 'z': ('x', 'y')}

                pm.scaleConstraint(ikJoint, bindJoint, skip=skipDict['x'], maintainOffset=True)
                pm.scaleConstraint(ikJoint, fkJoint, skip=skipDict['x'], maintainOffset=True)

            pm.setAttr('{0}.interpType'.format(theConstraint), interpType)

            allConstraints.append(theConstraint)

            # gets the name of the constraint targets:
            wals = constraintsLib.get_wals(constraint=theConstraint)

            # direct to constraint:
            pm.connectAttr('{0}.{1}'.format(control, attributeName),
                             '{0}.{1}'.format(theConstraint, wals[1]),
                             force=True)

            # via reverseNode:
            pm.connectAttr('{0}.outputX'.format(reverseNode),
                             '{0}.{1}'.format(theConstraint, wals[0]),
                             force=True)

            jointIndex += 1

        return reverseNode, allConstraints

# ========================== STRETCH FUNCTIONS
def single_chain_stretch(jnt, start, end, CTL, global_scale, axis="x"):

    """
    creates a single chain stretch
    :param jnt: joint to scale
    :param start: start distance
    :param end: end distance
    :param CTL: control to carry attribute
    :param global_scale: global scale to divide by
    :param axis: axis to stretch
    :return: start and end locators
    """

    start_LOC, end_LOC, distance = transformLib.get_distance(start, end, keepNode=True)
    [pm.setAttr(x + ".visibility", 0) for x in [start_LOC, end_LOC]]
    try:
        pm.parent(start_LOC, start)
        pm.parent(end_LOC, end)
    except:
        print "dist locators already parented"

    # setup nodes
    globalMD = pm.createNode("multiplyDivide", n=distance + "_global_MLD")
    distanceMD = pm.createNode("multiplyDivide", n=distance + "_distance_MLD")
    clamp = pm.createNode("clamp", n=distance + "_global_CLP")
    pm.setAttr(globalMD + ".input1X", pm.getAttr(distance + ".distance"))
    # global scale input else = 1
    if global_scale:
        pm.connectAttr(global_scale, globalMD + ".input2X")
    else:
        pm.setAttr(globalMD + ".input2X", 1)
    # connect nodes
    pm.connectAttr(distance + ".distance", distanceMD + ".input1X")
    pm.connectAttr(globalMD + ".outputX", distanceMD + ".input2X")
    pm.setAttr(distanceMD + ".operation", 2)
    pm.connectAttr(distanceMD + ".outputX", clamp + ".inputR")

    pm.connectAttr(clamp + ".outputR", jnt + ".scale%s" % (axis.upper()), f=True)
    # add attributes
    pm.addAttr(CTL, ln="minStretch", at="float", dv=1, min=0.001)
    pm.addAttr(CTL, ln="maxStretch", at="float", dv=1, min=0.002)
    pm.setAttr(CTL + ".minStretch", l=0, k=1)
    pm.setAttr(CTL + ".maxStretch", l=0, k=1)

    # add offset PMA
    pma = pm.createNode("plusMinusAverage", name=CTL+"_MORPH")

    pm.connectAttr(CTL + ".minStretch", pma+".input2D[0].input2Dx")
    pm.connectAttr(CTL + ".maxStretch", pma+".input2D[0].input2Dy")

    pm.connectAttr(pma + ".output2D.output2Dx", clamp + ".minR")
    pm.connectAttr(pma + ".output2D.output2Dy", clamp + ".maxR")

    return start_LOC, end_LOC

def limbStretch(chain, start, end, globalScale=None, control=None, scale_attr="X"):

    """

    :param chain: joint chain
    :param start: start object
    :param end: end object
    :param globalScale: global scale to divide value from
    :param control: control to hold settings
    :param scale_attr: scale axis
    :return:
    """

    # add value to chain start if no control given
    attrNode = control if control else chain[0]

    # setup start and end locators
    startLoc = pm.spaceLocator(n=start+"_distTrack")
    endLoc = pm.spaceLocator(n=end+"_distTrack")
    pm.parent(startLoc,start,r=1)
    pm.parent(endLoc,end,r=1)
    pm.setAttr(startLoc+".v", 0)
    pm.setAttr(endLoc+".v", 0)
    distBet = pm.createNode("distanceDimShape",ss=True)
    distBetTransNode = pm.listRelatives(distBet, p=True)[0]
    pm.parent(distBetTransNode, startLoc)
    pm.connectAttr(startLoc+".worldPosition",distBet+".startPoint")
    pm.connectAttr(endLoc+".worldPosition",distBet+".endPoint")


    # create global scale hookup
    globalMD = pm.createNode("multiplyDivide", ss=True)
    distanceMD = pm.createNode("multiplyDivide", ss=True)
    clamp = pm.createNode("clamp", ss=True)
    if globalScale:
        pm.connectAttr(globalScale, globalMD+".input1X")
    pm.setAttr(globalMD+".input2X", pm.getAttr(distBetTransNode+".distance"))
    pm.connectAttr(distBetTransNode+".distance", distanceMD+".input1X")
    pm.connectAttr(globalMD+".outputX", distanceMD+".input2X")
    pm.setAttr(distanceMD+".operation", 2)
    pm.connectAttr(distanceMD+".outputX", clamp+".inputR")
    pm.addAttr(attrNode, ln="minStretch", at="float", dv=1, k=True)
    pm.addAttr(attrNode, ln="maxStretch", at="float", dv=1, k=True)
    pm.addAttr(attrNode, ln="stretchOffset", at="float", dv=1, k=True)

    # add offset PMA
    pma = pm.createNode("plusMinusAverage", name=attrNode+"_MORPH")
    pm.connectAttr(attrNode + ".minStretch", pma+".input2D[0].input2Dx")
    pm.connectAttr(attrNode + ".maxStretch", pma+".input2D[0].input2Dy")
    pm.connectAttr(pma + ".output2D.output2Dx", clamp + ".minR")
    pm.connectAttr(pma + ".output2D.output2Dy", clamp + ".maxR")
    mult = pm.createNode("multiplyDivide", ss=True)


    #reverse connect
    revNode = pm.createNode("reverse",ss=True)
    pm.connectAttr(attrNode+".stretchOffset",revNode+".inputX")
    add = pm.createNode("addDoubleLinear",ss=True)
    pm.connectAttr(revNode+".outputX",add+".input1")
    pm.setAttr(add+".input2", 1)
    pm.connectAttr(add+".output",mult+".input2X",force=True)

    pm.connectAttr(attrNode+".stretchOffset", mult+".input2Y")
    pm.connectAttr(clamp+".outputR", mult+".input1X")
    pm.connectAttr(clamp+".outputR", mult+".input1Y")
    pm.connectAttr(mult+".outputX", chain[0]+".scale"+(scale_attr.upper()))
    pm.connectAttr(mult+".outputY", chain[1]+".scale"+(scale_attr.upper()))

    return startLoc, endLoc



def spline_stretch(chain, curve, control=None, globalScale=None, axis="X", volumePreserve="YZ"):

    """
        Description:
            spline stretch.

        Flags:
            chain: chain to receive scale, usually the IKspline chain.
            curve: the curve linked to the IKspline.
            control: control to receive attrs, else uses the first joint
            globalScale: what to receive scale from. e.g - global_CTL.scaleX
            axis: scale axis.
            volumePreserve: squash and stretch. give angles to stretch along

        Return:
            None.

    """
    # if not control, then use first joint instead
    attribute_dag = control if control else chain[0]

    # curve length
    arcLength_CNF = pm.createNode("curveInfo", n=curve+"_CNF")
    pm.connectAttr(pm.listRelatives(curve, s=True)[0]+".worldSpace", arcLength_CNF+".inputCurve")
    #setup nodes
    originalLength = pm.getAttr(arcLength_CNF+".arcLength")
    globalMD = pm.createNode("multiplyDivide", n=curve+"_global_MLD")
    distanceMD = pm.createNode("multiplyDivide", n=curve+"_distance_MLD")
    clamp = pm.createNode("clamp", n=curve+"_global_CLP")
    pm.setAttr(globalMD+".input1X", originalLength)
    # global scale input else = 1
    if globalScale:
        pm.connectAttr(globalScale, globalMD+".input2X")
    else:
        pm.setAttr(globalMD+".input2X", 1)
    #connect nodes
    pm.connectAttr(arcLength_CNF+".arcLength", distanceMD+".input1X")
    pm.connectAttr(globalMD+".outputX", distanceMD+".input2X")
    pm.setAttr(distanceMD+".operation", 2)
    pm.connectAttr(distanceMD+".outputX", clamp+".inputR")
    for jnt in chain[:-1]:
        pm.connectAttr(clamp+".outputR", jnt+".scale%s"%(axis.upper()), f=True)
    #add attributes
    if pm.attributeQuery("minStretch", node=attribute_dag, exists=True) == False:
        pm.addAttr(attribute_dag, ln="minStretch", at="float", dv=1, min=0.001)
        pm.addAttr(attribute_dag, ln="maxStretch", at="float", dv=1, min=0.002)
        pm.setAttr(attribute_dag+".minStretch", l=0, k=1)
        pm.setAttr(attribute_dag+".maxStretch", l=0, k=1)
    else:
        print "adding stretch to existing attributes"

    # add offset PMA
    pma = pm.createNode("plusMinusAverage", name=attribute_dag+"_MORPH")

    pm.connectAttr(attribute_dag + ".minStretch", pma+".input2D[0].input2Dx")
    pm.connectAttr(attribute_dag + ".maxStretch", pma+".input2D[0].input2Dy")

    pm.connectAttr(pma + ".output2D.output2Dx", clamp + ".minR")
    pm.connectAttr(pma + ".output2D.output2Dy", clamp + ".maxR")

    # pm.connectAttr(attribute_dag + ".minStretch", clamp + ".minR")
    # pm.connectAttr(attribute_dag + ".maxStretch", clamp + ".maxR")

    # This creates an simple inverse stretch for the other axis,
    # using the equation `1/sqrt(axis)` as the inverse scale
    #
    # POWER = Scale**0.5
    # DIVIDE = 1/POWER
    # BLEND = output . This will decide if it stretches inversely or not,
    #                  based on the parameter `volumePreservation`
    #
    if volumePreserve:
        #volume activate float attr
        if pm.attributeQuery("volumePreservation", node=attribute_dag, exists=True) == False:
            pm.addAttr(attribute_dag, ln="volumePreservation", at="float", dv=0, min=0.0, max=1.0)
            pm.setAttr(attribute_dag+".volumePreservation", l=0, k=1)
        else:
            print "adding stretch to existing attributes"
        #create nodes
        power_MLD = pm.createNode("multiplyDivide")
        divide_MLD = pm.createNode("multiplyDivide")
        blend_BLN = pm.createNode("blendColors")
        #connect some stuff
        pm.setAttr(power_MLD+".operation", 3)
        pm.connectAttr(clamp+".outputR", power_MLD+".input1X")
        pm.setAttr(power_MLD+".input2X", 0.5)
        pm.setAttr(divide_MLD+".operation", 2)
        pm.setAttr(divide_MLD+".input1X", 1)
        pm.connectAttr(power_MLD+".outputX", divide_MLD+".input2X")

        pm.setAttr(blend_BLN+".color2R", 1)
        pm.connectAttr(divide_MLD+".outputX", blend_BLN+".color1R")

        for axisOther in volumePreserve:
            for jnt in chain[:-1]:
                pm.connectAttr(blend_BLN+".outputR", jnt+".scale%s"%(axisOther.upper()), f=True)

        pm.connectAttr(attribute_dag+".volumePreservation", blend_BLN+".blender")


# ========================== TWIST FUNCTIONS
def create_advanced_twist_locators(side=None,
                                   name=None,
                                   startJoint=None,
                                   endJoint=None,
                                   upAxis='Y',
                                   upOffset=10.00,
                                   ikHandle=None,
                                   match=False):
    """
        Description:
            Creates and connects two locators that are used in the advanced twist section of an ik solver.

        Flags:
            side: A single character representing the side, "L", "R", "C".
            name: A base string name for the locators.
            startJoint: The start joint...
            endJoint: Take a guess...
            upAxis: Like an aim constraint, the up direction can be set here.
            upOffset: A value that defines how far in the upAxis the locators are transformed.
            ikHandle: The ikhandle that you are assigning the advanced twist to.
            match: Cant remember...

        Return:
            The two locators that are created.

    """

    upAxis = upAxis.upper()

    # up locators:
    startTwistLocator = pm.spaceLocator(name='{0}_{1}_twistUpStart_LOC'.format(side, name))
    endTwistLocator = pm.spaceLocator(name='{0}_{1}_twistUpEnd_LOC'.format(side, name))

    # position:
    # pm.delete(pm.pointConstraint(theCluster, theLocator, maintainOffset=False))

    pm.delete(pm.parentConstraint(startJoint, startTwistLocator, maintainOffset=False))

    if match:
        pm.delete(pm.parentConstraint(startJoint, endTwistLocator, maintainOffset=False))
    else:
        pm.delete(pm.parentConstraint(endJoint, endTwistLocator, maintainOffset=False))

    startNull = transformLib.null_grps(node=startTwistLocator)
    endNull = transformLib.null_grps(node=endTwistLocator)

    pm.setAttr('{0}.translate{1}'.format(startTwistLocator, upAxis), upOffset)
    pm.setAttr('{0}.translate{1}'.format(endTwistLocator, upAxis), upOffset)

    # startTwistLocator.setAttr('translate%s' % upAxis, upOffset)
    # endTwistLocator.setAttr('translate%s' % upAxis, upOffset)

    pm.parent(startTwistLocator, world=True)
    pm.parent(endTwistLocator, world=True)

    pm.delete(startNull, endNull)

    pm.setAttr('{0}.dTwistControlEnable'.format(ikHandle), True)
    pm.setAttr('{0}.dWorldUpType'.format(ikHandle), 2)

    pm.connectAttr('{0}.worldMatrix[0]'.format(startTwistLocator), '{0}.dWorldUpMatrix'.format(ikHandle))
    pm.connectAttr('{0}.worldMatrix[0]'.format(endTwistLocator), '{0}.dWorldUpMatrixEnd'.format(ikHandle))

    return startTwistLocator, endTwistLocator


def create_between(start_node, end_node, type, amount, orient=True, name="between_##_CHN"):
    '''
        Description:
            creates what you specify in "type" between two object, with even amount

        Flags:
            start_node (node): start of chain location
            end_node (node): end of chain location
            type (function): what to run between start and end, eg pm.joint
            amount (int): how many objects between start-end

            name (string): assign name, ## represent padding


        Return:
             The chain as a list.

    '''
    points = (pm.xform(start_node, q=True, rp=True, ws=True), pm.xform(end_node, q=True, rp=True, ws=True))
    chains = []

    iteration = 1.0 / float(amount - 1)
    startToEndVector = [math.fabs(x - y) if x < y else 0 - math.fabs(x - y) for x, y in
                        itertools.izip(points[0], points[1])]

    for itr in range(amount):
        pm.select(clear=True)

        if "#" in name:
            # get amount of "#" and use for padding amount then replace #'s
            count = name.count("#")
            chain = type(name=name.replace(str("#" * count), str(itr + 1).zfill(count)))

        else:
            chain = type(name=name)

        scalar = (itr) * iteration
        scaledVector = [x * scalar for x in startToEndVector]
        pm.xform(chain, ws=True, t=points[0])
        pm.move(scaledVector[0], scaledVector[1], scaledVector[2], chain, r=True)

        # parent chains
        if chains:
            pm.parent(chain, chains[-1])

        chains.append(chain)
    
    if orient:
        orient_chain(chains)
    
    return chains

def orient_chain(roots=None):
    if not roots:
        roots = pm.ls(sl=True, type='transform')

    for rootJoint in roots:
        pm.joint(rootJoint, edit=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)

        theChain = pm.listRelatives(rootJoint, type='joint', ad=True)
        # end joint:
        if theChain:
            if len(theChain) == 1:
                pm.joint(theChain[-1], edit=True, orientJoint='none', children=False, zeroScaleOrient=True)


# ========================== FOLLICLE STUFF
def follicle_from_position(SRF, points, cps=False, name="plane01"):
    """
        Description:
            creates a follicle on the surface from points by using then deleting the CPS node

        Flags:
            SRF: surface to attach follicles to
            points: points at which to create follicles
            cps: return closest point on surface locators
            inbetween: add extra between. ====== DOES NOT WORK WITH CPS YET
            name: 'arm', 'leg', etc...

        Return:
             follicles

    """
    SRF = pm.listRelatives(SRF, s=True)[0]
    fols = []
    locs = []
    for itr, obj in enumerate(points):
        # create follicle on surface
        fol = pm.createNode('transform', n='{0}_{1}_FOL'.format(name, itr), ss=True)
        folShape = pm.createNode('follicle', n=fol+"Shape", p=fol, ss=True)
        pm.connectAttr(SRF + ".local", folShape + ".inputSurface")
        pm.connectAttr(SRF + ".worldMatrix[0]", folShape + ".inputWorldMatrix")
        pm.connectAttr(folShape + ".outRotate", fol + ".rotate")
        pm.connectAttr(folShape + ".outTranslate", fol + ".translate")
        pm.setAttr(fol + ".inheritsTransform", False)
        # create and connect closest point on surface
        CPS = pm.createNode("closestPointOnSurface", n='{0}_{1}_CPS'.format(name, itr))
        cps_LOC = pm.spaceLocator(n=name+"_cps_%s_LOC" % (itr))
        transformLib.match([cps_LOC], obj)
        # connections
        pm.connectAttr(cps_LOC + ".worldPosition", CPS + ".inPosition")
        pm.connectAttr(SRF + ".local", CPS + ".inputSurface")
        if cps == False:
            pm.setAttr(fol + ".parameterU", (pm.getAttr(CPS + ".result.parameterU")))
            pm.setAttr(fol + ".parameterV", (pm.getAttr(CPS + ".result.parameterV")))
            pm.delete(CPS, cps_LOC)
            # pm.parentConstraint(fol, obj, mo=True)
        else:
            pm.connectAttr(CPS + ".result.parameterU", fol + ".parameterU")
            pm.connectAttr(CPS + ".result.parameterV", fol + ".parameterV")
            locs.append(cps_LOC)

        fols.append(fol)
    if cps == False:
        return fols
    else:
        return fols, locs

def follicle_from_amount(SRF, amount=5, to_edge=True, name="plane01"):
    """
        Description:
            creates a follicle on the surface evenly from amount given

        Flags:
            SRF: surface to attach follicles to
            amount: amount
            to_edge: evenly across 0-1 or have it itr/2 from the boarders
            name: 'arm', 'leg', etc...

        Return:
             follicles

    """
    SRF = pm.listRelatives(SRF, s=True)[0]
    fols = []

    if to_edge == True:
        ratio = 1.0 / (amount - 1)

    else:
        ratio = 1.0 / amount

    for itr, obj in enumerate(range(amount)):
        # create follicle on surface
        fol = pm.createNode('transform', n='{0}_{1}_FOL'.format(name, itr), ss=True)
        folShape = pm.createNode('follicle', n=fol + "Shape", p=fol, ss=True)
        pm.connectAttr(SRF + ".local", folShape + ".inputSurface")
        pm.connectAttr(SRF + ".worldMatrix[0]", folShape + ".inputWorldMatrix")
        pm.connectAttr(folShape + ".outRotate", fol + ".rotate")
        pm.connectAttr(folShape + ".outTranslate", fol + ".translate")
        pm.setAttr(fol + ".inheritsTransform", False)

        # position
        if to_edge == True:
            value = ratio * itr
        else:
            value = (ratio * itr) + (ratio / 2)
        pm.setAttr(fol + ".parameterU", value)
        pm.setAttr(fol + ".parameterV", 0.5)

        fols.append(fol)

    return fols



# ==========================  SKIN WEIGHTS
def copy_skin_weights(source=None, destination=None, uv=None, matchInfluences=True):
    """

    Copy skin cluster information between geometrylib.

    Args:
        source: name of the source geometry
        destination: name of the destination geometry
        uv: specify a UV set to use for the transfer as a list: ['map1', 'map1] which represents the source
            and destination UV sets as the first and second index
        matchInfluences: if True, will unbind the target geometry and rebind it with the influences
                         from the source geometrylib. False, will dump the weights on to the target geometry's
                         current influences.

    Returns:
        None.

    """

    if source and destination and pm.objExists(source) and pm.objExists(destination):
        sourceSC = utilsLib.get_history(node=source, historyType='skinCluster')

        destinationSkinClusterName = destination

        if '|' in destination:
            nameBits = destination.split('|')

            destinationSkinClusterName = '{0}_001'.format(nameBits[-1])

        if sourceSC:
            destinationSC = utilsLib.get_history(node=destination, historyType='skinCluster')

            if matchInfluences and destinationSC:
                # unbind destination skin first:
                pm.skinCluster(destinationSC, edit=True, unbind=True)

                destinationSC = None

            if not destinationSC:
                sourceJoints = []

                allInfs = pm.skinCluster(sourceSC, query=True, influence=True)

                if allInfs:
                    # joint filter:
                    for inf in allInfs:
                        if pm.objectType(inf) == 'joint' and not inf.endswith('_END'):
                            sourceJoints.append(inf)

                if sourceJoints:
                    destinationSC = pm.skinCluster(sourceJoints,
                                                     destination,
                                                     name='{0}_SKN'.format(destinationSkinClusterName),
                                                     toSkeletonAndTransforms=False,
                                                     toSelectedBones=True,
                                                     removeUnusedInfluence=True,
                                                     maximumInfluences=4,
                                                     bindMethod=0,
                                                     skinMethod=0,
                                                     normalizeWeights=2,
                                                     weightDistribution=0,
                                                     dropoffRate=4.00)


            if sourceSC and destinationSC:
                pm.waitCursor(state=True)

                if not uv:
                    pm.copySkinWeights(sourceSkin=sourceSC,
                                         destinationSkin=destinationSC,
                                         noMirror=True,
                                         surfaceAssociation='closestPoint',
                                         influenceAssociation=['closestJoint', 'oneToOne', 'name'])
                else:
                    pm.copySkinWeights(sourceSkin=sourceSC,
                                         destinationSkin=destinationSC,
                                         noMirror=True,
                                         surfaceAssociation='closestPoint',
                                         uvSpace=uv,
                                         influenceAssociation=['closestJoint', 'oneToOne', 'name'])

                pm.waitCursor(state=False)


def xml_weights_in(path=None, useSelected=False, copyToRender=False, uv=None, method='index', render_suf=None, anim_suf=None):
    """

        Description:
            Uses Maya's XML system for deformer weights.

        Flags:
            path: (string) The path the the xml files.
            useSelected (bool): Use scene-selected items instead of everything in the weights folder.
            copyToRender: (True/False) To speed up the weights and bind process on the render meshes, you can choose to copy the
                        influence and weight data to the name-matched render geometrylib.
            uv: (list) If copying to render, specify the uv maps to use. Defaults to ['map1' ,'map1'] if left blank.
            method: (string) How to assign the weights from the XML. Options are:

                        "index", "nearest", "barycentric", "bilinear" and "over"

            jointsOnly (bool): Either True or False. True = restict the influence types to joints only. Set to False,
                               the influence list can contain other nodes as part of the geometry's influence list.

                               Setting to False take a lot longer to applied the xml file.

        Return:
             None.

    """
    print "IMPORTING WEIGHTS"
    #render SUF must be a list
    if not render_suf:
        render_suf = ['GES', 'GEV', 'GEP']
    if not anim_suf:
        anim_suf = 'PLY'
    sceneSelected = []

    if useSelected:
        sceneSelected = pm.ls(sl=True)

    if not uv:
        uv = ['map1', 'map1']

    if path:
        print path
        xmlFiles = os.listdir(path)

        if xmlFiles:
            pm.select(clear=True)

            if useSelected and sceneSelected:
                # replace the xmlFiles list:
                xmlFiles = []

                for sel in sceneSelected:
                    xmlFiles.append('{0}.xml'.format(sel))

            if xmlFiles:
                for xml in xmlFiles:
                    if xml.endswith("xml"):
                        influenceJoints = []
                        # theSkinCluster = None

                        # temp:
                        if '|' in xml:
                            xml = xml.split('|')[-1]

                        # parse the XML file:
                        if os.path.isfile('{0}/{1}'.format(path, xml)):
                            print path, xml
                            tree = ET.parse('{0}/{1}'.format(path, xml))
                            root = tree.getroot()

                            for infJoint in root.findall('weights'):
                                jointName = infJoint.get('source')

                                if pm.objExists(jointName):
                                    influenceJoints.append(jointName)

                            # bind:
                            meshName = xml.split('.xml')[0]

                            if pm.objExists(meshName):
                                meshShape = pm.listRelatives(meshName, shapes=True)[0]

                                skinTest = utilsLib.get_history(node=meshShape, historyType='skinCluster')

                                if skinTest:
                                    # unbind first:
                                    pm.skinCluster(skinTest, edit=True, unbind=True)

                                useTheseJoints = []

                                for inf in influenceJoints:
                                    if 'joint' in pm.objectType(inf) and '_END' not in inf:
                                        useTheseJoints.append(inf)

                                if useTheseJoints:
                                    # temp, as shouldne happen in the model:
                                    if '|' in meshName:
                                        meshName = meshName.split('|')[-1]

                                    # list should now only contain joints:
                                    pm.skinCluster(useTheseJoints,
                                                     meshName,
                                                     name='{0}_SKN'.format(meshName),
                                                     toSelectedBones=True,
                                                     removeUnusedInfluence=False,
                                                     maximumInfluences=4,
                                                     bindMethod=0,
                                                     skinMethod=0,
                                                     normalizeWeights=2,
                                                     weightDistribution=0,
                                                     dropoffRate=4.00)

                                # added from job branch...
                                if pm.objExists('{0}_SKN'.format(meshName)):
                                    if os.path.isfile('{0}/{1}.xml'.format(path,meshName)):
                                        pm.deformerWeights('{0}.xml'.format(meshName),
                                                             path=path,
                                                             method=method,
                                                             im=True,
                                                             # skip='transform',
                                                             deformer='{0}_SKN'.format(meshName))


                                if copyToRender:

                                    for resTest in render_suf:
                                        ges = meshName.replace(anim_suf, resTest)

                                        if pm.objExists(ges):
                                            copy_skin_weights(source=meshName,
                                                              destination=ges,
                                                              uv=uv,
                                                              matchInfluences=True)

                                            break
                                        else:
                                            print ' XML weights in: Skipping:', meshName, ges
                            else:
                                print '\nSkipped: {0}. Missing geometry: {1}'.format(xml, meshName)

    pm.select(clear=True)


def xml_weights_out(path, geometry=None):
    """
        Description:
            Uses Maya's XML process to export skin weight data.

        Flags:
            path (string): The path the the xml files.
            geometry (list): A list of geometry to work on. If left blank, will try to use any selected nodes.
            jointsOnly (bool): Of all the possible influences governing a surface, ignore the ones that aren't joints.
        Return:
            None.

    """

    if not geometry:
        geometry = pm.ls(sl=True, type='transform')

    if geometry and path:
        if not os.path.isdir(path):
            os.makedirs(path)

        for ply in geometry:
            if type(ply) == unicode or type(ply) == str:
                # already a string:
                plyName = ply
            else:
                plyName = ply.name()

            cls = utilsLib.get_history(node=plyName, historyType='skinCluster')

            if cls:
                pm.deformerWeights('{0}.xml'.format(plyName), path=path, ex=True, skip='transform', deformer=cls)

            else:
                print ' XML weights out: No skin cluster found on:', plyName


