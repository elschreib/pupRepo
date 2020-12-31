import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


from . import utilsLib








def shader_from_shape(shape):
    """

    :param shape: geo shape
    :return: material
    """


    shadeEng = pm.listConnections(shape, type="shadingEngine")
    material = pm.ls(pm.listConnections(shadeEng), materials=True)

    return material

def SG_to_material(material):

    """
    connecting a material to a shading group

    :param material:
    :return: new_SG
    """

    new_SG = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name="skin_SHDSG")
    pm.connectAttr(material + ".outColor", new_SG + ".surfaceShader")

    return new_SG


def export_materials(geos, path, name="shaders"):

    """
    
    :param geos: geo to export from - set([x.getParent() for x in pm.listRelatives("model_GRP", ad=True, type="mesh")])
    :param path: path to folder ending in "/"
    :param name: name of json
    :return: 
    """

    mat_dict = {}
    for geo in geos:
        mat = shader_from_shape(geo.getShape())
        if mat:
            if not str(mat[0]) == "lambert1":

                if str(mat[0]) in mat_dict:
                    mat_dict[str(mat[0])].append(str(geo))
                else:
                    mat_dict[str(mat[0])] = [str(geo)]



    utilsLib.saveJson(mat_dict, path + name)


    materials = (mat_dict.keys())
    for mat in materials:
        pm.select(mat)
        cmds.file(path + mat + ".ma", op="v=0;", typ="mayaAscii", pr=True, es=True)

    return mat_dict

def import_materials(path):
    """
    import materials from path - .json == {"head_SHD":["head_geo"], "poo_SHD":["shit_geo"]}
    :param path: path to folder with materials.ma and shaders.json for import instructions
    :return: fuck knows
    """


    file_path = utilsLib.import_latest(path, "*.json")
    material_dict = utilsLib.loadJson(file_path)

    for key in material_dict.keys():
        shader_name = key
        geos = material_dict[key]
        # load mat
        print path + shader_name + ".ma"
        cmds.file(path + shader_name + ".ma", i=True)
        # give it a shading group
        mat_SG = SG_to_material(shader_name)
        # add geo to shader
        for geo in geos:
            geo_check = cmds.ls(geo)
            if geo_check:
                pm.sets(mat_SG, forceElement=geo)
            else:
                print "no geo named "+geo




