
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import math
import os

from . import utilsLib
from . import attributesLib

"""

LIBRARY OF CORE FUNCTIONS NOT NEEDED IN NORMAL PART BUILD

"""

# ============================= FOLLOW GROUPS
def get_partGRP_follows(node):

    """
    get follow info, returns a dict
    :param node: single node
    :return: nested dict
    """

    attr_dict = {}
    attrs = pm.listAttr(node, cb=True)
    for itr, attr in enumerate(attrs):
        if attr.startswith("follow"):
            # attribute name e.g IK, PV
            follow_name = attr.split("_")[-1]
            # get name + connection splitting at ","
            input_list = pm.getAttr(node + "." + attr).split(",")
            # split names and constraints
            names = [x.split("=")[0] for x in input_list]
            constraints = [x.split("=")[-1] for x in input_list]

            # put them into their own dict
            attr_dict[follow_name] = {}
            count = 0
            for name, constraint in (zip(names, constraints)):
                count = count+1
                # first item is name for UI and second is constraint GRP
                attr_dict[follow_name][count] = name.replace(" ", ""), constraint
    return attr_dict


    # attr_dict = {}
    # attrs = pm.listAttr(node, cb=True)
    # for itr, attr in enumerate(attrs):
    #     if attr.startswith("follow"):
    #         # attribute name e.g IK, PV
    #         follow_name = attr.split("_")[-1]
    #         # get name + connection splitting at ","
    #         input_list = pm.getAttr(node + "." + attr).split(",")
    #         # split names and constraints
    #         names = [x.split("=")[0] for x in input_list]
    #         constraints = [x.split("=")[-1] for x in input_list]
    #
    #         # put them into their own dict
    #         attr_dict[follow_name] = {}
    #         for name, constraint in zip(names, constraints):
    #             attr_dict[follow_name][name.replace(" ", "")] = constraint


def follow_groups(prefix, dicts):
    """
    creates groups from follow dict and adds input info for where to connect
    :param prefix: part prefix
    :param dicts: dict of follow groups + constraints
    :return:
    """


    groups = []

    for key in dicts.keys():
        group_names = [x[0] for x in dicts[key].values()]
        group_constraints = [x[1] for x in dicts[key].values()]

        for group_name, group_constraint in zip(group_names, group_constraints):

            name = "{0}_{1}_in".format(prefix, group_name)

            if not cmds.ls(name):
                grp = pm.group(em=True, name=name)
                groups.append(grp)

                # add attr for constraint
                pm.addAttr(grp, ln="input_node", dt="string")
                pm.setAttr(grp.input_node, cb=True)
                pm.setAttr(grp.input_node, group_constraint)
    # for itr, dict in enumerate(dicts):
    #     # if single dict
    #     if len(dicts) == 1:
    #         combined_dict = dicts
    #     # merge dicts
    #     else:
    #         if itr == 0:
    #             combined_dict = dicts[dict].copy()
    #         else:
    #             combined_dict.update(dicts[dict])
    #
    # group_names = combined_dict.keys()
    #
    # groups = []
    # for group_name in group_names:
    #     name = "{0}_{1}_in".format(prefix, group_name)
    #
    #     if not cmds.ls(name):
    #         grp = pm.group(em=True, name=name)
    #         groups.append(grp)
    #
    #         # add attr for constraint
    #         pm.addAttr(grp, ln="input_node", dt="string")
    #         pm.setAttr(grp.input_node, cb=True)
    #         pm.setAttr(grp.input_node, combined_dict[group_name])

    return groups


def connect_follow_in(static_GRP):

    """
    connects follow groups using the attr added to group to define constrtaint
    :param static_GRP:
    :return:
    """


    children = pm.listRelatives(static_GRP, c=True, type="transform")

    for child in children:
        if "_in" in str(child):
            if "_global_in" in str(child):
                pass
            else:
                constraint = pm.getAttr(child.input_node)

                constraint_check = cmds.ls(constraint)
                if constraint_check:
                    pm.parentConstraint(constraint, child, mo=True)
                    pm.scaleConstraint(constraint, child, mo=True)
                else:
                    utilsLib.print_it("ERROR-------------NO INPUT CONSTRAINT ---- "+constraint)
                    cmds.group(em=True, name=constraint)

# ============================ CONNECT ATTRS

def get_partGRP_connects(node):

    """
    get follow info, returns a dict
    :param node: single node
    :return: nested dict
    """

    attr_dict = {}
    attrs = pm.listAttr(node, cb=True)
    for itr, attr in enumerate(attrs):
        if attr.startswith("connect"):
            # get name + connection splitting at ","
            input_list = pm.getAttr(node + "." + attr)
            # split names and constraints
            if input_list:
                attr_out = input_list.split("=")[0]
                attr_in = input_list.split("=")[-1]

                # put them into their own dict
                attr_dict[attr_out] = attr_in

    return attr_dict





def load_guide(scene_folder, asset_name):
    """

    :param scene_folder: "E:/Files/3D/test_rigging/rigging/work/scene/"
    :return:
    """
    cmds.file(new=True, f=True)
    guides = utilsLib.import_latest(scene_folder, "*guides*")
    cmds.file(guides, i=True)
    cmds.file(rename=scene_folder + asset_name+'_temp.ma')
    cmds.file(save=True, type='mayaAscii')



def save_to_path(folder, asset_folder, versionUp=False):
    """
    returns path to latest folder v00* or if one exists and versionUp=True will make and return latest+1


    :param folder: name of folder - eg. skinweights
    :param asset_folder: path to folder
    :param versionUp: true or false version up makes v001 + 1
    :return:
    """



    latest_folder = utilsLib.import_latest(asset_folder + folder+ "/", "v*")

    if latest_folder:
        version = int((latest_folder.split("/")[-1])[1:])
        num = "v" + str(version + 1).zfill(3)
        if versionUp:
            os.makedirs(asset_folder + folder + "/" + num)
            latest_folder = asset_folder + folder + "/" + num

    else:
        os.makedirs(asset_folder + folder + "/v001")
        latest_folder = utilsLib.import_latest(asset_folder + folder + "/", "v*")

    return latest_folder


def part_group(name, parent):

    part_GRP = pm.group(em=True, name=name+"_GRP", p=parent)
    part_in = pm.group(em=True, name=name+"_in_GRP", p=part_GRP)
    part_out = pm.group(em=True, name=name+"_out_GRP", p=part_GRP)

    return [part_GRP,part_in,part_out]






