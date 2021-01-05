from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import os
import maya.cmds as cmds
import re

from ..library import utilsLib
from ..shelf import alembic
from . import projectinfo
from ..tool import characterSetup

from . import generictab
from . import guidestab
from . import modeltab
from . import texturetab
from . import lookdevtab
from . import lightingtab

reload(projectinfo)
reload(generictab)
reload(guidestab)
reload(modeltab)
reload(texturetab)
reload(lookdevtab)
reload(lightingtab)

PROJECTS_FOLDER = projectinfo.get_project_path()

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class PupUI(QtWidgets.QDialog):

    # @classmethod
    # def show_dialog(cls):
    #     if not cls.dlg_instance:
    #         cls.dlg_instance = PupUI()
    #
    #     if cls.dlg_instance.isHidden():
    #         cls.dlg_instance.show()
    #     else:
    #         cls.dlg_instance.raise_()
    #         cls.dlg_instance.activeWindow()

    def __init__(self, parent=maya_main_window()):
        super(PupUI, self).__init__(parent)

        self.setWindowTitle("Kanto")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(PROJECTS_FOLDER+"_Resources/pref_images/ash_32x32.png")))
        self.setMinimumSize(400, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()



    def get_files(self, path, ignore_files=""):

        projects = os.listdir(path)
        projectsClean = utilsLib.remove_items_with(projects)

        return projectsClean

    # ============================================== CREATE WIDGETS ====================================================
    def create_widgets(self):
        # PROJECT
        self.project_cmb = QtWidgets.QComboBox()
        self.project_cmb.setFixedWidth(100)
        self.project_cmb.addItems(self.get_files(PROJECTS_FOLDER))
        self.project_LE = QtWidgets.QLineEdit()
        self.project_LE.setPlaceholderText("create project...")
        # ASSET
        self.asset_cmb = QtWidgets.QComboBox()
        self.asset_cmb.setFixedWidth(150)
        self.asset_cmb.addItems(self.get_files(PROJECTS_FOLDER+str(self.project_cmb.currentText())))
        self.asset_LE = QtWidgets.QLineEdit()
        self.asset_LE.setPlaceholderText("create asset...")

        self.project = self.project_cmb.currentText()
        self.asset = self.asset_cmb.currentText()
        self.project_dict = projectinfo.project_info(self.project, self.asset, step="model")

        # TABS
        self.create_tabs()

    # ============================================== TABS
    def create_tabs(self):
        self.model_wdg = modeltab.ModelWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                   self.asset_cmb.currentText(),
                                                                   step="model"))
        self.texture_wdg = texturetab.TextureWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                   self.asset_cmb.currentText(),
                                                                   step="texture"))
        self.rigging_wdg = RiggingWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                       self.asset_cmb.currentText(),
                                                                       step="rigging"))
        self.guides_wdg = guidestab.GuidesWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                       self.asset_cmb.currentText(),
                                                                       step="guides"))
        self.lookdev_wdg = lookdevtab.LookdevWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                   self.asset_cmb.currentText(),
                                                                   step="lookdev"))
        self.lighting_wdg = lightingtab.LightingWidget(info=projectinfo.project_info(self.project_cmb.currentText(),
                                                                   self.asset_cmb.currentText(),
                                                                   step="lighting"))
        self.tab_widget = QtWidgets.QTabWidget()
        # self.tab_widget.setAutoFillBackground(True)
        #
        # palette = self.tab_widget.palette()
        # palette.setColor(self.tab_widget.backgroundRole(), QtCore.Qt.red)
        # self.tab_widget.setPalette(palette)

        self.tab_widget.addTab(self.model_wdg,"model")
        self.tab_widget.addTab(self.texture_wdg,"texture")
        self.tab_widget.addTab(self.rigging_wdg,"rigging")
        self.tab_widget.addTab(self.guides_wdg,"guides")
        self.tab_widget.addTab(self.lookdev_wdg,"lookdev")
        self.tab_widget.addTab(self.lighting_wdg,"lighting")

        self.tab_index = self.tab_widget.currentIndex()

        self.tab_names = ["model", "rigging", "guides"]

        # set project info dict for each tab
        self.project_dict_refresh()
        

    def project_dict_refresh(self):
        """
        refresh the info in tabs to match project or asset changes
        :return: your mama
        """
        # model
        self.model_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="model"))
        self.model_wdg.refresh_widgets()
        # texture
        self.texture_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="texture"))
        self.texture_wdg.refresh_widgets()
        # rigging
        self.rigging_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="rigging"))
        self.rigging_wdg.refresh_widgets()
        # guides
        self.guides_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="guides"))
        self.guides_wdg.refresh_widgets()
        # lookdev
        self.lookdev_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="lookdev"))
        self.lookdev_wdg.refresh_widgets()
        # guides
        self.lighting_wdg.get_project_info(projectinfo.project_info(self.project_cmb.currentText(),self.asset_cmb.currentText(),step="lighting"))
        self.lighting_wdg.refresh_widgets()
    def project_refresh(self):
        self.project_cmb.clear()
        self.project_cmb.addItems(self.get_files(PROJECTS_FOLDER))
        self.project_dict_refresh()

    def asset_refresh(self):
        self.asset_cmb.clear()
        self.asset_cmb.addItems(self.get_files(PROJECTS_FOLDER+str(self.project_cmb.currentText())))
        self.project_dict_refresh()

    # ============================================== CREATE LAYOUT =====================================================
    def create_layout(self):
        # top layout for PROJECT and ASSET
        project_layout = QtWidgets.QHBoxLayout()
        project_layout.addWidget(self.project_cmb)
        project_layout.addWidget(self.project_LE)

        asset_layout = QtWidgets.QHBoxLayout()
        asset_layout.addWidget(self.asset_cmb)
        asset_layout.addWidget(self.asset_LE)

        # add to form
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Project:", project_layout)
        form_layout.addRow("Asset:", asset_layout)

        formTabs_layout = QtWidgets.QFormLayout()
        formTabs_layout.addRow(self.tab_widget)

        # for tabs in self.all_tabs:
        # fianalize
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(formTabs_layout)

    # ============================================== CREATE CONNECTIONS ================================================
    def create_connections(self):
        # pass
        self.project_cmb.currentTextChanged.connect(self.asset_refresh)

        self.asset_cmb.currentTextChanged.connect(self.project_dict_refresh)

        self.project_LE.returnPressed.connect(self.project_enter_pressed)
        self.asset_LE.returnPressed.connect(self.asset_enter_pressed)


    def project_enter_pressed(self):
        # name from line edit
        self.project_LE_str = self.project_LE.text()
        # create folder with name
        create_folder(self.project_dict["base_path"], self.project_LE_str)
        # refresh projects to add new project
        self.project_refresh()
        # clear line edit
        self.project_LE.clear()

    def asset_enter_pressed(self):
        # name from line edit
        self.asset_LE_str = self.asset_LE.text()
        # create folder with name
        # TODO: update project_dict when project change cmb
        create_asset(self.project_dict["base_path"]+self.project_cmb.currentText()+"/", self.asset_LE_str)
        # refresh projects to add new asset
        self.asset_refresh()
        # clear line edit
        self.asset_LE.clear()



