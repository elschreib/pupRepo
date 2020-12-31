import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


projectsPath = "E:/Files/3D/"


class scene_info():


    def __init__(self):
        print "SCENE INFO"

    def project_from_scene(self):
        self.asset_name = (cmds.file(loc=True, q=True).split("/")[-1]).split("_")[0]
        self.folder_project = cmds.file(loc=True, q=True).split(self.asset_name)[0]+self.asset_name+"/"
        self.get_paths(self.folder_project)

    def project_load(self, path):
        self.asset_name = (path.split("/")[-1])
        self.folder_project = path + "/" if not path.endswith("/") else path
        self.get_paths(self.folder_project)





    # add on paths for established asset name and path
    def get_paths(self, folder_project):
        self.all_projects_path = projectsPath

        self.streams_names = ["proxy","anim","render", "blendshape"]
        # ============ MODEL
        self.folder_model_scene = folder_project + "model/work/scene/"
        self.folder_model_publish = folder_project + "model/publish/"
        # publish+
        self.folder_model_anim = self.folder_model_publish + "anim/"
        self.folder_model_render = self.folder_model_publish + "render/"

        # ============ RIGGING
        self.folder_rigging_scene = folder_project + "rigging/work/scene/"
        self.folder_rigging_data = folder_project + "rigging/work/data/"
        self.folder_rigging_publish = folder_project + "rigging/publish/"
        # data+
        self.folder_rigging_skinWeights = self.folder_rigging_data + "skinweights/"
        self.folder_rigging_controlShapes = self.folder_rigging_data + "controlShapes/"
        self.folder_rigging_shaders = self.folder_rigging_data + "shaders/"
        self.folder_rigging_blendShapes = self.folder_rigging_data + "blendShapes/"
        self.folder_rigging_extraGeo = self.folder_rigging_data + "extraGeo/"

        self.folder_rigging_code = self.folder_rigging_data + "code/"

        # ============ LOOKDEV
        self.folder_lookDev_scene = folder_project + "lookDev/work/scene/"


        # ============ LIGHTING
        self.folder_lighting_scene = folder_project + "lighting/work/scene/"