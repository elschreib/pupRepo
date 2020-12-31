import maya.cmds as cmds
import os
import glob
import sys
import shutil
from functools import partial
import pkgutil

folder_dict = {'assemblies': '', 'characters': '', 'data': ['control_curves', 'guides'], 'parts': ''}

toolFolder = os.path.dirname(__file__)

templatesFolder = toolFolder + '/templates'

userHomeFolder = os.environ["HOME"]
user = os.environ["USERNAME"]

userGitFolder = '/job/comms/pipeline/dev/' + user + "er" + '/git/commsrigging'
userPrefsFolder = userHomeFolder + '/pacman'

if not os.path.isdir(userPrefsFolder):
    os.makedirs(userPrefsFolder)

if not os.path.isdir(userGitFolder):
    userGitFolder = '/job/comms/pipeline/dev/' + user + '/commsrigging'

assetsFolder = userGitFolder + '/pacldn/assets'


side_dict = {1: 'L', 2: 'C', 3: 'R', 4: 'Other'}


class Pacman:
    def __init__(self):
        self.windowHandle = None

        self.pacmanWindow()


    def pacmanWindow(self):
        size = [464, 335]
        # create window name
        self.windowHandle = 'pacmanWindow'

        # delete if there
        if cmds.window(self.windowHandle, query=True, exists=True):
            cmds.deleteUI(self.windowHandle, window=True)

        # create window ================================================================================================
        cmds.window(self.windowHandle, title='PACMAN')

        # create a frameLayout
        cmds.frameLayout(lv=False, mh=5, mw=5)
        cmds.columnLayout('mainLayout', adj=True)
        # another frameLayout with title
        cmds.frameLayout(label='Asset package:')
        cmds.columnLayout(adj=True)

        # top text field that creates ==================================================================================
        cmds.textFieldButtonGrp('packageNameCtl',
                                label='Name: ',
                                buttonLabel=' Create ',
                                buttonCommand=partial(self.make, 'package'))

        # creates the package list optionMenu ==========================================================================
        cmds.optionMenuGrp('existingPackagesCtl', label='Package list: ', changeCommand=self.get_all_package_data)

        # frameLayout for next section =================================================================================
        cmds.frameLayout(label='Build and create:')
        form = cmds.formLayout()

        # create tab layout linking to select_tab ======================================================================
        cmds.tabLayout('tabLayout', innerMarginWidth=5, innerMarginHeight=5, selectCommand=self.select_tab)
        # formLayout for tabs
        cmds.formLayout(form, edit=True,
                        attachForm=(('tabLayout', 'top', 0),
                                    ('tabLayout', 'left', 0),
                                    ('tabLayout', 'bottom', 0),
                                    ('tabLayout', 'right', 0)))

        # ==============================================================================================================
        # PARTS TAB:
        # ==============================================================================================================
        # create a tab layout
        partTab = cmds.columnLayout(adj=True)

        # part optionMenu ==============================================================================================
        cmds.optionMenuGrp('partListCtl', label='Part: ')
        # menu for the side selection ==================================================================================
        cmds.radioButtonGrp('partSideCtl',
                            label='Side: ',
                            nrb=4,
                            labelArray4=('L', 'C', 'R', 'Other/Use default'),
                            select=4,
                            cw5=(140, 50, 50, 50, 50),
                            changeCommand=partial(self.change_side, 'partSideCtl', 'partOtherSideCtl'))
        # optional text field ==========================================================================================
        cmds.textFieldGrp('partOtherSideCtl', label='Side: ', enable=False)
        # asset guide text field
        cmds.textFieldButtonGrp('partAssetGuideCtl',
                                label='Asset guide: ',
                                buttonLabel=' Load ',
                                buttonCommand=self.load_guide,  # button
                                pht='Right-click for previously used guides...')  # soft text visibile in box
        # popup menu child of text field
        cmds.popupMenu('partAssetGuideCtl_popupMenu', parent='partAssetGuideCtl')
        # optionMenu with local guides
        cmds.optionMenuGrp('partLocalGuidesCtl', label='Local guides: ', enable=False, changeCommand=self.change_part)
        # checkBox for use job
        cmds.checkBoxGrp('partUseJobCtl', label='Use job: ', value1=True, changeCommand=self.part_use_job)
        # when done set to parent 'tabLayout'
        cmds.setParent('tabLayout')

        # ==============================================================================================================
        # ASSEMBLY TAB:
        # ==============================================================================================================

        assemblyTab = cmds.columnLayout(adj=True)

        cmds.optionMenuGrp('assemblyListCtl', label='Assembly: ')

        cmds.textFieldButtonGrp('assemblyUseAssetGuide',
                                label='Asset guide: ',
                                buttonLabel=' Load ',
                                buttonCommand=self.load_guide,
                                pht='Right-click for previously used guides...')

        cmds.popupMenu('assemblyUseAssetGuide_popupMenu', parent='assemblyUseAssetGuide')

        cmds.optionMenuGrp('assemblyLocalGuidesCtl',
                           label='Local guides: ',
                           changeCommand=self.change_assembly,
                           enable=False)
        cmds.checkBoxGrp('assemblyUseJob', label='Use job: ', value1=True, changeCommand=self.assembly_use_job)

        cmds.setParent('tabLayout')

        # ==============================================================================================================
        # CHARACTER TAB:
        # ==============================================================================================================

        characterTab = cmds.columnLayout(adj=True)

        cmds.optionMenuGrp('charAssemblyListCtl', label='Use assembly: ')
        cmds.optionMenuGrp('charCharacterListCtl', label='Character: ', changeCommand=self.get_class_names)
        cmds.optionMenuGrp('charCharacterClassListCtl', label='Character class: ')

        cmds.setParent('tabLayout')

        # ==============================================================================================================
        # CREATE TAB:
        # ==============================================================================================================
        # create rowColumnLayout
        createTab = cmds.rowColumnLayout(numberOfColumns=2)
        # createLayout
        cmds.columnLayout('createLayout', adj=True)

        cmds.radioButtonGrp('createDefaultSideCtl',
                            label='Default side: ',
                            nrb=4,
                            labelArray4=('L', 'C', 'R', 'Other'),
                            select=1,
                            cw5=(140, 50, 50, 50, 50),
                            changeCommand=partial(self.change_side, 'createDefaultSideCtl', 'createOtherSideCtl'))

        cmds.textFieldGrp('createOtherSideCtl', label='Side: ', enable=False)

        cmds.textFieldButtonGrp('partNameCtl',
                                label='Part name: ',
                                buttonLabel=' Create ',
                                buttonCommand=partial(self.make, 'part'),
                                changeCommand=partial(self.make, 'part'))

        cmds.separator(height=12, style='in')

        cmds.textFieldButtonGrp('assemblyNameCtl',
                                label='Assembly name: ',
                                buttonLabel=' Create ',
                                buttonCommand=partial(self.make, 'assembly'),
                                changeCommand=partial(self.make, 'assembly'))

        cmds.textFieldButtonGrp('characterNameCtl',
                                label='Character name: ',
                                buttonLabel=' Create ',
                                buttonCommand=partial(self.make, 'character'),
                                changeCommand=partial(self.make, 'character'))

        cmds.setParent('mainLayout')

        # ======================================================================================================================
        # FINALIZE
        # ======================================================================================================================

        # create buttons
        cmds.button('buildButtonCtl', label='Build', command=self.pre_build)
        cmds.button(label='Refresh window', command=self.get_packages)
        cmds.button(label='Reload core', command=self.reload_core)

        # add the tabs to the tabLayout
        cmds.tabLayout('tabLayout',
                       edit=True,
                       tabLabel=((partTab, 'Parts'),
                                 (assemblyTab, 'Assemblies'),
                                 (characterTab, 'Characters'),
                                 (createTab, 'Create')))
        # CHECK
        self.get_packages()
        # CHECK
        self.fill_guide_menu()

        # edit window
        cmds.window(self.windowHandle, edit=True, wh=size, sizeable=False)
        # show window
        cmds.showWindow(self.windowHandle)

    # ======================================================================================================================
    # UI state:
    # ======================================================================================================================

    def select_tab(self, *args):
        visibleTab = cmds.tabLayout('tabLayout', query=True, selectTabIndex=True)

        # change build button depending on tab
        if visibleTab < 4:
            cmds.button('buildButtonCtl', edit=True, enable=True)
        else:
            cmds.button('buildButtonCtl', edit=True, enable=False)

    def clear_menu(self, controlName=None):
        numberOfItems = cmds.optionMenuGrp(controlName, query=True, numberOfItems=True)

        if numberOfItems >= 1:
            items = cmds.optionMenuGrp(controlName, query=True, itemListLong=True)

            cmds.deleteUI(items)

    def assembly_use_job(self, *args):
        state = cmds.checkBoxGrp('assemblyUseJob', query=True, value1=True)

        self.package_contents(component='/data/guides', controlName='assemblyLocalGuidesCtl')

        if state:
            cmds.textFieldGrp('assemblyUseAssetGuide', edit=True, text='')

            cmds.optionMenuGrp('assemblyLocalGuidesCtl', edit=True, enable=False)
        else:
            cmds.optionMenuGrp('assemblyLocalGuidesCtl', edit=True, enable=True)

            value = cmds.optionMenuGrp('assemblyLocalGuidesCtl', query=True, value=True)

            cmds.textFieldGrp('assemblyUseAssetGuide', edit=True, text=value)

    def change_assembly(self, *args):
        value = cmds.optionMenuGrp('assemblyLocalGuidesCtl', query=True, value=True)

        cmds.textFieldGrp('assemblyUseAssetGuide', edit=True, text=value)

    def part_use_job(self, *args):
        state = cmds.checkBoxGrp('partUseJobCtl', query=True, value1=True)

        self.package_contents(component='/data/guides', controlName='partLocalGuidesCtl')

        if state:
            cmds.textFieldButtonGrp('partAssetGuideCtl', edit=True, text='')

            cmds.optionMenuGrp('partLocalGuidesCtl', edit=True, enable=False)
        else:
            cmds.optionMenuGrp('partLocalGuidesCtl', edit=True, enable=True)

            value = cmds.optionMenuGrp('partLocalGuidesCtl', query=True, value=True)

            cmds.textFieldButtonGrp('partAssetGuideCtl', edit=True, text=value)

    def change_part(self, *args):
        value = cmds.optionMenuGrp('partLocalGuidesCtl', query=True, value=True)

        cmds.textFieldButtonGrp('partAssetGuideCtl', edit=True, text=value)

    def change_side(self, radioControl=None, controlName=None, *args):
        selectedSide = cmds.radioButtonGrp(radioControl, query=True, select=True)

        if selectedSide == 4:
            cmds.textFieldGrp(controlName, edit=True, enable=True)
        else:
            cmds.textFieldGrp(controlName, edit=True, enable=False)

    # ======================================================================================================================
    # CREATE P, A, C files:
    # ======================================================================================================================

    def make(self, mode=None, *args):
        selectedPackage = cmds.optionMenuGrp('existingPackagesCtl', query=True, value=True)

        if mode == 'package':
            packageName = cmds.textFieldButtonGrp('packageNameCtl', query=True, text=True)

            if packageName:
                cmds.waitCursor(state=True)

                packageName = '{0}{1}'.format(packageName[0].capitalize(), packageName[1:])
                packageName = packageName.replace('_', '')
                packageName = packageName.replace(' ', '')
                packageName = packageName.replace('-', '')

                packageRootFolder = assetsFolder + '/' + packageName

                if not os.path.isdir(packageRootFolder):
                    os.makedirs(packageRootFolder)

                # copy package loader init:
                shutil.copyfile(templatesFolder + '/package_init.py',
                                packageRootFolder + '/__init__.py')

                for rootFolder in folder_dict.keys():
                    os.makedirs(packageRootFolder + '/' + rootFolder)

                    # copy blank init:
                    shutil.copyfile(templatesFolder + '/__init__.py',
                                    packageRootFolder + '/' + rootFolder + '/__init__.py')

                    for folder in folder_dict[rootFolder]:
                        os.makedirs(packageRootFolder + '/' + rootFolder + '/' + folder)

                        # copy blank init:
                        shutil.copyfile(templatesFolder + '/__init__.py',
                                        packageRootFolder + '/' + rootFolder + '/' + folder + '/__init__.py')

                # self.add_to_git(path='pacldn/assets/{0}'.format(packageName),
                #                 message='Initial commit of old asset package, [{0}] on job branch [{1}]"'.format(
                #                     packageName,
                #                     branch))

                cmds.waitCursor(state=False)

            cmds.textFieldButtonGrp('packageNameCtl', edit=True, text='')

        if mode == 'part' and selectedPackage:
            selectedSide = cmds.radioButtonGrp('createDefaultSideCtl', query=True, select=True)

            if selectedSide == 4:
                side = cmds.textFieldGrp('createOtherSideCtl', query=True, text=True)
            else:
                side = side_dict[selectedSide]

            partName = cmds.textFieldButtonGrp('partNameCtl', query=True, text=True)

            if partName and side:
                cmds.waitCursor(state=True)

                partName = partName.lower()
                partName = partName.replace(' ', '')
                partName = partName.replace('_', '')
                partName = partName.replace('-', '')

                partsFolder = assetsFolder + '/' + selectedPackage + '/parts'

                fileId = open(templatesFolder + '/part.py', 'r')

                partLines = fileId.readlines()

                fileId.close()

                partLines[12] = partLines[12].replace('partName', partName)
                partLines[18] = partLines[18].replace("self.side = 'L'", "self.side = '{0}'".format(side))

                newPartFilename = partsFolder + '/{0}.py'.format(partName)

                newFileId = open(newPartFilename, 'w')

                newFileId.writelines(partLines)

                newFileId.close()

                # self.add_to_git(path='pacldn/assets/{0}/parts/{1}.py'.format(selectedPackage, partName),
                #                 message='Added old part, [{0}] for asset package [{1}]"'.format(partName,
                #                                                                                 selectedPackage))

                cmds.waitCursor(state=False)

            cmds.textFieldButtonGrp('partNameCtl', edit=True, text='')

        if mode == 'assembly' and selectedPackage:
            assemblyName = cmds.textFieldButtonGrp('assemblyNameCtl', query=True, text=True)

            if assemblyName:
                cmds.waitCursor(state=True)

                assemblyName = assemblyName.lower()
                assemblyName = assemblyName.replace(' ', '')
                assemblyName = assemblyName.replace('_', '')
                assemblyName = assemblyName.replace('-', '')

                assemblyFolder = assetsFolder + '/' + selectedPackage + '/assemblies'

                fileId = open(templatesFolder + '/assembly.py', 'r')

                assemblyLines = fileId.readlines()

                fileId.close()

                assemblyLines[21] = assemblyLines[21].replace('assemblyName', assemblyName)

                newAssemblyFilename = assemblyFolder + '/{0}.py'.format(assemblyName)

                newFileId = open(newAssemblyFilename, 'w')

                newFileId.writelines(assemblyLines)

                newFileId.close()

                # self.add_to_git(path='pacldn/assets/{0}/assemblies/{1}.py'.format(selectedPackage, assemblyName),
                #                 message='Added old assembly, [{0}] for asset package [{1}]"'.format(
                #                     assemblyName,
                #                     selectedPackage))

                cmds.waitCursor(state=False)

            cmds.textFieldButtonGrp('assemblyNameCtl', edit=True, text='')

        if mode == 'character' and selectedPackage:
            characterName = cmds.textFieldButtonGrp('characterNameCtl', query=True, text=True)

            if characterName:
                cmds.waitCursor(state=True)

                characterName = '{0}{1}'.format(characterName[0].capitalize(), characterName[1:])
                characterName = characterName.replace('_', '')
                characterName = characterName.replace(' ', '')
                characterName = characterName.replace('-', '')

                characterFolder = assetsFolder + '/' + selectedPackage + '/characters'

                fileId = open(templatesFolder + '/character.py', 'r')

                lines = fileId.readlines()

                lines[18] = lines[18].replace('CharacterAssetName', characterName)

                fileId.close()

                newFilename = characterFolder + '/{0}.py'.format(characterName)

                newFileId = open(newFilename, 'w')

                newFileId.writelines(lines)

                newFileId.close()

                # self.add_to_git(path='pacldn/assets/{0}/characters/{1}.py'.format(selectedPackage, characterName),
                #                 message='Added old character, [{0}] for asset package [{1}]"'.format(
                #                     characterName,
                #                     selectedPackage))

                cmds.waitCursor(state=False)

            cmds.textFieldButtonGrp('characterNameCtl', edit=True, text='')

        self.get_packages()

    # ======================================================================================================================
    # READ AND WRITE DATA:
    # ======================================================================================================================

    def fill_guide_menu(self):
        guideNames = self.user_data(mode='read')

        if guideNames:
            for popup in ('partAssetGuideCtl_popupMenu', 'assemblyUseAssetGuide_popupMenu'):
                cmds.popupMenu(popup, edit=True, deleteAllItems=True)

                for guide in guideNames:
                    if guide:
                        cmds.menuItem(label=guide.strip(),
                                      parent=popup,
                                      command=partial(self.fill_guide, guide, popup.split('_')[0]))

    def fill_guide(self, guide=None, control=None, *args):
        cmds.textFieldGrp(control, edit=True, text=guide.strip())

    def user_data(self, mode=None):
        selectedPackage = cmds.optionMenuGrp('existingPackagesCtl', query=True, value=True)
        prefsFile = userPrefsFolder + '/pacman_guides.{0}'.format(selectedPackage)

        if not os.path.isfile(prefsFile):
            fileId = open(prefsFile, 'w')
            fileId.close()

        if mode == 'read':
            fileId = open(prefsFile, 'r')

            guideNames = fileId.readlines()

            fileId.close()

            return guideNames

        if mode == 'write':
            finalGuideList = []

            localGuides = self.package_contents(component='/data/guides', returnData=True)

            currentGuideList = cmds.popupMenu('partAssetGuideCtl_popupMenu', query=True, itemArray=True)
            partGuide = cmds.textFieldButtonGrp('partAssetGuideCtl', query=True, text=True)
            assemblyGuide = cmds.textFieldGrp('assemblyUseAssetGuide', query=True, text=True)

            if currentGuideList:
                for guide in currentGuideList:
                    label = cmds.menuItem(guide, query=True, label=True)

                    finalGuideList.append(label)

                finalGuideList.append(partGuide)
                finalGuideList.append(assemblyGuide)
            else:
                finalGuideList = [partGuide, assemblyGuide]

            # remove local guides, as the right-click menu should only contain show side asset names:
            for localGuide in localGuides:
                if localGuide in finalGuideList:
                    finalGuideList.remove(localGuide)

            if finalGuideList:
                finalGuideList = set(finalGuideList)

                fileId = open(prefsFile, 'w')

                for guide in finalGuideList:
                    if guide:
                        fileId.write(guide.strip() + '\n')

                fileId.close()

                self.fill_guide_menu()

    # ======================================================================================================================
    # GET PACKAGE DETAILS:
    # ======================================================================================================================

    def get_packages(self, returnSelected=False):
        packages = os.listdir(assetsFolder)

        # clear option menu:
        numberOfItems = cmds.optionMenuGrp('existingPackagesCtl', query=True, numberOfItems=True)

        if numberOfItems >= 1 and not returnSelected:
            items = cmds.optionMenuGrp('existingPackagesCtl', query=True, itemListLong=True)

            cmds.deleteUI(items)

        if returnSelected:
            selectedPackage = cmds.optionMenuGrp('existingPackagesCtl', query=True, value=True)

            return selectedPackage
        else:
            if packages:
                packages.remove('common')
                packages.remove('sandbox')
                packages.remove('__init__.py')

                packages.sort()

                for package in packages:
                    cmds.menuItem(label=package, parent='existingPackagesCtl|OptionMenu')

                self.get_all_package_data()

    def get_all_package_data(self, *args):
        self.package_contents(component='parts', controlName='partListCtl')
        self.package_contents(component='assemblies', controlName='assemblyListCtl')
        self.package_contents(component='/data/guides', controlName='assemblyLocalGuidesCtl')
        self.package_contents(component='/data/guides', controlName='partLocalGuidesCtl')
        self.package_contents(component='characters', controlName='charCharacterListCtl')
        self.package_contents(component='assemblies', controlName='charAssemblyListCtl')

        self.get_class_names()
        self.fill_guide_menu()

        cmds.textFieldButtonGrp('assemblyUseAssetGuide', edit=True, text='')
        cmds.textFieldButtonGrp('partAssetGuideCtl', edit=True, text='')

    def package_contents(self, component=None, controlName=None, returnData=False):
        selectedPackage = self.get_packages(returnSelected=True)

        fileList = os.listdir(assetsFolder + '/' + selectedPackage + '/' + component)

        if not returnData:
            self.clear_menu(controlName=controlName)

        returnList = []

        if fileList:
            fileList.sort()

            for item in fileList:
                if '__' not in item:
                    item = item.split('.')[0]
                    item = item.replace('_guide', '')

                    if not returnData:
                        cmds.menuItem(label=item, parent='{0}|OptionMenu'.format(controlName))

                    returnList.append(item)

        return returnList

    def get_class_names(self):
        selectedPackage = self.get_packages(returnSelected=True)
        selectedCharacterFile = cmds.optionMenuGrp('charCharacterListCtl', query=True, value=True)

        characterFile = assetsFolder + '/' + selectedPackage + '/characters/' + selectedCharacterFile + '.py'

        fileId = open(characterFile, 'r')

        allLines = fileId.readlines()

        fileId.close()

        self.clear_menu(controlName='charCharacterClassListCtl')

        if allLines:
            for line in allLines:
                if '(pacman.Character)' in line and 'class' in line:
                    characterClass = line.replace('(pacman.Character):', '')
                    characterClass = characterClass.replace('class ', '')

                    characterClass = characterClass.strip()

                    cmds.menuItem(label=characterClass, parent='charCharacterClassListCtl|OptionMenu')

    # ======================================================================================================================
    # CORE AND PACKAGE RELOADING:
    # ======================================================================================================================

    def reload_core(self, *args):
        if pkgutil.find_loader('pacldn'):
            del sys.modules['pacldn']

        core_reload_command = 'from pacldn import pacman; reload(pacman)'

        cmds.evalDeferred(core_reload_command)

    def reload_asset_package(self, *args):
        selectedPackage = self.get_packages(returnSelected=True)

        if pkgutil.find_loader(selectedPackage):
            del sys.modules[selectedPackage]

        asset_package_reload_command = 'from pacldn.assets import {0}; reload({1})'.format(selectedPackage,
                                                                                           selectedPackage)

        cmds.evalDeferred(asset_package_reload_command)

    # ======================================================================================================================
    # LOAD GUIDE:
    # ======================================================================================================================

    def load_guide(self, *args):
        guideFiles = None
        selectedPackage = self.get_packages(returnSelected=True)

        guideName = cmds.textFieldButtonGrp('partAssetGuideCtl', query=True, text=True)
        useJob = cmds.checkBoxGrp('partUseJobCtl', query=True, value1=True)

        if guideName:
            if useJob:
                guidePath = os.path.join(os.path.sep,
                                         'job',
                                         'comms',
                                         # branch,
                                         'asset',
                                         guideName,
                                         'work',
                                         'rig',
                                         'rig',
                                         'maya',
                                         'scenes')

                if os.path.isdir(guidePath):
                    guideFiles = glob.glob('{0}{1}{2}_rig_guide_v*.mb'.format(guidePath, os.path.sep, guideName))
            else:
                guidePath = os.path.join(os.path.sep,
                                         'job',
                                         'comms',
                                         'pipeline',
                                         'dev',
                                         user,
                                         'commsrigging',
                                         'pacldn',
                                         'assets',
                                         selectedPackage,
                                         'data',
                                         'guides')

                if os.path.isdir(guidePath):
                    guideFiles = glob.glob('{0}{1}{2}_guide.mb'.format(guidePath, os.path.sep, guideName))

            if guideFiles:
                guideFiles.sort()
                guideFiles.reverse()

                if os.path.isfile(guideFiles[0]):
                    cmds.file(guideFiles[0], open=True, force=True)

    # ======================================================================================================================
    # BUILD:
    # ======================================================================================================================

    def pre_build(self, *args):
        self.reload_asset_package()

        visibleTab = cmds.tabLayout('tabLayout', query=True, selectTabIndex=True)

        if visibleTab == 1:
            self.build_part()

        if visibleTab == 2:
            self.build_assembly()

        if visibleTab == 3:
            self.build_character()

        if visibleTab < 4:
            self.user_data(mode='write')

    def build_character(self):
        selectedPackage = self.get_packages(returnSelected=True)

        assembly = cmds.optionMenuGrp('charAssemblyListCtl', query=True, value=True)
        character = cmds.optionMenuGrp('charCharacterListCtl', query=True, value=True)
        characterClass = cmds.optionMenuGrp('charCharacterClassListCtl', query=True, value=True)

        assCommand = 'ass = {0}.assemblies.{1}.{2}()'.format(selectedPackage,
                                                             assembly,
                                                             assembly)

        charCommand = 'char = {0}.characters.{1}.{2}()'.format(selectedPackage,
                                                               character,
                                                               characterClass)

        characterCommand = '{0};{1};pacman.Character.build(char, ass)'.format(assCommand, charCommand)

        cmds.evalDeferred(characterCommand)

    def build_assembly(self):
        selectedPackage = self.get_packages(returnSelected=True)

        assembly = cmds.optionMenuGrp('assemblyListCtl', query=True, value=True)
        guide = cmds.textFieldGrp('assemblyUseAssetGuide', query=True, text=True)
        useJob = cmds.checkBoxGrp('assemblyUseJob', query=True, value1=True)

        if guide:
            objectInitCommand = 'ass = {0}.assemblies.{1}.{2}()'.format(selectedPackage, assembly, assembly)

            if useJob:
                assCommand = 'pacman.Assembly.build(assembly_object=ass, asset_name="{0}", use_job=True)'.format(guide)
            else:
                assCommand = 'pacman.Assembly.build(assembly_object=ass, asset_name="{0}", package_name="{1}", use_job=False)'.format(
                    guide,
                    selectedPackage)

            cmds.file(new=True, force=True)

            cmds.evalDeferred(objectInitCommand)
            cmds.evalDeferred(assCommand)
        else:
            cmds.confirmDialog(title='\tPACMAN: Build assembly error\t\t',
                               message='Please specify an asset guide.',
                               button='Sure',
                               parent=self.windowHandle)

    def build_part(self):
        selectedPackage = self.get_packages(returnSelected=True)

        part = cmds.optionMenuGrp('partListCtl', query=True, value=True)
        selectedSide = cmds.radioButtonGrp('partSideCtl', query=True, sl=True)
        assetGuide = cmds.textFieldButtonGrp('partAssetGuideCtl', query=True, text=True)
        useJob = cmds.checkBoxGrp('partUseJobCtl', query=True, value1=True)

        if selectedSide == 4:
            side = cmds.textFieldGrp('partOtherSideCtl', query=True, text=True)
        else:
            side = side_dict[selectedSide]

        if assetGuide:
            if side:
                partInitCommand = 'partObject = {0}.parts.{1}.{2}(side="{3}")'.format(selectedPackage, part, part, side)
            else:
                partInitCommand = 'partObject = {0}.parts.{1}.{2}(side=None)'.format(selectedPackage, part, part)

            if useJob:
                partCommand = 'pacman.Part.build(part_object=partObject, asset_name="{0}", use_job=True, remove_guide=True)'.format(
                    assetGuide)
            else:
                partCommand = 'pacman.Part.build(part_object=partObject, asset_name="{0}", use_job=False, remove_guide=True)'.format(
                    assetGuide)

            cmds.file(new=True, force=True)

            cmds.evalDeferred(partInitCommand)
            cmds.evalDeferred(partCommand)
        else:
            cmds.confirmDialog(title='\tPACMAN: Build part error\t\t',
                               message='Please specify an asset guide.',
                               button='Sure',
                               parent=self.windowHandle)
