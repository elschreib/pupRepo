import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os

from . import info
from . import alembic
from pup.library import utilsLib

class ShelfFunctions(info.scene_info):



    def export_anim_alembic(self, grp):

        print self.asset_name
        objects = grp+"_GRP"

        if not utilsLib.import_latest(self.folder_model_publish, grp):
            os.makedirs(self.folder_model_publish + grp)

        latest_cache = utilsLib.import_latest(self.folder_model_publish + grp + "/", "*v*")

        if not latest_cache:
            cache = self.folder_model_publish + grp + "/{0}_model_{1}_v001.abc".format(self.asset_name, grp)

        else:
            version = int(((latest_cache.split("/")[-1]).split("_")[-1])[1:])
            num = "v" + str(version + 1).zfill(3)

            cache = self.folder_model_publish + grp + "/{0}_model_{1}_{2}.abc".format(self.asset_name, grp, num)

        print cache
        alembic.save_alembic([objects], cache)









