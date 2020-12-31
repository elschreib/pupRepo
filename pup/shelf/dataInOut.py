import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from ..library import utilsLib
from ..library import coreLib
from ..library import geometryLib
from ..library import kinematicsLib
from ..library import transformLib

from ..shelf import info
from . import alembic
from . import funkyshelf




class DataInOut(info.scene_info):


    def __init__(self, path):
        """
        use to manage all files - inherits from scene info to get paths
        :param path:
        """
        self.count = 0
        print self.count


        if path:
            self.project_load(path)
        else:
            self.project_from_scene()

        utilsLib.print_it("set project to: "+self.asset_name)


    def count_up(self):
        self.count = self.count+1
        print "version up is +"+str(self.count)

    def count_down(self):
        self.count = self.count-1
        print "version down is +"+str(self.count)

    def version_up(self):
        """
        versions up latest scene
        :return:
        """

        path = "/".join(cmds.file(loc=True, q=True).split("/")[:-1])
        stream = (cmds.file(loc=True, q=True).split("/")[-1]).split("_")[1]

        # for saving rigs after build
        if cmds.file(loc=True, q=True).split("/")[-1] == self.asset_name+"_temp.ma":
            stream = "rig"

        latest_scene = utilsLib.version_up_path(path, "*%s*"%stream)
        cmds.file(rename=latest_scene)
        cmds.file(save=True, type='mayaAscii')

        utilsLib.print_it("SAVED:   "+latest_scene)


    def export_model(self, varient, objects):

        object_check = pm.ls(objects)
        if not object_check:
            print "NO %s GEO"%objects
            return

        # if not model publish + varient directory
        varient_path = coreLib.save_to_path(varient, self.folder_model_publish, versionUp=True)
        file = varient_path + "/{0}_model_{1}_v001".format(self.asset_name, varient)

        # export alembic
        print file
        alembic.save_alembic([objects], file+".abc")
        alembic.save_obj([objects], file+".obj")

    def import_model(self, varient, type="abc"):
        """
        :param varient: eg. anim - render -proxy
        :param type: eg. abc - obj. only those two atm
        :return: nodes
        """


        varient_path = coreLib.save_to_path(varient, self.folder_model_publish)
        print varient_path
        file_path = utilsLib.import_latest(varient_path, "*"+type)

        # track incoming nodes and use to return
        nt = pm.NodeTracker()
        nt.startTrack()
        cmds.file(file_path, i=True)
        nt.endTrack()
        nodes = nt.getNodes()

        return nodes



    def open_model(self):
        # latest_scene = utilsLib.import_latest(self.folder_model_scene, "*model*")

        self.open_scene(self.folder_model_scene, "model")


    def open_rig(self):


        self.open_scene(self.folder_rigging_scene, "rig")

        # latest_scene = utilsLib.version_by_integer(self.folder_rigging_scene, "*rig*", self.count)
        #
        # if latest_scene:
        #     cmds.file(latest_scene, o=True, f=True)
        # else:
        #     print "NO RIG SCENE"

    def open_guides(self):

        self.open_scene(self.folder_rigging_scene, "guides")


    def open_lookDev(self):

        self.open_scene(self.folder_lookDev_scene, "lookDev")

        # latest_scene = utilsLib.import_latest(self.folder_lookDev_scene, "*lookDev*")
        # if latest_scene:
        #     cmds.file(latest_scene, o=True, f=True)
        # else:
        #     print "NO lookDev SCENE"


    def open_lighting(self):

        self.open_scene(self.folder_lighting_scene, "lighting")



    # def load_guides(self):
    #     """
    #
    #     :param scene_folder: "E:/Files/3D/test_rigging/rigging/work/scene/"
    #     :return:
    #     """
    #
    #
    #     latest_scene = utilsLib.import_latest(self.folder_rigging_scene, "*guides*")
    #     if latest_scene:
    #         cmds.file(latest_scene, o=True, f=True)
    #     else:
    #         print "NO guides SCENE"
    #
    #
    #     # cmds.file(new=True, f=True)
    #     # latest_scene = utilsLib.import_latest(self.folder_rigging_scene, "*guides*")
    #     # if latest_scene:
    #     #     cmds.file(latest_scene, i=True)
    #     #     cmds.file(rename=self.folder_rigging_scene + self.asset_name + '_temp.ma')
    #     #     cmds.file(save=True, type='mayaAscii')
    #     # else:
    #     #     print "NO MODEL SCENE"

    def load_rig(self):
        """

        :param scene_folder: "E:/Files/3D/test_rigging/rigging/work/scene/"
        :return:
        """


        latest_scene = utilsLib.import_latest(self.folder_rigging_scene, "*rig*")
        if latest_scene:
            cmds.file(latest_scene, i=True)
        else:
            print "NO rig SCENE"


        # cmds.file(new=True, f=True)
        # latest_scene = utilsLib.import_latest(self.folder_rigging_scene, "*guides*")
        # if latest_scene:
        #     cmds.file(latest_scene, i=True)
        #     cmds.file(rename=self.folder_rigging_scene + self.asset_name + '_temp.ma')
        #     cmds.file(save=True, type='mayaAscii')
        # else:
        #     print "NO MODEL SCENE"




    def import_guides(self):
        """

        :param scene_folder: "E:/Files/3D/test_rigging/rigging/work/scene/"
        :return:
        """

        cmds.file(new=True, f=True)
        latest_scene = utilsLib.import_latest(self.folder_rigging_scene, "*guides*")
        if latest_scene:
            cmds.file(latest_scene, i=True)
            cmds.file(rename=self.folder_rigging_scene + self.asset_name + '_temp.ma')
            cmds.file(save=True, type='mayaAscii')
        else:
            print "NO MODEL SCENE"



    def open_scene(self, folder_scene, stream):
        latest_scene = utilsLib.version_by_integer(folder_scene, "*%s*"%stream, self.count)

        self.count = 0

        if latest_scene:
            cmds.file(latest_scene, o=True, f=True)
        else:
            cmds.file(new=True, f=True)
            cmds.file(rename=folder_scene+self.asset_name+"_%s_v001"%stream)
            cmds.file(save=True, type='mayaAscii')


    # PUBLISH TAB

    def publish_skinWeights(self, versionUp = False):
        """
        TODO: clean up geo and group finding
        in your selections if you have a group it will publish it to the same named stream
        if shape then it finds all groups above, if anim etc.. in name then it publishes to that group

        :param versionUp:
        :return: fuck all
        """


        grp_lists = ["anim", "render", "proxy", "blendshape"]


        nodes = pm.selected()

        for node in nodes:
            nodeShape = node.getShape()

            if not nodeShape:
                print node
                geo = geometryLib.decending_geo(node)
                grp = node

                streamCheck =[]
                for x in self.streams_names:
                    if x + "_GRP" == str(grp):
                        streamCheck.append(x + "_GRP")
                if streamCheck:
                    stream = streamCheck[0].split("_")[0]
                    # publish weights
                    folder = coreLib.save_to_path(folder=stream, asset_folder=self.folder_rigging_skinWeights,
                                                  versionUp=versionUp)
                    kinematicsLib.xml_weights_out(folder, geometry=utilsLib.aslist(geo))
                else:
                    print "PLEASE SELECT TOP FLODER - eg. ANIM_GRP"

            else:
                geo = node
                parents = cmds.ls(str(geo), long=True)[0].split('|')[1:-1]
                grp = []
                for x in self.streams_names:
                    if x + "_GRP" in parents:
                        grp.append(x + "_GRP")

                stream = grp[0].split("_")[0]
                # publish weights
                folder = coreLib.save_to_path(folder=stream, asset_folder=self.folder_rigging_skinWeights,
                                              versionUp=versionUp)
                kinematicsLib.xml_weights_out(folder, geometry=utilsLib.aslist(geo))

    def load_skinWeights(self):

        grp_lists = ["anim", "render", "proxy", "blendshape"]


        nodes = pm.selected()

        for node in nodes:
            nodeShape = node.getShape()

            if not nodeShape:
                print node
                geo = geometryLib.decending_geo(node)
                grp = node

                streamCheck =[]
                for x in self.streams_names:
                    if x + "_GRP" == str(grp):
                        streamCheck.append(x + "_GRP")
                if streamCheck:
                    stream = streamCheck[0].split("_")[0]
                    # publish weights
                    folder = coreLib.save_to_path(folder=stream, asset_folder=self.folder_rigging_skinWeights,
                                                  versionUp=False)
                    pm.select(utilsLib.aslist(geo))
                    kinematicsLib.xml_weights_in(path=folder, useSelected=True)
                else:
                    print "PLEASE SELECT TOP FLODER - eg. ANIM_GRP"

            else:
                geo = node
                parents = cmds.ls(str(geo), long=True)[0].split('|')[1:-1]
                grp = []
                for x in self.streams_names:
                    if x + "_GRP" in parents:
                        grp.append(x + "_GRP")

                stream = grp[0].split("_")[0]
                # publish weights
                folder = coreLib.save_to_path(folder=stream, asset_folder=self.folder_rigging_skinWeights,
                                              versionUp=False)
                pm.select(utilsLib.aslist(geo))
                kinematicsLib.xml_weights_in(path=folder, useSelected=True)


    def mirror_guide(self):

        orig_guide = pm.selected()[0]
        ns = orig_guide.split(":")[0]
        side = ns[0]
        if side == "L":
            flipped_side = "R"
        elif side == "R":
            flipped_side = "L"
        else:
            flipped_side = "dope"
        if pm.namespace(ex=flipped_side + ns[1:]):
            flipped_ns = flipped_side + ns[1:]
        else:
            flipped_ns = pm.namespace(add=flipped_side + ns[1:])

        # groups
        flip_guide = pm.duplicate(orig_guide)[0]
        guide_nodes = pm.listRelatives(flip_guide, ad=True, type="transform")
        # add namespace
        flip_guide.rename(":{0}:{1}".format(flipped_ns, flip_guide))
        [x.rename(":{0}:{1}".format(flipped_ns, x)) for x in guide_nodes]

        # flip attributes
        attrs = pm.listAttr(flip_guide, ud=True)
        for attr in attrs:
            my_input = pm.getAttr(flip_guide + "." + attr)

            if "L_" in my_input:
                pm.setAttr(flip_guide + "." + attr, my_input.replace("L_", "R_"))
            elif "R_" in my_input:
                pm.setAttr(flip_guide + "." + attr, my_input.replace("R_", "L_"))
            else:
                pass

        # mirror
        guide_JNTs = []
        guide_other = []
        for guide in guide_nodes:
            if guide.type() == "joint":
                guide_JNTs.append(guide)
            elif guide.endswith("GUIDE"):
                guide_other.append(guide)

        # ================== JOINTS
        # parents
        parent_dict = {}
        for guide in guide_JNTs:
            parent_dict[str(guide)] = cmds.listRelatives(str(guide), p=True)[0]
        # mirror
        for guide in guide_JNTs:
            children=None
            guide.setParent(w=True)
            if pm.listRelatives(guide, c=True):
                children = pm.listRelatives(guide, c=True)
                pm.parent(children, w=True)
            new_joints = pm.mirrorJoint(guide, mirrorYZ=True, mirrorBehavior=True)
            pm.delete(guide)

            if children:
                pm.parent(children, new_joints[0])
            [pm.rename(x, ":{0}:{1}".format(flipped_ns, x)) for x in new_joints]



        for key, value in parent_dict.items():
            pm.parent(key, value)


        # ==================== OTHER
        parent_dict = {}
        for guide in guide_other:
            parent_dict[guide] = pm.listRelatives(guide, p=True)[0]

        for guide in guide_other:
            guide.setParent(w=True)

            if "mirror" in pm.listAttr(guide):
                if pm.getAttr(guide.mirror):
                    # flipped position
                    flip_GRP = pm.group(em=True, name=guide+"_flip_GRP")
                    guide.setParent(flip_GRP)
                    pm.setAttr(flip_GRP + ".scaleX", -1)


            else:
                transformLib.flip_without_orient(guide)





        for key, value in parent_dict.items():
            if "mirror" in pm.listAttr(guide):
                if pm.getAttr(guide.mirror):
                    key.getParent().setParent(value)
            else:
                key.setParent(value)





    def update_ref(self):
        funkyshelf.reference_update()




    def create_project(self):

        # path is your path to 3D folder --- project is name of new project
        path = "E:/Files/3D/"
        project = cmds.ls(selection=True)[0]

        import os
        import maya.cmds as cmds

        # create project
        os.makedirs(path + project)
        project_path = path + project + "/"

        # folder list
        main_folders = ["model", "_reference", "rigging", "texture", "lighting", "lookdev"]
        sub = ["work", "publish"]
        sub_work = ["scene", "data"]

        for folder in main_folders:
            # creates main folders
            os.makedirs(project_path + folder)
            path = project_path + folder + "/"
            # if reference make different folders
            if folder == "_reference":
                os.makedirs(path + "client_in")
                os.makedirs(path + "client_out")
                os.makedirs(path + "self")
            # make work and publish
            else:
                for i in sub:
                    os.makedirs(path + i)
                # add scene and data to work
                for i in sub_work:
                    os.makedirs(path + "work/" + i)
                # if model make sculpt folder
                if folder == "model":
                    os.makedirs(path + "work/" + "sculpt")
                    os.makedirs(path + "work/sculpt/" + "export")
                    os.makedirs(path + "work/sculpt/" + "scene")

























