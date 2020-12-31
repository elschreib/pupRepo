import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os
import json

from . import transformLib
from . import constraintsLib
from . import utilsLib
from . import geometryLib
from . import kinematicsLib
from . import attributesLib

"""

Pre made rigs through script



"""


def flexi_plane(name="my_surface"):

    base_GRP = pm.group(em=True, name=name + "_base_GRP")

    base_SRF = pm.nurbsPlane(ax=[0, 1, 0], u=5, name=name + "_base_SRF")[0]
    base_CRV = pm.curve(d=2, p=[[-.5, 0, 0], [0, 0, 0], [.5, 0, 0]], name=name + "_base_CRV")
    clusters = [pm.cluster(base_CRV + ".cv[%s]" % itr, name=name + "%s_CLU" % num)[1] for num, itr in
                enumerate(["0", "1", "2"])]

    # twist nonLinear Deformer
    pm.select(base_SRF)
    twist_NLD = pm.nonLinear(typ="twist", name=name + "_twist_NLD")
    pm.setAttr(twist_NLD[1].rotateZ, 90)

    # wire
    wire_DFM = pm.wire(base_SRF, w=base_CRV)[0]
    wire_DFM.dropoffDistance[0].set(10)

    pm.parent(clusters, base_SRF, base_CRV, twist_NLD, base_CRV + "BaseWire", base_GRP)

    # ============================ controls
    flexiPlane_GRP = pm.group(em=True, name=name+"_flexiPlane_GRP")

    control_SRF = pm.duplicate(base_SRF, name=name+"_control_SRF")[0]

    global_CTL = geometryLib.make_control_shape(shapeType="square",
                                                name=name+"_CTL",
                                                scale=.1,
                                                colour=name[0])

    start_CTL = geometryLib.make_control_shape(shapeType="square",
                                               name=name+"Start_CTL",
                                               scale=.1,
                                               offsets=2,
                                               colour=name[0])

    end_CTL = geometryLib.make_control_shape(shapeType="square",
                                             name=name+"End_CTL",
                                             scale=.1,
                                             offsets=2,
                                             colour=name[0])

    bend_CTL = geometryLib.make_control_shape(shapeType="sphere",
                                              name=name+"Bend_CTL",
                                              scale=.1,
                                              colour=name[0])

    start_CTL.getParent(2).translateX.set(.5)
    end_CTL.getParent(2).translateX.set(-.5)


    # set Parents
    control_SRF.setParent(global_CTL)
    global_CTL.getParent().setParent(flexiPlane_GRP)
    start_CTL.getParent(2).setParent(global_CTL)
    end_CTL.getParent(2).setParent(global_CTL)
    bend_CTL.getParent().setParent(global_CTL)

    # =============================================== CONNECT FLEXI CONTROL TO BASE
    for CTL, CLU in zip([end_CTL,start_CTL], [clusters[0],clusters[-1]]):
        PMA = pm.createNode("plusMinusAverage", name=CTL+"_PMA")
        pm.connectAttr(CTL.translate, PMA.input3D[0])
        pm.connectAttr(CTL.getParent().translate, PMA.input3D[1])
        pm.connectAttr(PMA.output3D, CLU.translate)
    pm.connectAttr(bend_CTL.translate, clusters[1].translate)


    BSN = pm.blendShape(base_SRF, control_SRF, name=name+"_base_to_control_BSN")[0]
    pm.setAttr(BSN+"."+base_SRF, 1)

    pm.connectAttr(start_CTL.rotateX, twist_NLD[0].startAngle)
    pm.connectAttr(end_CTL.rotateX, twist_NLD[0].endAngle)



    # JOINTS
    fol_GRP = pm.group(em=True, name=name+"_FOL_GRP", p=base_GRP)

    FOLs = kinematicsLib.follicle_from_amount(control_SRF, amount=5, to_edge=True, name=name)
    JNTs = kinematicsLib.create_chain(FOLs, name=name+"_###_JNT")

    pm.parent(JNTs, global_CTL)
    [pm.parentConstraint(y,x) for x,y in zip(JNTs, FOLs)]
    pm.parent(FOLs, fol_GRP)

    dict = {}
    
    dict["joints"] = JNTs
    dict["controls"] = [global_CTL,start_CTL,end_CTL,bend_CTL]
    dict["groups"] = [flexiPlane_GRP, base_GRP]
    dict["surfaces"] = [control_SRF, base_SRF]

    return dict