def create_folder(path, name):
    if os.path.isdir(path + name):
        utilsLib.print_error("---%s--- IS ALREADY THERE"%name)
    else:
        os.makedirs(path + name)
        utilsLib.print_it("---%s--- HAS BEEN CREATED"%name)

def create_asset(path, asset):
    if os.path.isdir(path + asset):
        utilsLib.print_error("---%s--- IS ALREADY AN ASSET"%asset)
    else:
        # create asset
        os.makedirs(path + asset)
        asset_path = path + asset + "/"

        # folder list
        main_folders = ["model", "_reference", "rigging", "texture", "lighting", "lookdev"]
        sub = ["work", "publish"]
        sub_work = ["scene", "data"]

        for folder in main_folders:
            # creates main folders
            os.makedirs(asset_path + folder)
            path = asset_path + folder + "/"
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
                if folder == "texture":
                    os.makedirs(path + "work/" + "painter")
                    os.makedirs(path + "work/painter/" + "export")
                    os.makedirs(path + "work/painter/" + "scene")
        utilsLib.print_it("---%s--- asset folder structure created"%asset)
# class GenericWidget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super(GenericWidget, self).__init__(parent)
#
#         self.project_dict = None
#
#         self.create_generic_widgets()
#         self.create_generic_layout()
#         self.create_generic_connections()
#
#     def create_generic_widgets(self):
#         self.open_btn = QtWidgets.QPushButton("open")
#         self.versionUp_btn = QtWidgets.QPushButton("version+")
#         self.folder_btn = QtWidgets.QPushButton("folder")
#
#         self.publish_btn = QtWidgets.QPushButton("publish")
#         self.load_btn = QtWidgets.QPushButton("load")
#         self.reference_btn = QtWidgets.QPushButton("ref")
#         self.variants_cmb = QtWidgets.QComboBox()
#         self.variants_cmb.addItems(["anim","render"])
#
#
#     def create_generic_layout(self):
#         layout1 = QtWidgets.QHBoxLayout()
#         layout1.addWidget(self.open_btn)
#         layout1.addWidget(self.versionUp_btn)
#         self.add_separator(layout1)
#         layout1.addWidget(self.folder_btn)
#
#         layout2 = QtWidgets.QHBoxLayout()
#         layout2.addWidget(self.publish_btn)
#         layout2.addWidget(self.load_btn)
#         layout2.addWidget(self.reference_btn)
#         self.add_separator(layout2)
#         layout2.addWidget(self.variants_cmb)
#
#
#
#         self.div1 = QtWidgets.QFrame()
#         self.div1.setFrameShape(QtWidgets.QFrame.HLine)
#         self.div1.setFrameShadow(QtWidgets.QFrame.Sunken)
#         layout2.addWidget(self.div1)
#
#         self.main_layout = QtWidgets.QVBoxLayout(self)
#         self.main_layout.addLayout(layout1)
#         self.main_layout.addLayout(layout2)
#         self.main_layout.addWidget(self.div1)
#
#
#
#     def create_generic_connections(self):
#         self.open_btn.clicked.connect(lambda: open_scene(self.project_dict))
#         self.versionUp_btn.clicked.connect(version_up)
#         self.folder_btn.clicked.connect(lambda: open_folder(self.project_dict))
#
#         self.publish_btn.clicked.connect(lambda: publish_from_step(self.project_dict, self.variants_cmb.currentText()))
#         self.load_btn.clicked.connect(lambda: load_publish(self.project_dict, self.variants_cmb.currentText()))
#         self.reference_btn.clicked.connect(lambda: ref_publish(self.project_dict, self.variants_cmb.currentText()))
#
#     def get_variants(self, path, ignore_files=""):
#
#         variants = os.listdir(path)
#         variantsClean = utilsLib.remove_items_with(variants)
#
#         return variantsClean
#
#     def get_project_info(self, dict):
#         self.project_dict = dict
#         # return self.project_dict
#
#     def add_separator(self, layout):
#
#         separator = QtWidgets.QFrame()
#         separator.setFrameShape(QtWidgets.QFrame.HLine)
#         separator.setFrameShadow(QtWidgets.QFrame.Sunken)
#         layout.addWidget(separator)



