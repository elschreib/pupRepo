import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import os
import maya.cmds as cmds
import re

from ..library import utilsLib
from ..shelf import alembic

PROJECTS_FOLDER = "E:/Files/3D/"


os.getcwd()

def get_project_path():
    PROJECTS_FOLDER = "E:/Files/3D/"
    return PROJECTS_FOLDER

def project_info(project, asset, step=""):
    current_project = project
    current_asset = asset

    # write around to allow guides to work within rigging
    if step == "guides":
        step = "rigging"
        step2 = "guides"
    else:
        step = step
        step2 = step

    projects_folder = PROJECTS_FOLDER + current_project + "/" + current_asset + "/"

    project_dict = {}

    project_dict["project"] = current_project
    project_dict["asset"] = current_asset
    project_dict["step"] = step2

    project_dict["base_path"] = PROJECTS_FOLDER
    project_dict["project_path"] = PROJECTS_FOLDER + project_dict["project"] + "/"
    project_dict["asset_path"] = project_dict["project_path"] + project_dict["asset"] + "/"

    # ============ FOLDERS DICT
    project_dict["scene"] = projects_folder + step + "/work/scene/"
    project_dict["publish"] = projects_folder + step + "/publish/"
    project_dict["data"] = projects_folder + step + "/work/data/"


    # =========== RIGGING
    if step == "rigging":
        project_dict["skinWeights"] = project_dict["data"] + "skinweights/"
        project_dict["controlShapes"] = project_dict["data"] + "controlShapes/"
        project_dict["shaders"] = project_dict["data"] + "shaders/"
        project_dict["blendShapes"] = project_dict["data"] + "blendShapes/"
        project_dict["extraGeo"] = project_dict["data"] + "extraGeo/"

        project_dict["guides"] = PROJECTS_FOLDER+"_Resources/Scripts/pup/assets/guides/"


    # =========== MODEL
    if step == "model":
        project_dict["sculpt_export"] = projects_folder + step + "/work/sculpt/export/"
        project_dict["sculpt_scene"] = projects_folder + step + "/work/sculpt/scene/"

    # =========== texture
    if step == "texture":
        project_dict["painter_export"] = projects_folder + step + "/work/painter/export/"
        project_dict["painter_scene"] = projects_folder + step + "/work/painter/scene/"




    return project_dict





