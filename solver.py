import collections

from loguru import logger

logger.add("puzzle_solver.log", rotation="50 MB", level="DEBUG")


class Field:
    def __init__(self, size):
        self.check_size(size)
        self._size = size

    @staticmethod
    def check_size(size):
        if type(size) is not int:
            raise TypeError("Field size should be an integer")

        if size < 2:
            raise ValueError("Minimum field size is 2")

    def size(self):
        return self._size

    def get_all_cells(self):
        for x in range(self._size):
            for y in range(self._size):
                yield x, y

    def get_neighbour_cells(self, cell):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_cell = (cell[0] + dx, cell[1] + dy)
            if (0 <= neighbour_cell[0] < self._size) and (
                0 <= neighbour_cell[1] < self._size
            ):
                yield neighbour_cell


class FieldState:
    def __init__(self, field):
        self.field = field
        self._state = collections.defaultdict(lambda: 0)

    def __str__(self):
        result = ""
        for x in range(self.field.size()):
            row = ""
            for y in range(self.field.size()):
                row += str(self._state[(x, y)]) + " "
            result += row + "\n"
        return result

    @staticmethod
    def from_list_to_state(matrix):
        size = len(matrix)
        field = Field(size)
        state = FieldState(field)

        for x in range(size):
            for y in range(size):
                state.set_state((x, y), matrix[x][y])

        return state

    def set_state(self, coords, value):
        if value < 0:
            raise ValueError("Value should be non-negative")

        if type(value) is not int:
            raise TypeError("Value should be an integer")
        self._state[coords] = value

    def get_state(self, coords):
        return self._state[coords]

    def get_involved(self, cell):
        involved = [cell]
        value = self._state[cell]
        not_checked = [cell]

        while not_checked:
            cell = not_checked.pop()

            for neighbour in self.field.get_neighbour_cells(cell):
                if neighbour not in involved and self._state[neighbour] == value:
                    involved.append(neighbour)
                    not_checked.append(neighbour)

        return involved


class CellsGroup:
    def __init__(self, value, initial_cells):
        self.value = value
        self.initial_cells = initial_cells
        self.possible_cells = []
        self.possible_connection_cells = []

    def get_value(self):
        return self.value

    def get_possible_len(self):
        logger.info(f"initial_cells {self.initial_cells}")
        logger.info(f"possible_cells {self.possible_cells}")
        logger.info(f"possible_connection_cells {self.possible_connection_cells}")
        res = (
            len(self.initial_cells)
            + len(self.possible_cells)
            + len(self.possible_connection_cells)
        )
        logger.info(
            f"initial {len(self.initial_cells)} | possible {len(self.possible_cells)} | possible_connection {len(self.possible_connection_cells)} | sum {res}"
        )

        return res

    def get_possible_length(self):
        return (
            len(self.initial_cells)
            + len(self.possible_cells)
            + len(self.possible_connection_cells)
        )

    def add_possible_cell(self, cell):
        if cell not in self.possible_cells:
            self.possible_cells.append(cell)


