#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

import io
import json
import re
import sys

from matplotlib import pyplot as plt

import fillomino as fo

PUZZLE_FILE = 'puzzle.json'


def read_puzzles(file: str = PUZZLE_FILE):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    text_wo_comment = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text)
    jobj = json.loads(text_wo_comment)
    return jobj


def main():
    puzzles = read_puzzles()
    fomatrix = puzzles[1]
    fomg = fo.master_graph(len(fomatrix), len(fomatrix[0]))
    fomg.set_numbers(fomatrix)
    fomg.check_puzzled_out_subgraph()
    fomg.check_other_number_wall()
    fomg.check_same_number_around_zero()
    fomg.draw()
    changed = True
    while changed:
        changed = False
        changed |= fomg.check_leaf_graphs()
        changed |= fomg.check_after_check()
        changed |= fomg.check_disconneced_subgraph()
        changed |= fomg.check_after_check()
        changed |= fomg.check_zero_single_connected_subgrapha()
        changed |= fomg.check_after_check()
        changed |= fomg.check_4n_2c()
        changed |= fomg.check_after_check()
    fomg.draw()
    # fosg = fo.graph(fomg.get_subgraph_wo_puzzled_out_and_wall_edges())
    # fosg.draw()
    plt.show()
    return 0  # 正常終了


if __name__ == '__main__':
    # MSYS2での文字化け対策
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.exit(main())
