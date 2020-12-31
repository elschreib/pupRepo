import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from ..library import attributesLib
from ..library import utilsLib
from ..library import coreLib

class PartSetup(object):

    def __init__(self):
        self.guide_ns = "testGuide"
        self.prefix = "testPrefix"
        self.guides_path = "path"

    def packSetup(self, prefix):
        if prefix and not prefix.endswith("_"):
            prefix += "_"

        self.pack_GRP = pm.group(em=1,name=prefix+"pack_GRP")
        self.pack_GRP.addAttr("primary_vis",at="long",min=0,max=1,dv=1)
        self.pack_GRP.primary_vis.set(cb=True)
        self.pack_GRP.addAttr("internal_vis",at="long",min=0,max=1,dv=0)
        self.pack_GRP.internal_vis.set(cb=True)
        self.pack_GRP.addAttr("bindJoint_vis",at="long",min=0,max=1,dv=0)
        self.pack_GRP.bindJoint_vis.set(cb=True)


        if hasattr(self,"static_GRP"):
            self.static_GRP = self.static_GRP
        else:
            self.static_GRP = pm.group(em=1,name=prefix+"static_GRP")

        self.static_GRP.inheritsTransform.set(0)
        # pm.connectAttr(self.pack_GRP.internal_vis, self.static_GRP.visibility)

        self.rootspace_GRP = pm.group(em=1,name=prefix+"rootspace_GRP")

        self.part_in = pm.group(em=1,name=prefix+"part_in", p=self.rootspace_GRP)
        self.part_out = pm.group(em=1,name=prefix+"part_out", p=self.rootspace_GRP)

        self.global_in = pm.spaceLocator(name=prefix+"global_in")
        self.global_in.v.set(False)
        self.global_in.setParent(self.static_GRP)

        # PARENT
        pm.parent(self.rootspace_GRP,self.static_GRP, self.pack_GRP)

        # ATTRIBUTES
        attributesLib.lock_and_hide([self.pack_GRP, self.static_GRP],t=True, r=True, s=True, v=False)
        self.bindjoints_SEL = pm.sets(em=1,name=prefix+"bindjoints_SEL")
        self.control_SEL = pm.sets(em=1,name=prefix+"control_SEL")

        self.pack_GRPs = [self.pack_GRP, self.rootspace_GRP, self.static_GRP]


        rig_parts_GRP = pm.ls("rig_parts_GRP")
        reference_JNT = pm.ls("reference_JNT")



    def get_part_info(self, prefix, ns):


        self.follow_dict = coreLib.get_partGRP_follows("{0}_{1}:guide".format(prefix, ns))

        if self.follow_dict:
            self.group_in = coreLib.follow_groups(prefix, self.follow_dict)

            for grp_in in self.group_in:
                # pm.scaleConstraint(self.global_in, grp_in)
                grp_in.setParent(self.pack_GRPs[-1])




    # def fetchGuide(self):
    #     cmds.file(new=True, f=True)
    #     print self.guides_path
    #     cmds.file(self.guides_path, i=True)

    def build_guides(self, prefix):

        print " "
        print " "
        print "BUILDING PART --------- {0} {1}".format(prefix, self.guide_ns)
        print " "
        print " "


        self.prefix = prefix

        self.packSetup(self.prefix)

        self.get_part_info(self.prefix, self.guide_ns)
        self.build_part(self.prefix)

        # connect joints
        bindJoints = []
        utilsLib.ad_from_SEL(my_SEL=self.bindjoints_SEL, jnts_list=bindJoints, type="joint")
        all_joints = set(pm.listRelatives(self.pack_GRP, ad=True, type="joint"))
        none_bind = set(all_joints - set(bindJoints))

        if bindJoints:
            [pm.connectAttr(self.pack_GRP.internal_vis, x + ".visibility") for x in none_bind]

        # attributesLib.drawing_override(nodes=[self.model_GRP], overrideType='reference', control=self.C_visibility_CTL)

