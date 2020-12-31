
# ============ imports
import pymel.core as pm
import maya.cmds as cmds
import glob
import os













def reference_update():
    ref_node = cmds.referenceQuery(cmds.ls(selection=True)[0], referenceNode=True)
    ref_fullPath = cmds.referenceQuery(ref_node, f=True, wcn=True)
    ref_file = ref_fullPath.split("/")[-1]
    ref_path = ref_fullPath.replace(ref_file, "")

    # get latest file - strip numbers and replace with "*"
    latest_file = utilsLib.import_latest(ref_path, re.sub('\d', '*', ref_file))
    # file type
    file_type = ["mayaBinary" if ".mb" in latest_file else "mayaAscii"][0]

    if ref_fullPath == latest_file:
        print utilsLib.print_it("THIS IS THE LATEST FILE ---- " + latest_file)
    else:
        cmds.file(latest_file, loadReference=ref_node, type=file_type, options="v=0")
