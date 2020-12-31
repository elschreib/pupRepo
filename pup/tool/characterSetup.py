import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os
import sys

from ..library import utilsLib
from ..library import coreLib

from ..library import geometryLib
from ..library import attributesLib
from ..library import kinematicsLib
from ..library import shaderLib



from . import assembleSetup

from pup.shelf import dataInOut
data = dataInOut.DataInOut("")

# TODO: get scene info flowing through char - assembly

class CharacterSetup(assembleSetup.AssembleSetup):


    def __init__(self, project_path):

        self.project_path = project_path
        # SETUP FOR BUILD -- CHECKS FOR FOLDERS, IF THERE IT WILL BUILD
        data.project_load(self.project_path)

        # self.folder_scene = data.folder_project + "rigging/work/scene/"
        # self.folder_data = data.folder_project + "rigging/work/data/"
        #
        # self.folder_model = data.folder_project + "model/publish/"
        #
        # # ORDER OF BUILD
        # #model
        # self.folder_anim = self.folder_model + "anim/"
        # self.folder_render = self.folder_model + "render/"
        #
        # self.folder_skinWeights = self.folder_data + "skinweights/"
        # self.folder_controlShapes = self.folder_data + "controlShapes/"
        # self.folder_shaders = self.folder_data + "shaders/"




    def build_character(self):

        print "BUILDING CHARACTER FROM SCENE PATH"
        self.build_guides()

        # =================== MODEL
        if os.path.isdir(data.folder_model_anim):
            self.step_anim()
        if os.path.isdir(data.folder_model_render):
            if "render" in cmds.listAttr("guides_GRP"):
                if cmds.getAttr("guides_GRP.render"):
                    print "creating render"
                    self.step_render()
        if os.path.isdir(data.folder_rigging_extraGeo):
            self.step_extraGeo()
        # ================== CUSTOM CODE
        #CODE
        if os.path.isdir(data.folder_rigging_code):
            sys.path.insert(0, data.folder_rigging_code)
            import pup_postCode
            reload(pup_postCode)
            self.characterCode = pup_postCode.PostCode()
            # self.characterCode.postRig()
            self.code_postRig()

        self.clean_up()

        # ================== SKINCLUSTERS
        if os.path.isdir(data.folder_rigging_skinWeights):
            utilsLib.print_it("SKIN WEIGHTS")
            self.step_skinweights()

        #CODE
        if os.path.isdir(data.folder_rigging_code):
            self.code_postBind()

        # ================== CONTROLSHAPES
        if os.path.isdir(data.folder_rigging_controlShapes):
            self.step_controlShapes()

        # ================== SHADERS
        if os.path.isdir(data.folder_rigging_shaders):
            self.step_shaders()
        #CODE
        if os.path.isdir(data.folder_rigging_code):
            self.code_finalize()

        self.step_finalize()



    #MODEL
    def step_anim(self):
        utilsLib.print_it("Step: LOAD ANIM")
        data.import_model("anim", type="abc")

        self.anim_GRP = pm.ls("anim_GRP")

        if self.anim_GRP:
            self.anim_GRP[0].setParent(self.model_GRP)

            pm.setAttr("C_visibility_CTL.anim", cb=True)
            pm.connectAttr("C_visibility_CTL.anim", self.anim_GRP[0].visibility)

    #MODEL
    def step_render(self):
        utilsLib.print_it("Step: LOAD RENDER")

        data.import_model("render", type="abc")

        self.render_GRP = pm.ls("render_GRP")

        if self.render_GRP:
            self.render_GRP[0].setParent(self.model_GRP)
            pm.setAttr("C_visibility_CTL.render", cb=True)
            pm.connectAttr("C_visibility_CTL.render", self.render_GRP[0].visibility)

    def step_extraGeo(self):
        utilsLib.print_it("Step: LOAD extraGeo")

        varient_path = coreLib.save_to_path("extraGeo", data.folder_rigging_data)
        file_path = utilsLib.import_latest(varient_path, "*ma")

        # track incoming nodes and use to return
        nt = pm.NodeTracker()
        nt.startTrack()
        cmds.file(file_path, i=True)
        nt.endTrack()
        nodes = nt.getNodes()



    #CODE -
    def code_postRig(self):
        self.characterCode.postRig()

    #DATA
    def step_skinweights(self):
        utilsLib.print_it("Step: LOAD SKINWEIGHTS")

        for stream in data.streams_names:
            file_path = utilsLib.import_latest(data.folder_rigging_skinWeights + stream + "/", "v*")
            if file_path and cmds.ls(stream+"_GRP"):
                print file_path
                kinematicsLib.xml_weights_in(path=file_path, useSelected=False, copyToRender=False, uv=None, method='index')

    #CODE -
    def code_postBind(self):
        self.characterCode.postBind()

    #DATA
    def step_controlShapes(self):
        utilsLib.print_it("Step: LOAD CONTROLSHAPES")

        folder = utilsLib.import_latest(data.folder_rigging_controlShapes, "v*")+"/"
        print folder
        file_ma = utilsLib.import_latest(folder, "control_shapes*")

        geometryLib.control_shapes_from_file(mode="load", controlShapeFile=file_ma)

    #DATA
    def step_shaders(self):
        utilsLib.print_it("Step: LOAD SHADERS")

        path = utilsLib.import_latest(data.folder_rigging_shaders, "v*")+"/"
        shaderLib.import_materials(path)

    #CODE -
    def code_finalize(self):
        self.characterCode.finalize()


    def step_finalize(self):
        #final step of everything
        cmds.viewFit()






