class RiggingWidget(generictab.GenericWidget):
    def __init__(self, parent=None, info=None):
        super(RiggingWidget, self).__init__(parent)
        # set project info
        self.get_project_info(info)

        # create tab extras
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):



        self.buildRig_btn = QtWidgets.QPushButton("buildRig")

        # create publish step

        self.saveControl_btn = QtWidgets.QPushButton("save")
        self.saveControlUp_btn = QtWidgets.QPushButton("version up")
        self.loadControl_btn = QtWidgets.QPushButton("load")

        self.saveWeights_btn = QtWidgets.QPushButton("save")
        self.saveWeightsUp_btn = QtWidgets.QPushButton("version up")
        self.loadWeights_btn = QtWidgets.QPushButton("load")

    def create_layout(self):
        # build rig
        rigBuild_layout = QtWidgets.QHBoxLayout()
        rigBuild_layout.addWidget(self.buildRig_btn)

        # publish rig steps
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.addWidget(self.saveControl_btn)
        control_layout.addWidget(self.saveControlUp_btn)
        control_layout.addWidget(self.loadControl_btn)
        control_formLayout = QtWidgets.QFormLayout()
        control_formLayout.addRow("controls:", control_layout)

        skinWeights_layout = QtWidgets.QHBoxLayout()
        skinWeights_layout.addWidget(self.saveWeights_btn)
        skinWeights_layout.addWidget(self.saveWeightsUp_btn)
        skinWeights_layout.addWidget(self.loadWeights_btn)
        skinWights_formLayout = QtWidgets.QFormLayout()
        skinWights_formLayout.addRow("skin weights:", skinWeights_layout)

        # main_layout from generic tabs
        self.main_layout.addLayout(rigBuild_layout)
        self.add_separator(self.main_layout)
        self.main_layout.addLayout(control_formLayout)
        self.main_layout.addLayout(skinWights_formLayout)

    def create_connections(self):



        self.buildRig_btn.clicked.connect(lambda: build_rig(self.project_dict, self.guides_cmb.currentText()))

    def refresh_widgets(self):
        pass