def ribbon_rig(guides, jntBetween=2, U_between=2, name="ribbon"):

    controls = len(guides)

    transform_GRP = pm.group(em=True, name=name + "_GRP")
    static_GRP = pm.group(em=True, name=name + "_static_GRP")
    controlJNT_GRP = pm.group(em=True, name=name + "_controlJNT_GRP", p=transform_GRP)
    bindJoints_GRP = pm.group(em=True, name=name + "_bindJoints_GRP", p=transform_GRP)

    base_SRF = pm.nurbsPlane(d=3, ax=[0, 1, 0], u=(len(guides) - 1) * U_between, v=1, name=name + "_base_SRF", ch=False)[0]
    base_SRF.setParent(static_GRP)

    itrAmount = 1.0 / (controls - 1)
    base_JNTs = []
    for itr, guide in enumerate(guides):
        if ":" in guide:
            guide_no_ns = guide.split(":")[1]
            guide_name = guide_no_ns.split("_")[1]
            side = guide_no_ns.split("_")[0]
        else:
            guide_name = guide.split("_")[1]
            side = guide.split("_")[0]
        # joint
        base_JNT = pm.createNode("joint", name="{0}_{1}_base_{2}_JNT".format(side, guide_name, str(int(itr) + 1)))
        pm.setAttr(base_JNT.translateX, (itrAmount * itr) - 0.5)
        transformLib.null_grps(base_JNT)
        base_JNTs.append(base_JNT)
        base_JNT.getParent().setParent(controlJNT_GRP)

    skinClu = pm.skinCluster(base_JNTs, base_SRF, mi=1, name=base_SRF + "_SKN")

    count = 0
    currentJnt = 1
    split = 1.0 / U_between
    for itr in range(pm.getAttr("{0}.spansU".format(base_SRF)) + 2):
        if itr == 0:
            pm.skinPercent(skinClu, "{0}.cv[0][0:3]".format(base_SRF), tv=[base_JNTs[0], 1.0])  # first
            pm.skinPercent(skinClu, "{0}.cv[1][0:3]".format(base_SRF),
                           tv=[(base_JNTs[0], 1 - (split / 3)), (base_JNTs[1], split / 3)])
        elif itr == (cmds.getAttr("{0}.spansU".format(base_SRF)) + 1):
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 2),
                           tv=[base_JNTs[-1], 1.0])  # last
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 1),
                           tv=[base_JNTs[-1], 1.0])  # fix second
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 1),
                           tv=[(base_JNTs[-1], 1 - (split / 3)), (base_JNTs[-2], split / 3)])
        else:
            count = count + 1
            secondJointVal = split * count

            if count == U_between:
                pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, itr + 1), tv=[base_JNTs[currentJnt], 1.0])
                currentJnt = currentJnt + 1
                count = 0
            else:
                pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, itr + 1), tv=(
                [base_JNTs[currentJnt - 1], 1 - secondJointVal], [base_JNTs[currentJnt], secondJointVal]))

    for guide, JNT in zip(guides, base_JNTs):
        transformLib.match([JNT.getParent()], guide)


    pm.delete(base_SRF, ch=True)

    skinClu = pm.skinCluster(base_JNTs, base_SRF, mi=1, name=base_SRF + "_SKN")

    count = 0
    currentJnt = 1
    split = 1.0 / U_between
    for itr in range(pm.getAttr("{0}.spansU".format(base_SRF)) + 2):
        if itr == 0:
            pm.skinPercent(skinClu, "{0}.cv[0][0:3]".format(base_SRF), tv=[base_JNTs[0], 1.0])  # first
            pm.skinPercent(skinClu, "{0}.cv[1][0:3]".format(base_SRF),
                           tv=[(base_JNTs[0], 1 - (split / 3)), (base_JNTs[1], split / 3)])
        elif itr == (cmds.getAttr("{0}.spansU".format(base_SRF)) + 1):
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 2),
                           tv=[base_JNTs[-1], 1.0])  # last
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 1),
                           tv=[base_JNTs[-1], 1.0])  # fix second
            pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, pm.getAttr("{0}.spansU".format(base_SRF)) + 1),
                           tv=[(base_JNTs[-1], 1 - (split / 3)), (base_JNTs[-2], split / 3)])
        else:
            count = count + 1
            secondJointVal = split * count

            if count == U_between:
                pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, itr + 1), tv=[base_JNTs[currentJnt], 1.0])
                currentJnt = currentJnt + 1
                count = 0
            else:
                pm.skinPercent(skinClu, "{0}.cv[{1}][0:3]".format(base_SRF, itr + 1), tv=(
                [base_JNTs[currentJnt - 1], 1 - secondJointVal], [base_JNTs[currentJnt], secondJointVal]))




    # BIND JOINTS
    fol_GRP = pm.group(em=True, name=name + "_FOL_GRP", p=static_GRP)

    FOLs = kinematicsLib.follicle_from_amount(base_SRF, amount=jntBetween * controls - 1, to_edge=True, name=name)
    JNTs = kinematicsLib.create_chain(FOLs, name=name + "_###_JNT")

    pm.parent(JNTs, bindJoints_GRP)
    [pm.parentConstraint(y, x) for x, y in zip(JNTs, FOLs)]
    pm.parent(FOLs, fol_GRP)

    return transform_GRP, static_GRP, base_JNTs, JNTs




