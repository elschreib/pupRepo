import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel



def get_wals(constraint=None, longName=False):
    """
        Description:
            Returns the name of the target weight attributes of a given constraint.

        Args:
            constraint: A single constraint node.
            longName: Returns either just the target names or the full node path.

        Example:
            theNames = get_wals(constraint='L_leg_001_PAC')

        Return:
            A list of either the short or long names of the target attribute names...

            Short names:
                Return the constraint name and the attribute name as an Attribute object:
                ['L_fingerA_01_pac_GRP_parentConstraint1.L_arm_006_JNTW0', ...]

            Long names include the constraint names as a string list:
                ['C_spine_001_CTLW0', 'C_neck_003_CTLW1', ...]

    """

    if constraint:
        if isinstance(constraint, list):
            constraint = constraint[0]

        if constraint and pm.objExists(constraint):
            conType = pm.objectType(constraint)

            # covers all constraint types:
            wals = mel.eval("string $wals[] = `{0} -query -weightAliasList {1}`;".format(conType, constraint))

            if not longName:
                return wals
            else:
                returnList = []

                for wal in wals:
                    returnList.append('{0}.{1}'.format(constraint, wal))

                return returnList

def cluster_nurbs_CVs(surface, UorV="U"):

    """
        Description:
            creates a cluster on a surface per edge, the start and end cluster include
            the extra CVs that get created. eg. ::   :    :    :   :: - cv's

        Args:
            surface (string): your surface
            UorV (string): U or V direction


        Return:
            None.

    """


    # cluster up nurbs
    cls_list = []
    spans = pm.getAttr(surface + ".spans"+UorV.upper())

    degree = pm.getAttr(surface+".degreeUV")

    if degree[0] == 3:
        for itr in range(spans + 1):
            if itr == 0:  # start
                cls = pm.cluster("{0}.cv[0:1][0:3]".format(surface), name="{0}_{1}_CLS".format(surface, itr))
            elif itr == spans:  # end
                cls = pm.cluster("{0}.cv[{1}:{2}][0:3]".format(surface, spans + 1, spans + 2),
                                   name="{0}_{1}_CLS".format(surface, itr))
            else:
                cls = pm.cluster("{0}.cv[{1}][0:3]".format(surface, itr + 1),
                                   name="{0}_{1}_CLS".format(surface, itr))
            cls_list.append(cls[1])
    elif degree[0] == 1:
        for itr in range(spans + 1):
                cls = pm.cluster("{0}.cv[{1}][0:3]".format(surface, itr), name="{0}_{1}_CLS".format(surface, itr))
                cls_list.append(cls[1])

    return cls_list