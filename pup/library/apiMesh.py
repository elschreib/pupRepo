import maya.api.OpenMaya as OpenMaya
import numpy as np
import maya.cmds as cmds
import re

from scipy.sparse import csc_matrix, csr_matrix
from scipy.spatial import Delaunay

WORLD_SPACE = OpenMaya.MSpace.kWorld
OBJECT_SPACE = OpenMaya.MSpace.kObject


class Mesh(OpenMaya.MFnMesh):

    def __init__(self, obj, extend_to_shape=True):
        """

        Mesh utils class

        :param obj: maya object to get mesh data for
        :type obj: str or OpenMaya.MDagPath or OpenMaya.MFnMesh
        """
        if isinstance(obj, str):
            self._obj = obj

            self.dag = self.dag(extend_to_shape=extend_to_shape)

            super(Mesh, self).__init__(self.dag)
        else:
            super(Mesh, self).__init__(obj)

        # cached version of tri data
        self._tris = None
        self._triangle_verts = None
        self._tri_edge_matrix = None
        self._tri_edge_vectors = None
        self._num_triangles = None
        self._tri_normals = None
        self._tri_edge_normals = None
        self._tri_points = None
        self._tri_centers = None

        # other cached data
        self._edge_vert_list = None
        self._edge_con_matrix = None
        self._vert_con_matrix = None
        self._vert_uv_list = None

        # delaunay trianglulation of UVs
        self._uv_dl_tri = None

        self._points = None
        self._normals = None

        self._poly_it = OpenMaya.MItMeshPolygon(self.dag)
        self._edge_it = OpenMaya.MItMeshEdge(self.dag)
        self._vert_it = OpenMaya.MItMeshVertex(self.dag)

    def clear_cache(self):
        """

        Clear the currently cached data

        """

        # cached version of tri data
        self._tris = None
        self._triangle_verts = None
        self._tri_edge_matrix = None
        self._tri_edge_vectors = None
        self._num_triangles = None
        self._tri_normals = None
        self._tri_edge_normals = None
        self._tri_points = None
        self._tri_centers = None

        # other cached data
        self._edge_vert_list = None
        self._edge_con_matrix = None
        self._vert_con_matrix = None

        self._points = None
        self._normals = None

    def dag(self, extend_to_shape=False):
        """

        Get the dag path for the specified object

        :return: dag path
        :rtype: OpenMaya.MDagPath
        """

        # init the iterators

        sel = OpenMaya.MSelectionList()

        sel.add(self._obj)

        dag = sel.getDagPath(0)

        if not extend_to_shape:
            return dag
        else:
            dag.extendToShape()
            return dag

    def mesh_fn(self):
        """

        Get the MFnMesh for the specified object

        :return: MFnMesh node
        :rtype: OpenMaya.MFnMesh

        """

        return OpenMaya.MFnMesh(self.dag)

    def set_points(self, points):
        """

        Assign the given points to the given mesh

        :param points: points to be assigned
        :type points: np.array

        """

        self.setPoints(OpenMaya.MPointArray(points.tolist()), OpenMaya.MSpace.kWorld)

    def points(self, space=OBJECT_SPACE):
        """

        Get the current points of the mesh, defaults to local space to figure out mesh orientation

        :param space: get world space positions
        :param space: OpenMaya.MSpace
        :return: list of points
        :rtype: numpy.ndarray
        """

        self._points = np.delete(np.array(self.getPoints(space)), 3, axis=1)
        return self._points

    def normals(self, angle_weighted=True, space=OBJECT_SPACE):
        """

        Get the vertex normals

        :param angle_weighted: use angle weighted
        :type angle_weighted: bool
        :param space: OpenMaya.MSpace
        :return: vertex normals
        :rtype: numpy.ndarray
        """

        self._normals = np.array(self.getVertexNormals(angle_weighted, space=space))

        return self._normals

    def bounding_box(self):
        """

        Get the bounding box as an numpy array

        :return: bounding box
        :rtype: numpy.ndarray
        """

        try:
            _m_bounding_box = self.boundingBox

            return np.array(list(_m_bounding_box.min) + list(_m_bounding_box.max))

        except RuntimeError:  # if a dag object is not passed we can't use boundingbox

            col_max = np.amax(self._points, axis=0)
            col_min = np.amin(self._points, axis=0)

            return np.array(col_min.tolist() + [0] + col_max.tolist() + [0])

    # should be memoised really
    def get_vert_uvs(self, uv_set=None):
        """

        Get the shared UVs for each vert on this mesh

        :rtype: list[tuple(float, float)]
        """

        if self._vert_uv_list is None:
            self._vert_it.reset()

            self._vert_uv_list = []

            while not self._vert_it.isDone():
                u, v = self._vert_it.getUV(uvSet=uv_set)

                self._vert_uv_list.append((u, v))

                self._vert_it.next()

        return self._vert_uv_list

    def min_u(self, uv_set=None):
        """

        Get the min U from the uv set

        :param uv_set: set to test
        :return: min u
        :rtype: float
        """

        uvs = self.get_vert_uvs(uv_set=uv_set)

        return np.amin(np.array(uvs), axis=0)[0]

    def max_u(self, uv_set=None):
        """

        Get the max U from the uv set

        :param uv_set: set to test
        :return: min u
        :rtype: float
        """

        uvs = self.get_vert_uvs(uv_set=uv_set)

        return np.amax(np.array(uvs), axis=0)[0]

    def min_v(self, uv_set=None):
        """

        Get the min V from the uv set

        :param uv_set: set to test
        :return: min u
        :rtype: float
        """

        uvs = self.get_vert_uvs(uv_set=uv_set)

        return np.amin(np.array(uvs), axis=0)[1]

    def max_v(self, uv_set=None):
        """

        Get the max V from the uv set

        :param uv_set: set to test
        :return: min u
        :rtype: float
        """

        uvs = self.get_vert_uvs(uv_set=uv_set)

        return np.amax(np.array(uvs), axis=0)[1]

    def uv_triangulation(self, uv_set=None):
        """

        get the delaunay triangulation for the given uv_set

        :param uv_set: uv set to triangulate
        :return: Delaunay triangulation
        :rtype: Delaunay
        """

        if self._uv_dl_tri is None:
            uvs = self.get_vert_uvs(uv_set=uv_set)

            self._uv_dl_tri = Delaunay(uvs, qhull_options="QJ")

        return self._uv_dl_tri

    def get_closest_at_uv(self, u, v, uv_set=None):
        """

        Get closest data at UV,

        :param u: u co-ord
        :param v: v co-ord
        :param uv_set: uv set to check
        :return: point, tris, barycentric coords
        :rtype: dict
        """

        # get the current uv triangulation

        tri = self.uv_triangulation(uv_set=uv_set)

        # find the tri that the uv is in
        simplex = tri.find_simplex((u, v))

        if simplex > -1:
            containing_verts = tri.simplices[simplex]

            # get the bary co-ords
            b = tri.transform[simplex, :2].dot(np.transpose([(u, v)] - tri.transform[simplex, 2]))
            barry_coord = np.c_[np.transpose(b), 1 - b.sum(axis=0)]

            # get the latest points
            points = self.points(space=OpenMaya.MSpace.kWorld)

            v_a = points[containing_verts[0]] * barry_coord[0][0]
            v_b = points[containing_verts[1]] * barry_coord[0][1]
            v_c = points[containing_verts[2]] * barry_coord[0][2]

            out_point = v_a + v_b + v_c

            return {"point": out_point, "tri_ids": containing_verts, "bary": barry_coord[0]}

        return None

    def get_uv_udim(self, uv_set=None):
        """

        Get the uv udim for the current set

        :param uv_set: uv set to test
        :return: u_udim, v_udim
        """

        uvs = np.array(self.get_vert_uvs(uv_set=uv_set))

        min_ = np.amin(uvs, axis=0)
        max_ = np.amax(uvs, axis=0)

        if int(min_[0]) == int(max_[0]) and int(max_[1]) == int(max_[1]):
            return int(min_[0]), int(min_[1])

        else:
            return None

    def point_on_mesh(self, points, uv_set=None):
        """

        Get all the information about the point on mesh closest to the given point

        :param points: points to test
        :param uv_set: map to use
        :return: closest data
        :rtype: list[(OpenMaya.MPointOnMesh, float, float)]
        """

        m_intersect = OpenMaya.MMeshIntersector()
        m_intersect.create(self.object())

        if not isinstance(points, list):
            points = [points]

        out_data = []

        for point in points:
            pos = OpenMaya.MPoint(point)
            point_info = m_intersect.getClosestPoint(pos)

            b_u, b_v = point_info.barycentricCoords
            b_w = 1.0 - (b_u + b_v)

            self._poly_it.setIndex(point_info.face)

            _, tri_verts = self._poly_it.getTriangle(point_info.triangle)

            final_u = 0
            final_v = 0

            for vert, bary in zip(tri_verts, [b_u, b_v, b_w]):
                self._vert_it.setIndex(vert)

                u_vals, v_vals, _ = self._vert_it.getUVs(uv_set=uv_set)

                final_u += u_vals[0] * bary
                final_v += v_vals[0] * bary

            out_data.append((point_info, final_u, final_v))

        return out_data

    def triangles(self):
        """

        Get the triangles for this mesh

        :return: number of triangles per face, triangle ids
        :rtype: list[int], list[int]
        """

        n_counts, tris_ = self.getTriangles()

        self._tris = tris_

        self._num_triangles = sum(n_counts)

        return n_counts, tris_

    def triangle_verts(self):
        """

        Get the triangles arranged as a n_tris x 3 matrix

        :return: triangle verts

        """

        if self._triangle_verts is None:
            # make sure we have the tris data
            if self._tris is None:
                self.triangles()

            self._triangle_verts = np.array(self._tris).reshape(-1, 3)

        return self._triangle_verts

    def triangle_points(self):
        """

        Get the points of each triangle, as described by the points from get_points

        :return: triangle point list
        :type: numpy.ndarray
        """

        if self._tri_points is None:
            if self._points is None:
                raise RuntimeError("Please run .points() first")

            if self._tris is None:
                self.triangles()

            self._tri_points = self._points[self._tris]

        return self._tri_points

    def triangle_centers(self):
        """

        Get the center point of each triangle

        :return: triangle centers
        :rtype: numpy.ndarray
        """

        if self._tri_centers is None:
            self.triangle_points()

            self._tri_centers = np.mean(self._tri_points.reshape(-1, 3, 3), axis=1)

        return self._tri_centers

    def triangle_edge_vectors(self, mode=0):
        """

        Get the triangle edge vectors

        :return: edge vectors for each triangle
        :rtype: numpy.ndarray
        """

        if self._tri_points is None:
            self.triangle_points()

        self._tri_edge_vectors = self._tri_points - self._tri_points.reshape(-1, 3, 3)[:, [1, 2, 0]].reshape(-1, 3)

        return self._tri_edge_vectors

    def triangle_edge_lengths(self):
        """

        Get the triangle edge lengths

        :return: triangle edge lengths
        :rtype: numpy.ndarray
        """

        if self._tri_edge_vectors is None:
            self.triangle_edge_vectors()

        return np.linalg.norm(self._tri_edge_vectors, axis=1)

    def triangle_normals(self):
        """

        Get the triangle normals

        :return: triangle normals
        :rtype: numpy.ndarray
        """

        if self._tri_normals is None:

            if self._tri_edge_vectors is None:
                self.triangle_edge_vectors()

            self._tri_normals = np.cross(self._tri_edge_vectors[::3], self._tri_edge_vectors[1::3])
            self._tri_normals /= np.apply_along_axis(np.linalg.norm, 1, self._tri_normals)[:, np.newaxis]

            return self._tri_normals

        else:
            return self._tri_normals

    def triangle_edge_normals(self):
        """

        Get the normal described by the triangle edges and the triangle normal

        :return: triangle edge normals
        :rtype: numpy.ndarray
        """

        if self._tri_edge_normals is None:
            edge_normals = np.cross(self.triangle_normals().repeat(3, axis=0), self.triangle_edge_vectors())
            self._tri_edge_normals = edge_normals / np.apply_along_axis(np.linalg.norm, 1, edge_normals)[:, np.newaxis]

        return self._tri_edge_normals

    def get_neighbour_verts(self, vert_ids):
        """

        Get the neighbour verts of verts

        :param vert_ids: verts to start with
        :type vert_ids: list[int]
        :return: list of neighbour ids
        :rtype: list[int]
        """

        neighbour_vids = []

        for vert in vert_ids:
            self._vert_it.setIndex(vert)

            neighbour_vids.extend(self._vert_it.getConnectedVertices() or [])

        return list(set(neighbour_vids) - set(vert_ids))

    def edge_vert_list(self):
        """

        Get a list of the vert ids for each edge

        :return: numpy.ndarray
        """

        if self._edge_vert_list is None:

            edge_verts = []

            while not self._edge_it.isDone():
                edge_verts.append([self._edge_it.vertexId(0), self._edge_it.vertexId(1)])

                self._edge_it.next()

            self._edge_vert_list = np.array(edge_verts)

        return self._edge_vert_list

    def edge_connectivity_matrix(self):
        """

        Get the edge vert connectivity matrix for this mesh

        :return: numpy.matrix
        """

        if self._edge_con_matrix is None:
            edge_vert_list = self.edge_vert_list()

            row = edge_vert_list.flatten()
            col = np.flipud(row)
            data = [1] * self.num_edges + [-1] * self.num_edges

            self._edge_con_matrix = csc_matrix((data, (row, col)), shape=(self.num_edges, self.num_edges))

            return self._edge_con_matrix
        else:
            return self._edge_con_matrix

    def vert_connectivity_matrix(self):
        """

        get the vert connectivity matrix

        :return: numpy.matrix
        """

        row = []
        col = []
        data = []

        if self._vert_con_matrix is None:
            while not self._vert_it.isDone():

                for vid in self._vert_it.getConnectedVertices():
                    row.append(self._vert_it.index())
                    col.append(vid)
                    data.append(1)

                self._vert_it.next()

            self._vert_con_matrix = csc_matrix((data, (row, col)), shape=(self.num_verts, self.num_verts))

        return self._vert_con_matrix

    @property
    def num_edges(self):
        """

        get the number of edges

        :return: number of edges
        :rtype: int
        """

        return self.numEdges

    @property
    def num_verts(self):
        """

        get the number of edges

        :return: number of edges
        :rtype: int
        """

        return self.numVertices

    @property
    def num_triangles(self):
        """

        Get the number of triangles

        :return: number of triangles
        :rtype: int
        """

        if not self._num_triangles:
            self.triangles()

        return self._num_triangles

    def select_verts(self, vert_ids, **kwargs):
        """

        Select the given verts, and pass kwargs to cmds.select

        :param vert_ids: ids to select
        :param kwargs: kwargs to pass to cmds.select

        """

        comps = ["{}.vtx[{}]".format(self.fullPathName(), vid) for vid in vert_ids]

        cmds.select(comps, **kwargs)

    def select_faces(self, face_ids, **kwargs):
        """

        Select the given faces, and pass kwargs to cmds.select

        :param face_ids: ids to select
        :param kwargs: kwargs to pass to cmds.select

        """

        comps = ["{}.f[{}]".format(self.fullPathName(), fid) for fid in face_ids]

        cmds.select(comps, **kwargs)

    def select_edges(self, edge_ids, **kwargs):
        """

        Select the given edges, and pass kwargs to cmds.select

        :param edge_ids: ids to select
        :param kwargs: kwargs to pass to cmds.select

        """

        comps = ["{}.e[{}]".format(self.fullPathName(), eid) for eid in edge_ids]

        cmds.select(comps, **kwargs)

    def march_vert_array(self, start_vert_ids):
        """

        Build an array of verts that "march" down the mesh from start_vert_ids

        :param start_vert_ids: verts to start from
        :type start_vert_ids: list[int]
        :return: list[list[int]]
        """

        found_verts = list(start_vert_ids)

        march_array = [list(start_vert_ids)]

        while len(found_verts) < self.num_verts:
            these_verts = self.get_neighbour_verts(march_array[-1])

            next_verts = [vert for vert in these_verts if vert not in found_verts]

            march_array.append(next_verts)

            found_verts += these_verts
            found_verts = list(set(found_verts))

        return march_array


def ids_from_selection():
    """

    Get the ids of the current selection

    :return: component type, list of ids
    :rtype: str, list[int]
    """

    ids = [re.match(r'(\D*)\[(\d*)', sel.split('.')[-1]).groups() for sel in cmds.ls(sl=True, fl=True)]

    comp_type = ids[0][0]

    return comp_type, [int(x[1]) for x in ids]