import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


from . import utilsLib



arnoldSurface_dict = {}
arnoldSurface_dict["DIFF"] = "baseColor"
arnoldSurface_dict["SPCR"] = "specularRoughness"
arnoldSurface_dict["METL"] = "metalness"
arnoldSurface_dict["NRML"] = "normalCamera"
arnoldSurface_dict["DISP"] = "None"
arnoldSurface_dict["BUMP"] = "normalCamera"
arnoldSurface_dict["EMIS"] = "emission"









def create_arnold_SHD(SHD_name="", DIFF=None, METL=None, SPCR=None, EMIS=None, NRML=None, BUMP=None, DISP=None):
    """

    :param path:
    :param DIFF:
    :param METL:
    :param SPCR:
    :param EMIS:
    :param NRML:
    :param HEGT:
    :return:
    """

    MAT = cmds.createNode("aiStandardSurface", name=SHD_name)
    SG = SG_to_material(MAT)

    MAT_dict = arnoldSurface_dict

    if DIFF:
        created_FILE = file_node(SHD_name, input="DIFF", texture=DIFF)
        cmds.connectAttr('{0}.outColor'.format(created_FILE), '{0}.{1}'.format(MAT, MAT_dict["DIFF"]))
    if METL:
        created_FILE = file_node(SHD_name, input="METL", texture=METL)
        cmds.connectAttr('{0}.outColorR'.format(created_FILE), '{0}.{1}'.format(MAT, MAT_dict["METL"]))
    if EMIS:
        created_FILE = file_node(SHD_name, input="EMIS", texture=EMIS)
        cmds.connectAttr('{0}.outColorR'.format(created_FILE), '{0}.{1}'.format(MAT, MAT_dict["EMIS"]))
    if SPCR:
        created_FILE = file_node(SHD_name, input="SPCR", texture=SPCR)
        cmds.connectAttr('{0}.outColorR'.format(created_FILE), '{0}.{1}'.format(MAT, MAT_dict["SPCR"]))
    if NRML:
        if not BUMP:
            create_BMP2 = cmds.createNode("bump2d", name=SHD_name + "_NORM_BMP2")
            cmds.setAttr(create_BMP2 + ".bumpInterp", 1)
            cmds.connectAttr(create_BMP2 + ".outNormal", '{0}.{1}'.format(MAT, MAT_dict["NRML"]), f=True)
            created_FILE = file_node(SHD_name, input="NORM", texture=NRML)
            cmds.connectAttr(created_FILE + ".outAlpha", create_BMP2 + ".bumpValue")
    if BUMP:
        create_BMP2 = cmds.createNode("bump2d", name=SHD_name + "_BUMP_BMP2")
        cmds.connectAttr(create_BMP2 + ".outNormal", '{0}.{1}'.format(MAT, MAT_dict["BUMP"]), f=True)
        created_FILE = file_node(SHD_name, input="BUMP", texture=BUMP)
        cmds.connectAttr(created_FILE + ".outAlpha", create_BMP2 + ".bumpValue")
    if NRML and BUMP:
        utilsLib.print_error("BUMP AND NORMAL EXIST: ONLY ATTACHED BUMP")


    return MAT





def file_node(shading_node, input=None, texture=None):
    name = input if input else "generic"
    SHD_name = shading_node if shading_node else "user"
    textureNode = cmds.shadingNode('file', name='{0}_{1}_file'.format(shading_node, name), asTexture=True)
    utilityNode = cmds.shadingNode('place2dTexture', name='{0}_{1}_place2D'.format(shading_node, name), asUtility=True)

    attrs = ('coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU',
             'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo',
             'vertexUvThree', 'vertexCameraOne'
             )

    for attr in attrs:
        cmds.connectAttr('{0}.{1}'.format(utilityNode, attr), '{0}.{1}'.format(textureNode, attr))

    cmds.connectAttr('{0}.outUV'.format(utilityNode), '{0}.uv'.format(textureNode))
    cmds.connectAttr('{0}.outUvFilterSize'.format(utilityNode), '{0}.uvFilterSize'.format(textureNode))

    # cmds.connectAttr('{0}.outColor'.format(textureNode), '{0}.color'.format(shading_node))

    if texture:
        cmds.setAttr('{0}.fileTextureName'.format(textureNode), texture, type='string')

    return textureNode

 # # find and set UV map:
 # if uvSet:
 # for index in range(0, 4): # ['map1', 'rigBody', 'fur']
 # for geo in geometry:
 # if cmds.objExists(geo):
 # geoShape = cmds.listRelatives(geo, shapes=True)[0]
 #
 # uvName = cmds.getAttr('{0}.uvSet[{1}].uvSetName'.format(geoShape, index))
 #
 # if uvName == uvSet:
 # cmds.uvLink(uvSet='{0}.uvSet[{1}].uvSetName'.format(geoShape, index),
 # texture=textureNode)








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

    new_SG = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=material+"SG")
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
            add_geo_to_shader(mat_SG, geo)


def add_geo_to_shader(SG, geo):
    geo_check = cmds.ls(geo)
    if geo_check:
        pm.sets(SG, forceElement=geo)
    else:
        print
        "no geo named " + geo