class PuzzleSolver:
    possible_values: collections.defaultdict
    involved: list = []
    unfilled_groups: dict = {}

    def __init__(self, field_state):
        self.field_state = field_state
        self.state_changed = True

    def solve(self):
        self._refresh_state()
        self._try_fill_empty_cells()

    def _refresh_state(self):
        self._find_unfilled_groups()
        for cell in filter(
            lambda c: self.field_state.get_state(c) != 0 and c in self.unfilled_groups,
            self.field_state.field.get_all_cells(),
        ):
            self._find_possible_values(cell)

        empty_cells = list(
            filter(
                lambda c: self.field_state.get_state(c) == 0,
                self.field_state.field.get_all_cells(),
            )
        )

        involved = set()
        for cell in empty_cells:
            if all(
                self.field_state.get_state(n) != 1
                for n in self.field_state.field.get_neighbour_cells(cell)
            ):
                self._add_possible_value(cell, 1)

            if cell not in involved:
                empty_group = self.field_state.get_involved(cell)
                involved = involved.union(empty_group)
                self._find_additional_values(empty_group)

        self.state_changed = True

    def _find_additional_values(self, empty_group):
        for value in range(2, min(len(empty_group) + 1, 10)):
            involved_for_value = set(empty_group)
            not_possible_cells = set()

            for involved in involved_for_value:
                if any(
                    self.field_state.get_state(n) == value
                    for n in self.field_state.field.get_neighbour_cells(involved)
                ):
                    not_possible_cells.add(involved)
            involved_for_value -= not_possible_cells

            if value <= len(involved_for_value):
                for cell in involved_for_value:
                    self._add_possible_value(cell, value)

    def _find_unfilled_groups(self):
        self.unfilled_groups = {}
        self.involved = []
        self.possible_values = collections.defaultdict(lambda: [])

        for cell in filter(
            lambda x: self.field_state.get_state(x) != 0,
            self.field_state.field.get_all_cells(),
        ):
            if cell not in self.involved:
                initial_cells = self.field_state.get_involved(cell)
                self.involved += initial_cells
                value = self.field_state.get_state(cell)

                if len(initial_cells) < value:
                    new_group = CellsGroup(value, initial_cells)
                    for c in initial_cells:
                        self.unfilled_groups[c] = new_group

                if len(initial_cells) > value:
                    raise ValueError("Wrong group size")

    def _find_possible_values(self, cell):
        next_cells = [(cell, 0)]
        value = self.field_state.get_state(cell)
        previous_cells = []
        group = self.unfilled_groups[cell]

        while next_cells:
            current_cell, current_length = next_cells.pop()
            previous_cells.append(current_cell)

            way_length = current_length + len(group.initial_cells)

            if way_length < value and current_cell != cell:
                self._add_possible_value(current_cell, value)
                group.add_possible_cell(current_cell)

            elif way_length == value:
                self._add_possible_value(current_cell, value)
                group.add_possible_cell(current_cell)
                continue

            free_neighbours = [
                neighbour
                for neighbour in self.field_state.field.get_neighbour_cells(
                    current_cell
                )
                if self.field_state.get_state(neighbour) == 0
                and neighbour not in previous_cells
            ]
            for neighbour in free_neighbours:
                next_cells.append((neighbour, current_length + 1))

    def _add_possible_value(self, cell, value):
        if value not in self.possible_values[cell]:
            invalid_values = set()
            for n in self.field_state.field.get_neighbour_cells(cell):
                n_value = self.field_state.get_state(n)
                if n_value != 0:
                    invalid_values.add(n_value + 1)  # Adding adjacent values
                    invalid_values.add(n_value - 1)
            if value not in invalid_values:
                self.possible_values[cell].append(value)

    def _try_fill_empty_cells(self):

        def backtrack():
            # print(self.field_state)
            if not free_cells:
                return True
            cell = free_cells.pop()
            possible_values[cell] = self.possible_values[cell]
            logger.info(f"CELL | {cell} | {self.field_state.get_state(cell)}")
            logger.info(f"POSSIBLE | {possible_values[cell]}")
            logger.info(f"\n{self.field_state}")
            for value in possible_values[cell]:
                self.field_state.set_state(cell, value)
                try:
                    self._check_group_size()
                    if backtrack():
                        return True
                except ValueError:
                    logger.info(f"check_group_size failed value={value}")
                    pass
                self.field_state.set_state(cell, 0)
            free_cells.append(cell)
            return False

        free_cells = list(
            filter(
                lambda c: self.field_state.get_state(c) == 0,
                self.field_state.field.get_all_cells(),
            )
        )
        possible_values = self.possible_values
        backtrack()

    def _check_group_size(self):
        self._refresh_state()
        if any(
            group.get_possible_length() < group.get_value()
            and not group.possible_connection_cells
            for group in self.unfilled_groups.values()
        ):
            for group in self.unfilled_groups.values():
                logger.info(
                    f"group.get_possible_length() < group.get_value() | {group.get_possible_len()} | {group.get_value()} | {group.get_possible_length() < group.get_value()}"
                )
                logger.info(
                    f"possible_connection_cells | {group.possible_connection_cells}"
                )
            raise ValueError("Wrong group size")


# Example usage:
rows = [[1, 0, 1, 0], [0, 6, 0, 0], [1, 0, 0, 0], [0, 0, 4, 0]]
rows_1 = [
    [2, 0, 0, 0, 0],
    [0, 0, 0, 0, 3],
    [0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0],
    [0, 0, 0, 0, 1],
]

rows_2 = [
    [1, 0, 2, 0, 0],
    [0, 5, 0, 0, 0],
    [1, 0, 0, 0, 4],
    [0, 0, 1, 0, 0],
    [0, 0, 7, 0, 1],
]
rows_3 = [
    [0, 0, 0, 0, 5, 0],
    [5, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 6, 0, 0, 0],
    [4, 0, 0, 0, 0, 0],
    [0, 3, 0, 0, 2, 0],
]
state = FieldState.from_list_to_state(rows_2)
solver = PuzzleSolver(state)
print(solver.field_state)
solver.solve()
print(solver.field_state)
