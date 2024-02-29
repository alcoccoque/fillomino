import json
import re
from typing import Dict, List, Tuple

from matplotlib import pyplot as plt

from constants import NUMBER, PUZZLE_FILE, WALL
from ui import MasterGraph


def read_puzzles(file: str = PUZZLE_FILE) -> List[List[List[int]]]:
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    text_wo_comment = re.sub(r"/\*[\s\S]*?\*/|//.*", "", text)
    jobj = json.loads(text_wo_comment)
    return jobj


def run() -> None:
    puzzles = read_puzzles()
    matrix = puzzles[0]
    graph = MasterGraph(_rows=len(matrix), _cols=len(matrix[0]))
    graph.set_numbers(matrix)
    graph.draw()
    graph.solve_puzzle()
    # graph.set_numbers(puzzles[1])
    graph.set_walls_for_neighbors()
    graph.draw()
    plt.show()


if __name__ == "__main__":
    run()
