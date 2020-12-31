import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


def lock_and_hide(nodes=None, channels=None, t=False, r=False, s=False, v=True):
    """
    Description:
        Will tag the items in "nodes" with a string attribute. The contents of the attribute - given in "channels" -
        must be valid channel names. Each channel can then be locked and hidden using "lock_and_hide_tagged_channels"
        at a later time - like at the end of the build in one line - or imediately using the "lock" flag set to "True".

        If "channels", "translate", "rotate" and "scale" are left as default, all channels will be tagged and/or locked.

    Args:
        nodes: a list of nodes
        channels: a custom list of the channels to lock. can be the long or short version. will combine with any
        of the other flags set to "True".
        translate: a True/False flag. True = all axis
        rotate: as above
        scale: as above
        visibility: have a guess
        lock: True = immediately lock and hide the tagged channels, False = just tag the node.. good for dev'ing

    Example:
            # scaleX, scaleZ and visiibility only:
            tag_channels_for_lock_and_hide(pm.ls('*_CTL'), channels=['sx', 'scaleZ', 'visibility'])

            # all rotate channels:
            tag_channels_for_lock_and_hide(pm.ls('*_PoleVector_CTL'), rotate=True)

            # tag but dont lock:
            tag_channels_for_lock_and_hide(pm.ls('*_IKH'), channels=['twist', 'roll'], lock=False)

            # all scale and user defined attibutes:
            tag_channels_for_lock_and_hide(nodes=['temp_001_LOC', 'temp_002_LOC'],
                                           channels=['scaleFactor', 'blendValue'],
                                           scale=True,
                                           lock=True)

    Returns:
        None.

    """

    lockTheseChannels = []

    if channels:
        lockTheseChannels.extend(channels)

    if t:
        lockTheseChannels.extend(['translateX', 'translateY', 'translateZ'])

    if r:
        lockTheseChannels.extend(['rotateX', 'rotateY', 'rotateZ'])

    if s:
        lockTheseChannels.extend(['scaleX', 'scaleY', 'scaleZ'])  # , 'visibility'])

    if v:
        lockTheseChannels.extend(['visibility'])

    # if not channels and not t and not r and not s:
    #     lockTheseChannels = ['translateX', 'translateY', 'translateZ',
    #                          'rotateX', 'rotateY', 'rotateZ',
    #                          'scaleX', 'scaleY', 'scaleZ']

    if nodes and lockTheseChannels:
        for node in nodes:
            for lockTheseChannel in lockTheseChannels:
                pm.setAttr(node+"."+lockTheseChannel, lock=True, channelBox=False, keyable=False)

def add_spacer_attribute(control=None, attributeName=None):
    """
        Description:
            Add an empty enum attribute to the given node for adding a space between attibute groups in the channelbox.
            The attribute is non-keyable and locked.

        Args:
            control: the name of the control you want to add the spacer to.
            attributeName: the name of the attribute

        Example:
                add_spacer_attribute(control='L_hand_001_CTL', attributeName='handPoses')

                This will add an enum attribute that looks like this:

                    Hand Poses:------------

                And is locked.

        Return:
            None.
    """

    pm.addAttr(control, longName=attributeName, at='enum', en='------------:')
    pm.setAttr('{0}.{1}'.format(control, attributeName), edit=True, lock=True, channelBox=True, keyable=False)



def reverse_connect(from_attr, to_attr, offset=0):
    """ -LS-
        Description:
            connects two attributes with outgoing connection inverted

        Flags:
            from_attr: node that has out going connection
            to_attr: node that has in coming connection
            offset: offset by a value

        Returns:
            None.

    """


    name = ("_".join(from_attr.split(".")))+"_"+("_".join(to_attr.split(".")))

    revNode = pm.createNode("reverse", name=name+"_RVS")
    pm.connectAttr(from_attr,revNode+".inputX")
    if offset != None:
        add = pm.createNode("addDoubleLinear",name=name+"_ADL")
        pm.connectAttr(revNode+".outputX",add+".input1")
        pm.setAttr(add+".input2", offset)
        pm.connectAttr(add+".output",to_attr,force=True)
    else:
        pm.connectAttr(revNode+".outputX",to_attr,force=True)


def drawing_override(nodes=None, overrideType='reference', control=None):
    """
        Description:
            Enables the overrideEnabled attribute on the given nodes and sets them to the type specified in the
            "overrideType" flag which can then be accessed via the given "control" Can apply to display layers.

        Args:
            nodes: A list of nodes.
            overrideType: The type of display override you want to use as a string. Defaults to "reference" if
            left blank.
            control: if set, will apply an enum attribute to alter the override type

        Example:
            Will set everything with the extension "_PLY" to reference mode making them unselectable:

                drawing_override(nodes=pm.ls(sl='*_PLY'), overrideType='reference')

        Return:
            None.

    """

    # nodes = utilslib.pynode(data=nodes)
    # control = utilslib.pynode(data=control)

    overrideType = overrideType.lower()
    typeDict = {'normal': 0, 'template': 1, 'reference': 2}

    if control and not pm.attributeQuery('drawingOverride', node=control, exists=True):
        pm.addAttr(control, longName='drawingOverride', at='enum', en='normal:template:reference:')
        pm.setAttr('{0}.drawingOverride'.format(control), edit=True, keyable=False, channelBox=True)

    if nodes:
        for node in nodes:
            if pm.objectType(node) == 'displayLayer':
                pm.setAttr('{0}.enabled'.format(node), True)
                pm.setAttr('{0}.displayType'.format(node), typeDict[overrideType])
            else:
                pm.setAttr('{0}.overrideEnabled'.format(node), True)
                pm.setAttr('{0}.overrideDisplayType'.format(node), typeDict[overrideType])

            # connect to attribute:
            if control:
                pm.setAttr('{0}.drawingOverride'.format(control), typeDict[overrideType])

                pm.connectAttr('{0}.drawingOverride'.format(control), '{0}.overrideDisplayType'.format(node))


# ==================== CORE FOR BUILDS
def get_inputs(node):
    """
    returns all *_input attrs on node
    :param node: node to take attr from
    :return:
    """

    attr_dict = {}
    attrs = pm.listAttr(node, cb=True)
    for attr in attrs:
        if attr.startswith("follow"):
            constraint = pm.getAttr(node + "." + attr)
            if attr.split("_")[-1] == "global":
                if constraint:
                    attr_dict[attr.split("_")[-1]] = constraint
            elif constraint:
                attr_dict[attr.split("_")[-1]] = constraint + "_in"
    return attr_dict




    # attr_name = []
    # attr_constraint = []
    # attrs = pm.listAttr(node, cb=True)
    # for attr in attrs:
    #     if attr.startswith("follow"):
    #         constraint = pm.getAttr(node + "." + attr)
    #         if constraint:
    #             attr_name.append(attr.split("_")[-1])
    #             attr_constraint.append(constraint)
    #
    # return attr_name,attr_constraint


def link_secondary(controlA, controlB, shape=True):
    if not "VISIBILITY" in pm.listAttr(controlA):
        add_spacer_attribute(controlA, attributeName="VISIBILITY")
    pm.addAttr(controlA, ln="secondary", at="bool", dv=0)
    pm.setAttr(controlA.secondary, cb=True)

    if shape:
        pm.connectAttr(controlA.secondary, controlB.getShape().visibility)
    else:
        pm.connectAttr(controlA.secondary, controlB.visibility)