import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from ..library import utilsLib
from ..library import coreLib

from ..library import geometryLib
from ..library import attributesLib

from pup.shelf import dataInOut
data = dataInOut.DataInOut("")





class AssembleSetup(object):

    def __init__(self):

        self.guides_path = ""


    def sceneSetup(self):
        print "core: ------------- sceneSetup"
        self.rig_GRP = pm.group(em=True, name="rig_GRP")
        self.model_GRP = pm.group(em=True, name="model_GRP", p=self.rig_GRP)
        self.rig_parts_GRP = pm.group(em=True, name="rig_parts_GRP", p=self.rig_GRP)

        self.rig_SEL = pm.sets(n="rig_SEL", em=True)
        self.bindjoints_SEL = pm.sets(n="bindjoints_SEL", em=True)
        self.control_SEL = pm.sets(n="control_SEL", em=True)
        self.cache_SEL = pm.sets(n="cache_SEL", em=True)

        pm.sets(self.rig_SEL, add=[self.bindjoints_SEL, self.control_SEL, self.cache_SEL])

        # =====================================================================================
        #                                  build global GRP
        self.global_GRP = pm.group(em=True, name="global_GRP", p=self.rig_parts_GRP)
        self.C_global_CTL = geometryLib.make_control_shape(shapeType="arrow4", scale=2, name="C_global_CTL", colour="C")
        self.C_global2_CTL = geometryLib.make_control_shape(shapeType="arrow4", scale=1, name="C_global2_CTL", colour="c")
        self.options_GRP = pm.group(em=True, name="options_GRP")
        self.C_visibility_CTL = geometryLib.make_control_shape(shapeType="connector", scale=.5, name="C_visibility_CTL", colour="C")

        # set parent
        self.C_visibility_CTL.getParent().setParent(self.options_GRP)
        self.options_GRP.setParent(self.C_global2_CTL)
        self.C_global2_CTL.getParent().setParent(self.C_global_CTL)
        self.C_global_CTL.getParent().setParent(self.global_GRP)
        # pack sets
        self.C_global_SEL = pm.sets(name="C_global_SEL", em=True)
        pm.sets(self.C_global_SEL, add=[self.C_global_CTL, self.C_global2_CTL, self.C_visibility_CTL])
        pm.sets(self.control_SEL, add=self.C_global_SEL)

        # global output
        self.reference_JNT = pm.createNode("joint", name="reference_JNT")
        self.static_GRP = pm.group(em=True, name="global_static_GRP")
        self.static_GRP.setParent(self.global_GRP)
        self.reference_JNT.setParent(self.static_GRP)
        pm.parentConstraint(self.C_global2_CTL,self.reference_JNT,mo=True)
        pm.scaleConstraint(self.C_global2_CTL,self.reference_JNT,mo=True)
        # self.reference_JNT.template.set(True)
        # self.reference_JNT.drawStyle.set(2)
        pm.sets(self.bindjoints_SEL,add=self.reference_JNT)


        # attributes
        attributesLib.add_spacer_attribute(self.C_visibility_CTL, "VISIBILITY")
        pm.addAttr(self.C_visibility_CTL,ln="primary_vis",at="long",min=0,max=1,dv=1)
        pm.addAttr(self.C_visibility_CTL,ln="global_vis",at="long",min=0,max=1,dv=1)
        pm.addAttr(self.C_visibility_CTL,ln="internal_vis",at="long",min=0,max=1,dv=0)
        pm.setAttr(self.C_visibility_CTL+".primary_vis",cb=True)
        pm.setAttr(self.C_visibility_CTL+".global_vis",cb=True)
        pm.setAttr(self.C_visibility_CTL+".internal_vis",cb=True)


        attributesLib.add_spacer_attribute(self.C_visibility_CTL, "MODEL")
        pm.addAttr(self.C_visibility_CTL,ln="anim",at="long",min=0,max=1,dv=1)
        pm.addAttr(self.C_visibility_CTL,ln="render",at="long",min=0,max=1,dv=0)

        # pm.setAttr(self.C_visibility_CTL, l=True)
        pm.connectAttr(self.C_visibility_CTL.global_vis,self.C_global_CTL.getShape().v)
        pm.connectAttr(self.C_visibility_CTL.global_vis,self.C_global2_CTL.getShape().v)

        # template model GRP
        attributesLib.drawing_override(nodes=[self.model_GRP], overrideType='reference', control=self.C_visibility_CTL)
        pm.setAttr(self.C_visibility_CTL.drawingOverride,0)

        # lock attributes
        self.C_global_CTL.v.set(l=True,k=False)
        self.C_global2_CTL.v.set(l=True,k=False)
        attributesLib.lock_and_hide([self.C_visibility_CTL], t=True, r=True, s=True)


        attributesLib.add_spacer_attribute(self.C_visibility_CTL, "JOINTS")
        pm.addAttr(self.C_visibility_CTL, longName='drawStyle', at='enum', en='bone:multiChild:none:')
        pm.setAttr(self.C_visibility_CTL.drawStyle, edit=True, keyable=False, channelBox=True)



    def import_guides(self):
        pass
        # cmds.file(new=True, f=True)
        #
        # print self.guides_path
        # cmds.file(self.guides_path, i=True)
        #
        # # get all ns and prefixs
        # self.prefixs, self.parts = utilsLib.guide_namespaces()
        #
        # return self.prefixs, self.parts


    def build_guides(self):

        self.prefixs, self.part_ns = utilsLib.guide_namespaces()

        print "BUILDING PARTS:"
        print self.prefixs, self.part_ns
        print data.asset_name

        self.sceneSetup()

        ns_list = self.part_ns
        prefixs_list = self.prefixs
        self.parts = []
        for ns, prefix in zip(ns_list, prefixs_list):
            print "PART:"
            print ns.lower()
            module_path = "pup.assets.parts.{0}.{1}".format(ns.lower(), ns)
            components = module_path.split('.')
            mod = __import__(components[0])

            pass_check = 0
            for comp in components[1:]:
                try:
                    mod = getattr(mod, comp)
                    pass_check = 1
                except:
                    pass_check = 0

            if pass_check == 1:
                guide_check = pm.ls("{0}_{1}:guide".format(prefix, ns))
                if guide_check:
                    part = mod()
                    part.build_guides(prefix)
                    self.parts.append(part)
                else:
                    utilsLib.print_it("REMOVING_____{0}_{1}_____ due to no guide".format(prefix, ns))
                    self.part_ns.remove(ns)
                    self.prefixs.remove(prefix)
            else:
                utilsLib.print_it("REMOVING_____{1}_______ due to no matching part".format(prefix, ns))
                self.part_ns.remove(ns)
                self.prefixs.remove(prefix)


        # ============================ AFTER BUILD RE-LOOP THROUGH PARTS TO CONNECT
        for ns, prefix, part in zip(self.part_ns, self.prefixs, self.parts):
            self.connect_parts(part)
            # CONNECT PART IN

            # connect part part_in to assigned input
            if pm.attributeQuery("part_input", node=prefix+"_"+ns+":"+"guide", exists=True):
                connector = pm.getAttr(prefix+"_"+ns+":"+"guide.part_input")
                constraint_check = cmds.ls(connector)
                if constraint_check:
                    pm.parentConstraint(connector, part.part_in, mo=True)
                    pm.scaleConstraint(connector, part.part_in, mo=True)

            attrs_dict = coreLib.get_partGRP_connects(prefix+"_"+ns+":"+"guide")
            print attrs_dict
            if attrs_dict:
                for key in attrs_dict.keys():
                    pm.connectAttr(key, attrs_dict[key])

            # connect follow groups
            coreLib.connect_follow_in(part.static_GRP)

        # connect joints
        bindJoints = []
        utilsLib.ad_from_SEL(my_SEL=self.bindjoints_SEL, jnts_list=bindJoints, type="joint")
        for jnt in bindJoints:
            pm.connectAttr(self.C_visibility_CTL.drawStyle, jnt.drawStyle, f=True)


        guides_GRP = pm.ls("guides_GRP")
        if guides_GRP:
            guides_GRP[0].v.set(0)

        # self.clean_up()


    def connect_parts(self, part):

        """
        CONNECTS ALL COMMON PART CONNECTIONS TO GLOBAL PART
        GLOBAL - REFERENCE_JNT > ROOTSPACE GRP
        GLOBAL - REFERENCE_JNT > GLOBAL_INPUT
        GLOBAL - C_VISIBILITY_CTL > PACK_GRP + "primary_vis", "internal_vis"
        """

        [pm.connectAttr(self.reference_JNT+"."+axis, part.rootspace_GRP+"."+axis) for axis in "translate","rotate","scale"]
        # pm.scaleConstraint(self.reference_JNT, part.rootspace_GRP)

        part.pack_GRP.setParent(self.rig_parts_GRP)
        [pm.connectAttr(self.reference_JNT+"."+axis, part.global_in+"."+axis) for axis in ["translate", "rotate", "scale"]]

        [pm.connectAttr(self.C_visibility_CTL+"."+attr, part.pack_GRPs[0]+"."+attr) for attr in ["primary_vis", "internal_vis"]]

        pm.sets(self.control_SEL, add=part.control_SEL)
        pm.sets(self.bindjoints_SEL, add=part.bindjoints_SEL)



        "part_input"


    def clean_up(self):

        # CLEAN UP STAGE

        pm.delete("guides_GRP")



