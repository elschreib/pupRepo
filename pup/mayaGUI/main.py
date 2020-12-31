import maya.cmds as cmds
import os

from ..library import utilsLib

from pup.shelf import dataInOut
data = dataInOut.DataInOut("")

from pup.pipeline import pipefunctions
pip = pipefunctions.PipeFunctions()


projectsPath = "E:/Files/3D/"

path = []
class Main(object):

    def __init__(self):

        self.title = "PUP_GUI"


    def setupUI(self):
        # create a main layout
        mainLayout = cmds.columnLayout(w=300, h=300)

        # banner image
        imagePath = pip.projectsPath+"_Resources/pref_images/ash_32x32.png"  # cmds.internalVar(upd=True) + "icons/"

        cmds.image(w=32, h=32, image=imagePath)
        cmds.separator(h=15)

        self.project_set()

        # # create character option menu
        # stepOptionMenu = cmds.optionMenu("stepOptionMenu", w=200, label="Step:     ")
        # self.populateSteps()



        #CREATE TABS
        self.createTabs()

    #CREATE PROJECT STUFF AT TOP
    def project_set(self):
        #create text
        cmds.rowColumnLayout(numberOfColumns=3, columnAttach=(1, 'left', 0), columnWidth=[(1, 100), (2, 200)])
        cmds.text(label='createProject')
        self.projectNameField = cmds.textField("projectName", h=20, w=100)
        cmds.button("create", c=self.create_project_button)


        # cmds.textField(projectNameField, edit=True, enterCommand=('self.create_project_button(%s)'%textFieldData))



        mainLayout2 = cmds.columnLayout(w=400, h=300)


        # create projects option menu
        projectsOptionMenu = cmds.optionMenu("projectsOptionMenu", w=200, label="Project: ", cc=self.createTabs)
        self.populateProjects()
        cmds.separator(h=15)



    def populateProjects(self):
        """
        populate the projects optionsMenu
        """

        projects = os.listdir(pip.projectsPath)
        projectsClean = utilsLib.remove_items_with(projects)

        for project in projectsClean:
            cmds.menuItem(label=project, parent="projectsOptionMenu")

    def populateSteps(self,*args):
        """
        populate the projects optionsMenu
        """
        menuItems = cmds.optionMenu("stepOptionMenu", q=True, itemListLong=True)
        if menuItems:
            for item in menuItems:
                cmds.deleteUI(item)

        selectedProject = pip.projectsPath + cmds.optionMenu("projectsOptionMenu", q=True, v=True) + "/"

        files = os.listdir(selectedProject)
        filesClean = utilsLib.remove_items_with(files)

        for file in filesClean:
            cmds.menuItem(label=file, parent="stepOptionMenu")

        print "change"


    # CREATE PROJECT TABS
    def createTabs(self, *args):

        pip.set_asset(cmds.optionMenu("projectsOptionMenu", q=True, v=True))


        tabs = cmds.tabLayout(w=400, h=300)

        self.modelTab()
        # self.textureTab()
        # self.lightingTab()
        # self.lookdevTab()
        # self.riggingTab()

        cmds.tabLayout(tabs, edit=True, tabLabel=((self.modelTabChild, 'Model'),
                                                  (self.modelTabChild, 'texture'),
                                                  (self.modelTabChild, 'lighting'),
                                                  (self.modelTabChild, 'lookdev'),
                                                  (self.modelTabChild, 'rigging')))




        # # create button
        # cmds.separator(h=15)
        # cmds.button(label="buttonz", w=300, h=50)  # c=command
        # cmds.separator(h=15)

    def defaultTab(self, *args):



        cmds.button("openScene", h=20, w=100, align="left", c=self.openScene)
        cmds.button("saveScene", h=20, w=100, align="right",  c=self.openScene)

        # cmds.rowColumnLayout(numberOfColumns=3, columnAttach=(1, 'left', 0), columnWidth=[(1, 100), (2, 200)])
        cmds.button("+", h=20, w=20, align="left")
        cmds.button("-", h=20, w=20, align="center")
        cmds.text(label='counter', align="right")

    def modelTab(self):
        self.modelTabChild = cmds.rowColumnLayout(numberOfColumns=2)
        self.defaultTab()
        cmds.setParent('..')

    def textureTab(self):
        self.textureTabChild = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.setParent('..')

    def lightingTab(self):
        self.lightingTabChild = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.setParent('..')

    def lookdevTab(self):
        self.lookdevTabChild = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.setParent('..')

    def riggingTab(self):
        self.riggingTabChild = cmds.rowColumnLayout(numberOfColumns=2)
        imagePath = pip.projectsPath+"_Resources/pref_images/shoggoth.png"  # cmds.internalVar(upd=True) + "icons/"
        cmds.image(w=32, h=32, image=imagePath)
        cmds.separator(h=15)

        cmds.setParent('..')








    # FUNCTIONS
    def openScene(self, *args):
        pip.open_model()

    def create_project_button(self, *args):
        textFieldData = cmds.textField(self.projectNameField, editable=True, query=True, text=True)
        print "CREATING PROJECT - " + textFieldData
        pip.create_project(textFieldData)







    def run(self):

        if cmds.window(self.title, exists=True):
            cmds.deleteUI(self.title)

        window = cmds.window(self.title, title=self.title, w=350, h=300, mxb=False, sizeable=True)


        self.setupUI()



        cmds.showWindow(window)





        # self.project_path = "E:/Files/3D"
        # # SETUP FOR BUILD -- CHECKS FOR FOLDERS, IF THERE IT WILL BUILD
        # data.project_load(self.project_path)





