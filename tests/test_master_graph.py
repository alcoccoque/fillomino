#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

import fillomino as fo
import pytest


class Test_master_graph(object):
    def test_default_constructor(self):
        """デフォルトコンストラクタのテスト
        """
        with pytest.raises(AssertionError) as e:
            mg = fo.master_graph()
            assert mg.rows == 0
            assert mg.cols == 0
            assert e.type == AssertionError

    def test_constructor(self):
        m, n = (2, 3)
        mg = fo.master_graph(m, n)
        assert mg.rows == m
        assert mg.cols == n
        assert mg.G.number_of_nodes() == m * n
        assert mg.G.number_of_edges() == (m - 1) * n + (n - 1) * m
