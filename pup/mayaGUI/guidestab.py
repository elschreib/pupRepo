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
from . import projectinfo

from . import generictab


class GuidesWidget(generictab.GenericWidget):
    def __init__(self, parent=None, info=None):
        super(GuidesWidget, self).__init__(parent)
        # set project info
        self.get_project_info(info)

        # create generic setup
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.guidesLib_cmb = QtWidgets.QComboBox()
        self.guidesLib_cmb.addItems(generictab.get_files(self.project_dict["guides"], ignore_files=[".mayaSwatches", "__init__.py"]))
        self.loadGuide_btn = QtWidgets.QPushButton("load")

    def create_layout(self):
        # guides lib
        guidesLib_layout = QtWidgets.QHBoxLayout()
        guidesLib_layout.addWidget(self.guidesLib_cmb)
        guidesLib_layout.addWidget(self.loadGuide_btn)
        guidesLib_formLayout = QtWidgets.QFormLayout()
        guidesLib_formLayout.addRow("Library:", guidesLib_layout)

        todo_layout = QtWidgets.QHBoxLayout()
        todo_formLayout = QtWidgets.QFormLayout()
        todo_formLayout.addRow("TODO: add guides and attrs", todo_layout)

        self.main_layout.addLayout(guidesLib_formLayout)
        self.main_layout.addLayout(todo_formLayout)

    def create_connections(self):
        self.loadGuide_btn.clicked.connect(self.namespace_text)

    def refresh_widgets(self):
        self.refresh_generic()
        self.guidesLib_cmb.clear()
        self.guidesLib_cmb.addItems(generictab.get_files(self.project_dict["guides"], ignore_files=[".mayaSwatches", "__init__.py"]))


    def namespace_text(self):
        # result = QtWidgets.QMessageBox.detailedText("something")

        # get guide name:
        self.guide_part = self.guidesLib_cmb.currentText()

        path = self.project_dict["guides"]+self.guide_part
        if "." in self.guide_part:
            self.guide_part = self.guide_part.split(".")[0]

        text, ok = QtWidgets.QInputDialog.getText(self, 'namespace', 'Enter part name:')

        if ok:
            generictab.load_referenced(path, namespace=text+"_"+self.guide_part)
            organise_guide(namespace=text+"_"+self.guide_part)






def organise_guide(namespace=None):

    guides_GRP = cmds.ls("guides_GRP")
    if not guides_GRP:
        guides_GRP = cmds.group(em=True, n="guides_GRP")

    ns_guide_GRP = cmds.ls(namespace+":guide")
    if ns_guide_GRP:
        cmds.parent(ns_guide_GRP, guides_GRP)
    else:
        utilsLib.print_error("NO GUIDE TOP GROUP TO PARENT")