# class GuidesWidget(generictab.GenericWidget):
#     def __init__(self, parent=None, info=None):
#         super(GuidesWidget, self).__init__(parent)
#         # set project info
#         self.get_project_info(info)
#
#         # create generic setup
#         self.create_widgets()
#         self.create_layout()
#         self.create_connections()
#
#     def create_widgets(self):
#         self.guides_cmb = QtWidgets.QComboBox()
#         self.guides_cmb.addItems(get_files(self.project_dict["scene"], wildcard="*guides*"))
#
#         self.openGuide_btn = QtWidgets.QPushButton("open")
#         self.versionUpGuide_btn = QtWidgets.QPushButton("version+")
#
#         self.guidesLib_cmb = QtWidgets.QComboBox()
#         self.guidesLib_cmb.addItems(get_files(self.project_dict["guides"], ignore_files=[".mayaSwatches","__init__.py"]))
#         self.loadGuide_btn = QtWidgets.QPushButton("load")
#
#     def create_layout(self):
#         guides_layout = QtWidgets.QHBoxLayout()
#         guides_layout.addWidget(self.guides_cmb)
#         guides_layout.addWidget(self.openGuide_btn)
#         guides_layout.addWidget(self.versionUpGuide_btn)
#         form_layout = QtWidgets.QFormLayout()
#         form_layout.addRow("Guides:", guides_layout)
#
#         # guides lib
#         guidesLib_layout = QtWidgets.QHBoxLayout()
#         guidesLib_layout.addWidget(self.guidesLib_cmb)
#         guidesLib_layout.addWidget(self.loadGuide_btn)
#         guidesLib_formLayout = QtWidgets.QFormLayout()
#         guidesLib_formLayout.addRow("Library:", guidesLib_layout)
#
#         self.main_layout.addLayout(form_layout)
#         self.main_layout.addLayout(guidesLib_formLayout)
#
#     def create_connections(self):
#         self.openGuide_btn.clicked.connect(
#             lambda: open_scene(full_path=self.project_dict["scene"] + self.guides_cmb.currentText()))
#         self.versionUpGuide_btn.clicked.connect(version_up)
#
#     def refresh_widgets(self):
#         self.guides_cmb.clear()
#         self.guides_cmb.addItems(get_files(self.project_dict["scene"], wildcard="*guides*"))
#
#         self.guidesLib_cmb.clear()
#         self.guidesLib_cmb.addItems(get_files(self.project_dict["guides"], ignore_files=[".mayaSwatches","__init__.py"]))
# =============================================== MODULES ==============================================================



# def get_files(path, ignore_files=None, wildcard=None):
#
#         projects = os.listdir(path)
#
#         if wildcard:
#             projects_full = utilsLib.import_latest(path, wildcard)
#             projects = []
#             if projects_full:
#                 for i in [projects_full]:
#                     projects.append(i.split("/")[-1])
#         if ignore_files:
#             for ignore_file in ignore_files:
#                 projects.remove(ignore_file)
#
#         if not projects:
#             projects = ["none"]
#
#         return projects





# def open_scene(dict=None, step=None, full_path=None):
#
#     if full_path:
#         cmds.file(full_path, o=True, f=True, iv=True)
#     else:
#         count = 0
#         # this is for if guide so it saves guide
#         step = step if step else dict["step"]
#
#         latest_scene = utilsLib.version_by_integer(dict["scene"], "*%s*" % step, count )
#
#         if latest_scene:
#             cmds.file(latest_scene, o=True, f=True, iv=True)
#         else:
#             cmds.file(new=True, f=True)
#             cmds.file(rename=dict["scene"] + dict["asset"] + "_%s_v001" % step)
#             cmds.file(save=True, type='mayaAscii')