# def directConnect_CTL(name, position, shape="circle"):
#
#     common_JNT = kinematicsLib.create_chain(node=position, name=name+"_###_JNT")
#     transformLib.null_grps(common_JNT[0], amount=2)
#
#     common_CTL = geometryLib.make_control_shape(shapeType=shape,
#                                                    name=name+"_CTL",
#                                                    position=position[0],
#                                                    rotation=True,
#                                                    scale=.7,
#                                                    colour=name[0])
#     common2_CTL = geometryLib.make_control_shape(shapeType=shape,
#                                                     name=name+"2_CTL",
#                                                     position=position[0],
#                                                     rotation=True,
#                                                     scale=.6,
#                                                     colour=name[0].lower())
#     attributesLib.link_secondary(common_CTL, common2_CTL, shape=True)
#     common2_CTL.getParent().setParent(common_CTL)
#
#     grp = pm.group(em=True, name= common_CTL+"_FOLLOW", p=common_CTL.getParent())
#     pm.parentConstraint(common2_CTL, grp)
#     pm.scaleConstraint(common2_CTL, grp)
#     [pm.connectAttr(grp + "." + trans, common_JNT[0] + "." + trans) for trans in ["translate", "rotate", "scale"]]
#
#     dict = {}
#     dict["controls"] = common_CTL,common2_CTL
#     dict["joints"] = common_JNT[0]
#
#     return dict
    
def directConnect_CTL(name, position, mirror=False, shape="circle"):



    common_JNT = kinematicsLib.create_chain(node=position, name=name+"_###_JNT")
    transformLib.null_grps(common_JNT[0], amount=1)

    common_CTL = geometryLib.make_control_shape(shapeType=shape,
                                                   name=name+"_CTL",
                                                   position=position[0],
                                                   rotation=True,
                                                   scale=.7,
                                                   colour=name[0])
    common2_CTL = geometryLib.make_control_shape(shapeType=shape,
                                                    name=name+"2_CTL",
                                                    position=position[0],
                                                    rotation=True,
                                                    scale=.6,
                                                    colour=name[0].lower())
    attributesLib.link_secondary(common_CTL, common2_CTL, shape=True)
    common2_CTL.getParent().setParent(common_CTL)

    grp = pm.group(em=True, name= common_CTL+"_FOLLOW", p=common_CTL.getParent())
    pm.parentConstraint(common2_CTL, grp)
    pm.scaleConstraint(common2_CTL, grp)
    [pm.connectAttr(grp + "." + trans, common_JNT[0] + "." + trans) for trans in ["translate", "rotate", "scale"]]

    if mirror:

        #flipped position
        flip_GRP = pm.group(em=True)
        pm.setAttr(flip_GRP+".scale"+mirror.upper(),-1)
        loc = pm.spaceLocator()
        loc.setParent(flip_GRP)
        pm.delete(pm.parentConstraint(position, loc))
        pm.setAttr(flip_GRP+".scale"+mirror.upper(),1)


        pm.delete(pm.parentConstraint(loc, common_CTL.getParent()))
        pm.delete(pm.parentConstraint(loc, common_JNT[0].getParent()))

        pm.delete(flip_GRP)


        mirror_CTL_GRP = pm.group(em=True, name=common_CTL+"_flip_GRP")
        mirror_JNT_GRP = pm.group(em=True, name=common_JNT[0] + "_flip_GRP")
        common_CTL.getParent().setParent(mirror_CTL_GRP)
        common_JNT[0].getParent().setParent(mirror_JNT_GRP)
        [pm.setAttr(grp+".scale"+mirror.upper(), -1) for grp in [mirror_CTL_GRP,mirror_JNT_GRP]]

    else:
        transformLib.null_grps(common_CTL.getParent(), amount=1)
        transformLib.null_grps(common_JNT[0].getParent(), amount=1)

    dict = {}
    dict["controls"] = common_CTL,common2_CTL
    dict["joints"] = common_JNT[0]

    return dict