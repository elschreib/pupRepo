def rivit(refPoint, mesh, orient=True, name = "myRvt"):

    if refPoint and mesh:
        loc = pm.spaceLocator()
        pm.delete(pm.parentConstraint(refPoint, loc))

        CPOM = pm.createNode("closestPointOnMesh", name="delete_CPM")
        pm.connectAttr(mesh + ".outMesh", CPOM.inMesh)
        pm.connectAttr(loc.getShape() + ".parentInverseMatrix[0]", CPOM.inputMatrix)

        faceNumber = pm.getAttr(CPOM + ".closestFaceIndex")

        pm.select(mesh+".f[%s]" % faceNumber)

        mel.eval("ConvertSelectionToEdges;selectType -ocm -alc false;selectType -ocm -polymeshEdge true;")


        edges = pm.ls(selection=True)
        print edges
        if len(edges) == 1:
            e1 = int((edges[0].split("[")[1]).split(":")[0])
            e2 = int(((edges[0].split("[")[1]).split(":")[1])[:-1])

        elif len(edges) > 1:
            temp_edge = []
            for edge in edges:
                if ":" in str(edge):
                    temp_edge.append(int(((edge.split("[")[1]).split(":")[1])[:-1]))
                    print "double " + (((edge.split("[")[1]).split(":")[1])[:-1])
                else:
                    temp_edge.append(int((edge.split("[")[1])[:-1]))
                    print "double " + ((edge.split("[")[1])[:-1])

            e1 = temp_edge[0]
            e2 = temp_edge[-1]

        else:
            print "no edges"

        print e1, e2
        pm.delete(CPOM, loc)
    else:

        edges = pm.selected()
        mesh = edges[0].split(".")[0]
        e1 = int((edges[0].split("[")[1])[:-1])
        e2 = int((edges[1].split("[")[1])[:-1])


    print refPoint
    print e1
    print e2

    # nodes
    CFME1 = pm.createNode("curveFromMeshEdge", name=name + "1_CFME")
    pm.setAttr(CFME1.ihi, 1)
    pm.setAttr(CFME1.ei[0], e1)
    CFME2 = pm.createNode("curveFromMeshEdge", name=name + "2_CFME")
    pm.setAttr(CFME2.ihi, 1)
    pm.setAttr(CFME2.ei[0], e2)

    LOFT = pm.createNode("loft", name=name + "LOFT")
    pm.setAttr(LOFT.ic, s=2)
    pm.setAttr(LOFT.u, True)
    pm.setAttr(LOFT.rsn, True)

    POSI = pm.createNode("pointOnSurfaceInfo", name=name + "_POSI")
    pm.setAttr(POSI.turnOnPercentage, 1)
    pm.setAttr(POSI.parameterU, 0.5)
    pm.setAttr(POSI.parameterV, 0.5)

    pm.connectAttr(LOFT.outputSurface, POSI.inputSurface, f=True)
    pm.connectAttr(CFME1.outputCurve, LOFT.ic[0])
    pm.connectAttr(CFME2.outputCurve, LOFT.ic[1])
    pm.connectAttr(mesh + ".worldMesh", CFME1.inputMesh)
    pm.connectAttr(mesh + ".worldMesh", CFME2.inputMesh)

    # ====== rvt

    RVT = pm.createNode("transform", name=name + "_RVT")
    RVTShape = pm.createNode("locator", name=name + "_RVTShape", p=RVT)

    pm.connectAttr(POSI.position, RVT.translate)

    if orient:
        aimCon = pm.createNode("aimConstraint", p=RVT, name=name + "_ACON")
        pm.setAttr(aimCon.tg[0].tw, 1)
        pm.setAttr(aimCon.aimVector, [0, 1, 0], type="double3")
        pm.setAttr(aimCon.upVector, [0, 0, 1], type="double3")
        [pm.setAttr(aimCon + "." + attr, k=False) for attr in ["visibility", "rotate", "translate", "scale"]]

        pm.connectAttr(POSI.n, aimCon.tg[0].tt)
        pm.connectAttr(POSI.tv, aimCon.worldUpVector)


        pm.connectAttr(aimCon.constraintRotateX, RVT.rotateX)
        pm.connectAttr(aimCon.constraintRotateZ, RVT.rotateZ)

    return RVT
