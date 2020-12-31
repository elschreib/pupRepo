import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os

from ..library import utilsLib
from ..library import coreLib
from ..library import geometryLib
from ..library import kinematicsLib
from ..library import transformLib

from . import pipeinfoplatform
from ..shelf import alembic
from ..shelf import funkyshelf




class PipeFunctions(pipeinfoplatform.PipeInfoPlatform):




    def open_scene(self, folder_scene, step, asset):

        self.count = 0

        latest_scene = utilsLib.version_by_integer(folder_scene, "*%s*"%step, self.count)



        if latest_scene:
            cmds.file(latest_scene, o=True, f=True)
        else:
            print "CREATING A %s SCENE" %step
            cmds.file(new=True, f=True)
            cmds.file(rename=folder_scene+asset+"_%s_v001"%step)
            cmds.file(save=True, type='mayaAscii')


    def open_folder(self, folder_scene):
        path = folder_scene
        path = os.path.realpath(path)
        os.startfile(path)






    def create_project(self, projectsFolder, project):

        # create project
        if not os.path.isdir(projectsFolder + project):
            os.makedirs(projectsFolder + project)
        else:
            utilsLib.print_error("--%s-- IS A PROJECT"%project)


    def create_asset(self, projectsFolder, project, asset):

        path_project = projectsFolder + project + "/"

        # create project
        if not os.path.isdir(path_project + asset):
            os.makedirs(path_project + asset)

            path_project_asset = path_project + asset + "/"


            # folder list
            main_folders = ["model", "_reference", "rigging", "texture", "lighting", "lookdev"]
            sub = ["work", "publish"]
            sub_work = ["scene", "data"]

            for folder in main_folders:
                # creates main folders
                os.makedirs(path_project_asset + folder)
                path = path_project_asset + folder + "/"
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








        else:
            utilsLib.print_error("--%s-- IS AN ASSET"%asset)



























