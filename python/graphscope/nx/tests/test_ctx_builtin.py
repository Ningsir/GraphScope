import os

import numpy as np
import pandas as pd
import pytest

import graphscope
from graphscope import nx
from graphscope.nx.tests.utils import almost_equal
from graphscope.nx.tests.utils import replace_with_inf


@pytest.mark.usefixtures("graphscope_session")
class TestBuiltInApp:
    @classmethod
    def setup_class(cls):
        cls.grid_edges = [
            (1, 2),
            (1, 5),
            (2, 3),
            (2, 6),
            (3, 4),
            (3, 7),
            (4, 8),
            (5, 6),
            (5, 9),
            (6, 7),
            (6, 10),
            (7, 8),
            (7, 11),
            (8, 12),
            (9, 10),
            (9, 13),
            (10, 11),
            (10, 14),
            (11, 12),
            (11, 15),
            (12, 16),
            (13, 14),
            (14, 15),
            (15, 16),
        ]
        cls.grid = nx.Graph()
        cls.grid.add_edges_from(cls.grid_edges, weight=1)
        cls.grid_ans = {
            1: 0,
            5: 1,
            2: 1,
            9: 2,
            6: 2,
            3: 2,
            13: 3,
            10: 3,
            7: 3,
            4: 3,
            14: 4,
            11: 4,
            8: 4,
            15: 5,
            12: 5,
            16: 6,
        }
        cls.grid_path_ans = {
            3: 7,
            4: 8,
            8: 12,
            12: 16,
            1: 5,
            5: 9,
            9: 13,
            2: 3,
            6: 10,
            10: 14,
            7: 11,
            11: 15,
        }

        data_dir = os.path.expandvars("${GS_TEST_DIR}")
        p2p_file = os.path.expandvars("${GS_TEST_DIR}/dynamic/p2p-31_dynamic.edgelist")
        p2p_sub_file = os.path.expandvars(
            "${GS_TEST_DIR}/dynamic/p2p-31_dynamic_subgraph.edgelist"
        )
        cls.p2p = nx.read_edgelist(
            p2p_file, nodetype=int, data=True, create_using=nx.DiGraph
        )
        cls.p2p_undirected = nx.read_edgelist(
            p2p_file, nodetype=int, data=True, create_using=nx.Graph
        )
        cls.p2p_subgraph = nx.read_edgelist(
            p2p_sub_file, nodetype=int, data=True, create_using=nx.DiGraph
        )
        cls.p2p_subgraph_undirected = nx.read_edgelist(
            p2p_sub_file, nodetype=int, data=True, create_using=nx.Graph
        )
        cls.p2p_length_ans = dict(
            pd.read_csv(
                "{}/p2p-31-sssp".format(data_dir), sep=" ", header=None, prefix=""
            ).values
        )
        cls.p2p_dc_ans = dict(
            pd.read_csv(
                "{}/p2p-31-degree_centrality".format(data_dir),
                sep="\t",
                header=None,
                prefix="",
            ).values
        )
        cls.p2p_ev_ans = dict(
            pd.read_csv(
                "{}/p2p-31-eigenvector".format(data_dir),
                sep="\t",
                header=None,
                prefix="",
            ).values
        )
        cls.p2p_kz_ans = dict(
            pd.read_csv(
                "{}/p2p-31-katz".format(data_dir), sep="\t", header=None, prefix=""
            ).values
        )
        cls.p2p_hits_ans = pd.read_csv(
            "{}/p2p-31-hits-directed".format(data_dir), sep="\t", header=None, prefix=""
        )
        cls.p2p_pagerank_ans = dict(
            pd.read_csv(
                "{}/p2p-31-pagerank_nx".format(data_dir),
                sep="\t",
                header=None,
                prefix="",
            ).values
        )
        cls.p2p_clus_ans = dict(
            pd.read_csv(
                "{}/p2p-31-clustering".format(data_dir), sep=" ", header=None, prefix=""
            ).values
        )
        cls.p2p_triangles_ans = dict(
            pd.read_csv(
                "{}/p2p-31-triangles".format(data_dir), sep=" ", header=None, prefix=""
            ).values
        )
        cls.p2p_kcore_ans = sorted(
            pd.read_csv(
                "{}/p2p-31-kcore".format(data_dir), sep=" ", header=None, prefix=""
            ).values
        )

    def assert_result_almost_equal(self, r1, r2):
        assert len(r1) == len(r2)
        for k in r1.keys():
            assert almost_equal(r1[k], r2[k])

    def test_single_source_dijkstra_path_length(self):
        ret = nx.builtin.single_source_dijkstra_path_length(
            self.grid, 1, weight="weight"
        )
        ans = dict(ret.astype(np.int64).values)
        assert ans == self.grid_ans

        ret = nx.builtin.single_source_dijkstra_path_length(
            self.p2p_undirected, 6, weight="weight"
        )
        ans = dict(ret.values)
        assert replace_with_inf(ans) == self.p2p_length_ans

    def test_subgraph_single_source_dijkstra_path_length(self):
        # test subgraph and edge_subgraph with p2p_subgraph_undirected
        ret = nx.builtin.single_source_dijkstra_path_length(
            self.p2p_subgraph_undirected, 6, weight="weight"
        )
        SG = self.p2p_undirected.subgraph(self.p2p_subgraph_undirected.nodes)
        ret_sg = nx.builtin.single_source_dijkstra_path_length(SG, 6, weight="weight")
        assert dict(ret.values) == dict(ret_sg.values)
        ESG = self.p2p_undirected.edge_subgraph(self.p2p_subgraph_undirected.edges)
        ret_esg = nx.builtin.single_source_dijkstra_path_length(ESG, 6, weight="weight")
        assert dict(ret.values) == dict(ret_esg.values)

        # test subgraph and edge_subgraph with p2p directed
        ret2 = nx.builtin.single_source_dijkstra_path_length(
            self.p2p_subgraph, 6, weight="weight"
        )
        SDG = self.p2p.subgraph(self.p2p_subgraph.nodes)
        ret_sdg = nx.builtin.single_source_dijkstra_path_length(SDG, 6, weight="weight")
        assert dict(ret2.values) == dict(ret_sdg.values)
        ESDG = self.p2p.edge_subgraph(self.p2p_subgraph.edges)
        ret_esdg = nx.builtin.single_source_dijkstra_path_length(
            ESDG, 6, weight="weight"
        )
        assert dict(ret2.values) == dict(ret_esdg.values)

    def test_shortest_path(self):
        ctx1 = nx.builtin.shortest_path(self.grid, source=1, weight="weight")
        ret1 = dict(ctx1.to_numpy("r"))
        assert ret1 == self.grid_path_ans

    def test_has_path(self):
        ctx = nx.builtin.has_path(self.grid, source=1, target=6)
        assert ctx.to_numpy("r", axis=0)[0]
        ctx = nx.builtin.has_path(self.p2p, source=6, target=3728)
        assert not ctx.to_numpy("r", axis=0)[0]
        ctx = nx.builtin.has_path(self.p2p, source=6, target=3723)
        assert ctx.to_numpy("r", axis=0)[0]

    def test_average_shortest_path_length(self):
        ret = nx.builtin.average_shortest_path_length(self.grid, weight="weight")
        assert ret == 2.6666666666666665

    def test_degree_centrality(self):
        ans = dict(nx.builtin.degree_centrality(self.p2p).values)
        self.assert_result_almost_equal(ans, self.p2p_dc_ans)

    def test_eigenvector_centrality(self):
        ans = dict(nx.builtin.eigenvector_centrality(self.p2p, weight="weight").values)
        self.assert_result_almost_equal(ans, self.p2p_ev_ans)

    @pytest.mark.skip(
        reason="FIXME(acezen): p2p katz centrality result need to recheck."
    )
    def test_katz_centrality(self):
        ans = dict(nx.builtin.katz_centrality(self.p2p, weight="default").values)
        self.assert_result_almost_equal(ans, self.p2p_kz_ans)

    def test_hits(self):
        expected_hub = self.p2p_hits_ans[1].to_numpy(dtype=float)
        expected_auth = self.p2p_hits_ans[2].to_numpy(dtype=float)
        df = nx.builtin.hits(self.p2p, tol=0.001).sort_values(by=["node"])
        auth = df["auth"].to_numpy(dtype=float)
        hub = df["hub"].to_numpy(dtype=float)
        np.allclose(auth, expected_auth)
        np.allclose(hub, expected_hub)

    def test_clustering(self):
        ans = dict(nx.builtin.clustering(self.p2p).values)
        self.assert_result_almost_equal(ans, self.p2p_clus_ans)

    def test_triangles(self):
        ans = dict(nx.builtin.triangles(self.p2p_undirected).values)
        self.assert_result_almost_equal(ans, self.p2p_triangles_ans)

    def test_average_clustering(self):
        ret = nx.builtin.average_clustering(self.p2p_undirected)

    def test_weakly_connected_components(self):
        ret = nx.builtin.weakly_connected_components(self.p2p_undirected)

    def test_pagerank(self):
        ans = dict(nx.builtin.pagerank(self.p2p).values)
        self.assert_result_almost_equal(ans, self.p2p_pagerank_ans)

    def test_degree_assortativity_coefficient(self):
        ans = nx.builtin.degree_assortativity_coefficient(self.p2p_undirected)
        assert almost_equal(ans, -0.0925578, places=5)

    def test_average_degree_connectivity(self):
        gt = {
            23: 12.079051383399209,
            36: 12.213541666666666,
            6: 13.41948833709556,
            13: 10.631225667874883,
            15: 11.13222089789432,
            31: 12.525345622119815,
            18: 11.670812603648425,
            22: 12.205342902711324,
            20: 12.039447236180905,
            7: 13.233418367346939,
            3: 13.822278481012658,
            2: 14.043461910390029,
            17: 11.186960563006242,
            8: 13.315128504672897,
            5: 13.480509745127437,
            1: 14.27883608959598,
            4: 13.57874109263658,
            27: 12.93676603432701,
            12: 10.081949352179034,
            11: 9.594664409134323,
            16: 11.09459175084175,
            21: 12.016680118375033,
            19: 11.686204146730462,
            25: 12.745416666666667,
            30: 12.973563218390805,
            42: 10.657738095238095,
            28: 12.34593837535014,
            10: 9.59122965641953,
            14: 10.633949982870845,
            24: 12.37938596491228,
            26: 12.934065934065934,
            33: 10.980392156862745,
            39: 10.663003663003662,
            32: 11.841911764705882,
            9: 12.373635600335852,
            35: 10.806722689075631,
            34: 11.237851662404092,
            45: 10.526984126984127,
            29: 12.315958299919808,
            46: 10.108695652173912,
            37: 10.373464373464374,
            70: 13.642857142857142,
            40: 9.74375,
            41: 11.207317073170731,
            38: 10.493927125506072,
            43: 13.023255813953488,
            44: 10.655844155844155,
            55: 7.472727272727273,
            49: 9.755102040816327,
            95: 9.863157894736842,
            47: 9.063829787234043,
            78: 10.205128205128204,
            62: 9.274193548387096,
            66: 10.378787878787879,
            48: 9.552083333333334,
            51: 9.882352941176471,
        }
        ans = nx.builtin.average_degree_connectivity(self.p2p_undirected)
        assert gt == ans

    def test_all_simple_paths(self):
        ans = nx.builtin.all_simple_paths(self.p2p, 1, 4, cutoff=10)
        assert len(ans) == 1022
        ans = nx.builtin.all_simple_paths(self.p2p_undirected, 1, [4, 6], cutoff=5)
        assert len(ans) == 1675
