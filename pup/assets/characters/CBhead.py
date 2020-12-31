import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import os

from ..library import utilsLib
from ..library import coreLib

from ..library import geometryLib
from ..library import attributesLib
from ..library import kinematicsLib



from . import assembleSetup


class CBhead(assembleSetup.AssembleSetup):

    def step_prebuild(self):

        print "step_prebuild"

    def step_postRig(self):

        print "step_postRig"


    def step_postBind(self):

        print "step_postBind"