def version_up():
    """
    versions up latest scene
    :return:
    """

    path = "/".join(cmds.file(loc=True, q=True).split("/")[:-1])
    stream = (cmds.file(loc=True, q=True).split("/")[-1]).split("_")[1]

    # # for saving rigs after build
    # if cmds.file(loc=True, q=True).split("/")[-1] == self.asset_name+"_temp.ma":
    #     stream = "rigging"

    latest_scene = utilsLib.version_up_path(path, "*%s*"%stream)
    cmds.file(rename=latest_scene)
    cmds.file(save=True, type='mayaAscii')

    utilsLib.print_it("SAVED:   "+latest_scene)

# def publish_from_step(dict, variant):
#     folder_publish = dict["publish"] + variant + "/"
#
#     current_scene = (cmds.file(loc=True, q=True).split("/")[-1]).split(".")[0]
#     if current_scene and not current_scene == "unknown":
#         versionNumber = re.findall(r'\d+', current_scene)[0]
#
#         if os.path.isdir(folder_publish + "v"+versionNumber):
#             print "VERSION EXISTS, version up please"
#
#         else:
#             os.makedirs(folder_publish + "v"+versionNumber)
#             objects = cmds.ls(selection=True)
#             save_alembic(objects, folder_publish + "v"+versionNumber+"/"+current_scene)
#             save_obj(objects, folder_publish + "v"+versionNumber+"/"+current_scene)
#     else:
#         print "SAVE YOUR SCENE IN THE RIGHT STEP BEFORE PUBLISHING"

# def load_publish(dict, variant):
#     folder_publish = dict["publish"] + variant + "/"
#
#     latest_publish = utilsLib.import_latest(folder_publish, "v*")
#     if latest_publish:
#         full_path = utilsLib.import_latest(latest_publish, "*v*.abc")
#         cmds.file(full_path, i=True, ignoreVersion=True)
#         print "LOADED LATEST PUBLISH FOR --- %s ---"%variant
#     else:
#         print "NO LATEST PUBLISH FOR --- %s ---"%variant

# def ref_publish(dict, variant):
#     folder_publish = dict["publish"] + variant + "/"
#
#     latest_publish = utilsLib.import_latest(folder_publish, "v*")
#     if latest_publish:
#         full_path = utilsLib.import_latest(latest_publish, "*v*.abc")
#         cmds.file(full_path, reference=True, ignoreVersion=True, ns=dict["asset"]+"_"+dict["step"])
#         print "REFERENCED LATEST PUBLISH FOR --- %s ---" % variant
#     else:
#         print "NO LATEST PUBLISH FOR --- %s ---" % variant



#
# def save_alembic(objects, path):
#
#     root = ""
#     for x in objects:
#         root = root + "-root %s " % x
#
#     save_name = path
#     if not save_name.endswith(".abc"):
#         save_name = save_name+".abc"
#
#     command = " -uvWrite -worldSpace -writeUvSets " + root + " -file " + save_name
#     cmds.AbcExport(j=command)
#
# def save_obj(objects, path):
#     cmds.select(objects)
#     cmds.file(path, pr=1, typ="OBJexport", es=1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")

# def open_folder(dict):
#     print "open folder"
#     print dict
#     if os.path.isdir(dict["scene"]):
#         os.startfile(dict["scene"])



def import_scene(path):
    cmds.file(path, i=True, ignoreVersion=True)





# RIG STUFF
def publish_skinWeights(dict, versionUp = False):
    """
    TODO: clean up geo and group finding
    in your selections if you have a group it will publish it to the same named stream
    if shape then it finds all groups above, if anim etc.. in name then it publishes to that group

    :param versionUp:
    :return: fuck all
    """


    streams_names = ["proxy","anim","render", "blendshape"]


    nodes = pm.selected()

    for node in nodes:
        # if useing selected geo
        nodeShape = node.getShape()

        if not nodeShape:
            # if transform selected then get decending geo
            geo = geometryLib.decending_geo(node)
            # group if selecting soemthing like anim_GRP as node
            grp = node

            streamCheck =[]
            for x in streams_names:
                if x + "_GRP" == str(grp):
                    streamCheck.append(x + "_GRP")
            if streamCheck:
                stream = streamCheck[0].split("_")[0]
                # publish weights
                folder = coreLib.save_to_path(folder=stream, asset_folder=dict["skinWeights"],
                                              versionUp=versionUp)
                kinematicsLib.xml_weights_out(folder, geometry=utilsLib.aslist(geo))
            else:
                print "PLEASE SELECT TOP FLODER - eg. ANIM_GRP"

        else:
            geo = node
            parents = cmds.ls(str(geo), long=True)[0].split('|')[1:-1]
            grp = []
            for x in streams_names:
                if x + "_GRP" in parents:
                    grp.append(x + "_GRP")

            stream = grp[0].split("_")[0]
            # publish weights
            folder = coreLib.save_to_path(folder=stream, asset_folder=dict["skinWeights"],
                                          versionUp=versionUp)
            kinematicsLib.xml_weights_out(folder, geometry=utilsLib.aslist(geo))


