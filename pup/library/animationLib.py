import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


from . import constraintsLib



def create_space_switch(destination=None,
                        targets=None,
                        targetNames=None,
                        control=None,
                        spaceAttributeName='space',
                        default=0,
                        translate=True,
                        rotate=True,
                        keyable=True,
                        maintainOffset=True,
                        asEnum=True):
    """
        Description:
            Creates a space switch network and creates an enum attribute in order to control it.
            Is an additive process which means it can be called again with old names and targets without
            affecting existing switches. The "targets" list length and the "targetNames" list length need to match.

        Flags:
            destination: The node that will move between the given targets.
            targets: A list of nodes that the "destination" node will move between.
            targetNames: A list of nice names for the targets. Must match the number of targets.
            spaceAttributeName: The name for the attribute that appears on the control.
            default: The initial setting for the enum.
            translate: Include translation in the space switch or not. This is so controls can have their
                       rotation and translation separated - like in a neck or head.
            rotate: Include the rotation in the space switch.
            keyable: Whether the enum can be key-frameable.
            maintainOffset: Optional setting, but defaults to True which is prefereable in most cases.
            asEnum: Create the space switches on an enum (drop-list) attribute on the control under one
                    attribute name. Setting to False will leave the targets as a list of float attributes on
                    the control. It makes the "spaceAttributeName" flag obsolete. Using this means you need unique
                    target names.

        Example:

                create_space_switch(destination='C_neck_001_CTL_GRP',
                                    targets=['C_spine_001_JNT', 'C_global_001_CTL'],
                                    targetNames=['spine', 'world']

        Return:
            None.

    """

    if len(targetNames) == len(targets):
        theConstraint = None

        if asEnum:
            enumAttributeString = ''

            if not pm.attributeQuery(spaceAttributeName, node=control, exists=True):
                for targetName in targetNames:
                    enumAttributeString = '{0}:{1}'.format(enumAttributeString, targetName)

                pm.addAttr(control, longName=spaceAttributeName, at='enum', en=enumAttributeString)
            else:
                existingEnums = pm.attributeQuery(spaceAttributeName, node=control, listEnum=True)

                for targetName in targetNames:
                    if targetName not in existingEnums[0]:
                        existingEnums[0] = '{0}:{1}'.format(existingEnums[0], targetName)

                pm.addAttr('{0}.{1}'.format(control, spaceAttributeName),
                             edit=True,
                             enumName=existingEnums)

            pm.setAttr('{0}.{1}'.format(control, spaceAttributeName), keyable=keyable)
            pm.setAttr('{0}.{1}'.format(control, spaceAttributeName), default)

        if translate and rotate:
            constraintName = '{0}_space_PAC'.format(destination)

            if pm.objExists(constraintName):
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      edit=True,
                                                      maintainOffset=maintainOffset)
            else:
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      name=constraintName,
                                                      maintainOffset=maintainOffset)

        if translate and not rotate:
            constraintName = '{0}_spaceTranslate_PAC'.format(destination)

            if pm.objExists(constraintName):
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      edit=True,
                                                      skipRotate=('x', 'y', 'z'),
                                                      maintainOffset=maintainOffset)
            else:
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      name=constraintName,
                                                      skipRotate=('x', 'y', 'z'),
                                                      maintainOffset=maintainOffset)

        if rotate and not translate:
            constraintName = '{0}_spaceRotate_PAC'.format(destination)

            if pm.objExists(constraintName):
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      edit=True,
                                                      skipTranslate=('x', 'y', 'z'),
                                                      maintainOffset=maintainOffset)
            else:
                theConstraint = pm.parentConstraint(targets,
                                                      destination,
                                                      name=constraintName,
                                                      skipTranslate=('x', 'y', 'z'),
                                                      maintainOffset=maintainOffset)

        pm.setAttr('{0}.interpType'.format(theConstraint), 0)

        wals = constraintsLib.get_wals(constraint=theConstraint)

        if asEnum:
            driverIndex = 0

            # sdk connect enum to wals:
            for wal in wals:
                pm.setAttr('{0}.{1}'.format(control, spaceAttributeName), driverIndex)

                # control.setAttr(spaceAttributeName, driverIndex)

                constraintDestination = '{0}.{1}'.format(theConstraint, wal)
                currentDriver = '{0}.{1}'.format(control, spaceAttributeName)

                pm.setDrivenKeyframe(constraintDestination,
                                       currentDriver=currentDriver,
                                       driverValue=driverIndex,
                                       value=1.00)

                driverIndex += 1

                # zero the others:
                remainderIndex = 0

                for w in wals:
                    pm.setAttr('{0}.{1}'.format(control, spaceAttributeName), remainderIndex)

                    # control.setAttr(spaceAttributeName, remainderIndex)

                    constraintDestination = '{0}.{1}'.format(theConstraint, wal)
                    currentDriver = '{0}.{1}'.format(control, spaceAttributeName)

                    if w is not wal:
                        pm.setDrivenKeyframe(constraintDestination,
                                               currentDriver=currentDriver,
                                               driverValue=remainderIndex,
                                               value=0.00)

                    remainderIndex += 1

            # set default:
            pm.setAttr('{0}.{1}'.format(control, spaceAttributeName), default)

            # control.setAttr(spaceAttributeName, default)
        else:
            # as separate float attributes:

            for index, targetName in enumerate(targetNames):
                if not pm.attributeQuery(targetName, node=control, exists=True):
                    # set the default and so that any zeroing script retrieves the proper defaultValue attribute:
                    if index == default:
                        pm.addAttr(control, longName=targetName, at='double', min=0.00, max=1.00, dv=1.00)
                    else:
                        pm.addAttr(control, longName=targetName, at='double', min=0.00, max=1.00, dv=0.00)

                    pm.setAttr('{0}.{1}'.format(control, targetName), edit=True, keyable=True)

                pm.connectAttr('{0}.{1}'.format(control, targetName), '{0}.{1}'.format(theConstraint, wals[index]))

        return theConstraint