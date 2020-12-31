



import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


projectsPath = "E:/Files/3D/"


class PipeInfoPlatform():

    def __init__(self):
        print "SCENE INFO"
        self.projectsPath = projectsPath


    # def set_project(self, project_name):
    #     self.project_name = project_name
    #
    #
    # def set_asset(self, asset_name):
    #     self.asset_name = asset_name
    #     self.all_projects_path = self.projectsPath + "/" + self.project_name + "/" + self.asset_name + "/"
    #     print
    #     print self.all_projects_path
    #     self.get_paths(self.all_projects_path)

    # add on paths for established asset name and path
    def get_paths(self, all_projects_path):
        self.all_projects_path= all_projects_path

        self.streams_names = ["proxy","anim","render", "blendshape"]
        # ============ MODEL
        self.folder_model_scene = self.all_projects_path + "model/work/scene/"
        self.folder_model_publish = self.all_projects_path + "model/publish/"
        # publish+
        self.folder_model_anim = self.folder_model_publish + "anim/"
        self.folder_model_render = self.folder_model_publish + "render/"

        # ============ RIGGING
        self.folder_rigging_scene = self.all_projects_path + "rigging/work/scene/"
        self.folder_rigging_data = self.all_projects_path + "rigging/work/data/"
        self.folder_rigging_publish = self.all_projects_path + "rigging/publish/"
        # data+
        self.folder_rigging_skinWeights = self.folder_rigging_data + "skinweights/"
        self.folder_rigging_controlShapes = self.folder_rigging_data + "controlShapes/"
        self.folder_rigging_shaders = self.folder_rigging_data + "shaders/"
        self.folder_rigging_blendShapes = self.folder_rigging_data + "blendShapes/"
        self.folder_rigging_extraGeo = self.folder_rigging_data + "extraGeo/"

        self.folder_rigging_code = self.folder_rigging_data + "code/"

        # ============ LOOKDEV
        self.folder_lookDev_scene = self.all_projects_path + "lookDev/work/scene/"


        # ============ LIGHTING
        self.folder_lighting_scene = self.all_projects_path + "lighting/work/scene/"
































