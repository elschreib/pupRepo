import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel




def save_alembic(objects, path):

    root = ""
    for x in objects:
        root = root + "-root %s " % x

    save_name = path

    command = " -uvWrite -worldSpace -writeUvSets " + root + " -file " + save_name
    cmds.AbcExport(j=command)



def save_obj(objects, path):
    cmds.select(objects)
    cmds.file(path, pr=1, typ="OBJexport", es=1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")

