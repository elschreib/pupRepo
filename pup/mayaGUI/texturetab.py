
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import os
import maya.cmds as cmds
import re

from ..library import utilsLib
from ..library import shaderLib
from . import projectinfo

from . import generictab





class TextureWidget(generictab.GenericWidget):
    def __init__(self, parent=None, info=None):
        super(TextureWidget, self).__init__(parent)
        # set project info
        self.get_project_info(info)

        # create generic setup
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.textureFiles_cmb = QtWidgets.QComboBox()
        self.texture_files()
        self.textureFiles_cmb.setFixedWidth(200)

        self.textureFilesOpen_btn = QtWidgets.QPushButton("Open")
        self.textureFilesRefresh_btn = QtWidgets.QPushButton("refresh")

        self.textureNodes_cmb = QtWidgets.QComboBox()
        self.textureNodes_cmb.setFixedWidth(150)
        self.texture_nodes()
        self.textureNodeRefresh_btn = QtWidgets.QPushButton("Refresh")
        self.textureNodeCreate_btn = QtWidgets.QPushButton("Create")
        self.textureNodeUpdate_btn = QtWidgets.QPushButton("Update")


        self.DIFF_cmb = QtWidgets.QComboBox()
        self.SPCR_cmb = QtWidgets.QComboBox()
        self.METL_cmb = QtWidgets.QComboBox()
        self.NRML_cmb = QtWidgets.QComboBox()
        self.DISP_cmb = QtWidgets.QComboBox()
        self.BUMP_cmb = QtWidgets.QComboBox()
        self.EMIS_cmb = QtWidgets.QComboBox()

        self.texture_cmbs = [self.DIFF_cmb,self.SPCR_cmb,self.METL_cmb,self.NRML_cmb,self.DISP_cmb,self.BUMP_cmb,self.EMIS_cmb]
        self.slots = ["DIFF","SPCR","METL", "NRML","DISP","BUMP","EMIS"]
        for cmb, slot in zip(self.texture_cmbs, self.slots):
            self.texture_cmb_fill(cmb, slot)
            cmb.setFixedWidth(200)



    def create_layout(self):
        textureScene_layout = QtWidgets.QHBoxLayout()
        textureScene_layout.addWidget(self.textureFiles_cmb)
        textureScene_layout.addWidget(self.textureFilesOpen_btn)
        textureScene_layout.addWidget(self.textureFilesRefresh_btn)
        textureScene_formLayout = QtWidgets.QFormLayout()
        textureScene_formLayout.addRow("File:", textureScene_layout)

        textureNode_layout = QtWidgets.QHBoxLayout()
        textureNode_layout.addWidget(self.textureNodes_cmb)
        textureNode_layout.addWidget(self.textureNodeRefresh_btn)
        textureNode_layout.addWidget(self.textureNodeCreate_btn)
        textureNode_layout.addWidget(self.textureNodeUpdate_btn)

        layouts = []
        for cmb,slot in zip(self.texture_cmbs,self.slots):
            cmb_layout = QtWidgets.QHBoxLayout()
            cmb_layout.addWidget(cmb)
            DIFF_formLayout = QtWidgets.QFormLayout()
            DIFF_formLayout.addRow(slot+":", cmb_layout)
            layouts.append(DIFF_formLayout)
        self.main_layout.addLayout(textureScene_formLayout)
        self.main_layout.addLayout(self.add_sepNameSep("Shader"))
        self.main_layout.addLayout(textureNode_layout)

        [self.main_layout.addLayout(layout)for layout in layouts]




    def create_connections(self):
        self.textureFilesOpen_btn.clicked.connect(self.open_file)
        self.textureFilesRefresh_btn.clicked.connect(self.refresh_widgets)

        self.textureNodeCreate_btn.clicked.connect(self.create_shader)


    def refresh_widgets(self):
        self.texture_files()
        self.texture_nodes()
        self.refresh_generic()


        # refresh textures
        for cmb, slot in zip(self.texture_cmbs, self.slots):
            self.texture_cmb_fill(cmb, slot)

    def open_file(self):
        selected_file = self.textureFiles_cmb.currentText()
        path = self.project_dict["painter_scene"]+selected_file
        os.startfile(path)

    def texture_files(self):
        self.textureFiles_cmb.clear()
        utilsLib.check_create_dir(self.project_dict["painter_scene"])
        self.textureFiles_cmb.addItems(os.listdir(self.project_dict["painter_scene"]))





    # ================================================ SHADER FUNCTIONS ================================================
    def texture_nodes(self):
        self.textureNodes_cmb.clear()
        utilsLib.check_create_dir(self.project_dict["painter_export"])
        self.textureNodes_cmb.addItems(os.listdir(self.project_dict["painter_export"]))

    def create_shader(self):

        DIFF_path =  self.sort_texture_return(currentText=self.DIFF_cmb.currentText())
        METL_path =  self.sort_texture_return(currentText=self.METL_cmb.currentText())
        SPCR_path =  self.sort_texture_return(currentText=self.SPCR_cmb.currentText())
        EMIS_path =  self.sort_texture_return(currentText=self.EMIS_cmb.currentText())
        NRML_path =  self.sort_texture_return(currentText=self.NRML_cmb.currentText())
        BUMP_path =  self.sort_texture_return(currentText=self.BUMP_cmb.currentText())
        DISP_path =  self.sort_texture_return(currentText=self.DISP_cmb.currentText())

        if cmds.ls(self.textureNodes_cmb.currentText()+"_SHD"):
            utilsLib.print_error("THERES A SHADER CALLED '%s' ALREADY THERE!"%self.textureNodes_cmb.currentText())
        else:
            MAT = shaderLib.create_arnold_SHD(SHD_name=self.textureNodes_cmb.currentText()+"_SHD", DIFF=DIFF_path,
                                              METL=METL_path, SPCR=SPCR_path, EMIS=EMIS_path,
                                              NRML=NRML_path, BUMP=BUMP_path, DISP=DISP_path)
            print MAT




    def sort_texture_return(self, currentText):
        """
        return None anything if no file
        :param currentText:
        :return:
        """
        path = self.project_dict["painter_export"] + self.textureNodes_cmb.currentText() + "/"

        output = None
        if currentText:
            if ":" in currentText:
                version = currentText.split(":")[0]
                file = currentText.split(":")[-1]
                output = path + version+"/"+file
            elif currentText == "None":
                output = None
            else:
                output = path + currentText
        return output

    def texture_cmb_fill(self, cmb, slot):
        cmb.clear()
        files = self.get_texture(slot)
        cmb.addItems(files)



    def get_texture(self, slot=""):
        texture_node = self.textureNodes_cmb.currentText()
        if texture_node:
            path = self.project_dict["painter_export"] + texture_node + "/"

            files = self.get_all_versions(path, excludes=[".tx"], search_for=slot)
            if files:
                return files

        else:
            return ["None"]

    def get_all_versions(self, path, excludes=[".tx"], search_for=""):
        # get all versions using wildcard
        versions = os.listdir(path)
        files = ["None"]
        if versions:
            for version in versions:
                all_files = os.listdir(path + version)
                for all_file in all_files:
                    if search_for in all_file:
                        files.append(str(version + ":" + all_file))
                        # remove exludes
        for file_ in files:
            for exclude in excludes:
                if exclude in file_:
                    files.remove(file_)
        return files

    # ================================================ SHADER FUNCTIONS ================================================














