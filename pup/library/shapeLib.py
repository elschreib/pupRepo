import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

import json

path = __file__.split("pup")[0]+"pup/assets/shapes/shapes_dict_v001.json"



def curve_to_dict(my_curve, name=None):
    """
    curve into dict -- {[name] : [points]}

    :param name: name if name else my_curve name
    :param my_curve: pyNode of curve
    :return: curve dict
    """
    dict = {}
    name = name if name else my_curve.name()

    degree = my_curve.degree()
    per = int(my_curve.form())
    if per == 1:
        per = 0
    else:
        per = 1


    my_curve_count = int(pm.ls(my_curve.cv)[0].split(":")[1][:-1])
    points = [pm.xform(my_curve.cv[itr], ws=True, t=True, q=True) for itr in range(my_curve_count + 1)]

    dict[name] = [degree, per, points]

    return dict






# ================================== JSON FUNCTIONS

def remove_shape(shape_name):
    """
    loads json and deletes specific shape
    :param shape_name: shape name to remove
    :return: None
    """
    shapes_dict = json.load(open(path))
    del shapes_dict[shape_name]
    json.dump(shapes_dict, open(path, 'w'), sort_keys=True, indent=4)

    print "removed shape '%s' from dict"%shape_name
    print shapes_dict.keys()

def add_shape(my_curve):
    """
    add item to shape dict and export
    :param shape_dict: new shape dict to add
    :return: None
    """
    dict = curve_to_dict(my_curve, name=None)

    shapes_dict = json.load(open(path))
    shapes_dict.update(dict)
    json.dump(shapes_dict, open(path, 'w'), sort_keys=True, indent=4)

    print "add shape '%s' to dict"%dict.keys()
    print shapes_dict.keys()

def query_shape():
    shapes_dict = json.load(open(path))
    print shapes_dict.keys()