def build_rig(dict, guide_path):
    """
    build rig
    :param path: path only goes up till asset e.g  "E:/Files/3D/goblin"
    :return:
    """

    utilsLib.print_it("BUILDING: {0} {1}".format(dict["project"], dict["asset"]))

    cmds.file(new=True, f=True)
    import_scene(dict["scene"] + guide_path)

    char = characterSetup.CharacterSetup(dict["base_path"] + "/" + dict["project"] + "/" + dict["asset"])
    char.build_character()

def mirror_guide():

    orig_guide = pm.selected()[0]
    ns = orig_guide.split(":")[0]
    side = ns[0]
    if side == "L":
        flipped_side = "R"
    elif side == "R":
        flipped_side = "L"
    else:
        flipped_side = "dope"
    if pm.namespace(ex=flipped_side + ns[1:]):
        flipped_ns = flipped_side + ns[1:]
    else:
        flipped_ns = pm.namespace(add=flipped_side + ns[1:])

    # groups
    flip_guide = pm.duplicate(orig_guide)[0]
    guide_nodes = pm.listRelatives(flip_guide, ad=True, type="transform")
    # add namespace
    flip_guide.rename(":{0}:{1}".format(flipped_ns, flip_guide))
    [x.rename(":{0}:{1}".format(flipped_ns, x)) for x in guide_nodes]

    # flip attributes
    attrs = pm.listAttr(flip_guide, ud=True)
    for attr in attrs:
        my_input = pm.getAttr(flip_guide + "." + attr)

        if "L_" in my_input:
            pm.setAttr(flip_guide + "." + attr, my_input.replace("L_", "R_"))
        elif "R_" in my_input:
            pm.setAttr(flip_guide + "." + attr, my_input.replace("R_", "L_"))
        else:
            pass

    # mirror
    guide_JNTs = []
    guide_other = []
    for guide in guide_nodes:
        if guide.type() == "joint":
            guide_JNTs.append(guide)
        elif guide.endswith("GUIDE"):
            guide_other.append(guide)

    # ================== JOINTS
    # parents
    parent_dict = {}
    for guide in guide_JNTs:
        parent_dict[str(guide)] = cmds.listRelatives(str(guide), p=True)[0]
    # mirror
    for guide in guide_JNTs:
        children=None
        guide.setParent(w=True)
        if pm.listRelatives(guide, c=True):
            children = pm.listRelatives(guide, c=True)
            pm.parent(children, w=True)
        new_joints = pm.mirrorJoint(guide, mirrorYZ=True, mirrorBehavior=True)
        pm.delete(guide)

        if children:
            pm.parent(children, new_joints[0])
        [pm.rename(x, ":{0}:{1}".format(flipped_ns, x)) for x in new_joints]



    for key, value in parent_dict.items():
        pm.parent(key, value)


    # ==================== OTHER
    parent_dict = {}
    for guide in guide_other:
        parent_dict[guide] = pm.listRelatives(guide, p=True)[0]

    for guide in guide_other:
        guide.setParent(w=True)

        if "mirror" in pm.listAttr(guide):
            if pm.getAttr(guide.mirror):
                # flipped position
                flip_GRP = pm.group(em=True, name=guide+"_flip_GRP")
                guide.setParent(flip_GRP)
                pm.setAttr(flip_GRP + ".scaleX", -1)


        else:
            transformLib.flip_without_orient(guide)





    for key, value in parent_dict.items():
        if "mirror" in pm.listAttr(guide):
            if pm.getAttr(guide.mirror):
                key.getParent().setParent(value)
        else:
            key.setParent(value)






if __name__ == "pup.mayaGUI.pupui":

    try:
        open_import_dialog.close()
        open_import_dialog.deleteLater()
    except:
        pass

    open_import_dialog = PupUI()
    print open_import_dialog
    print "OPENDED PUPUI"
    open_import_dialog.show()



