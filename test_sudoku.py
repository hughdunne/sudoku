import pytest
from sudoku import *
from test_strings import *


def test_all_cells():
    grid = [[None for _ in range(4)] for _ in range(3)]
    allcells = list(all_cells(grid))
    assert len(allcells) == 12
    assert allcells[-1] == (2, 3, None)


def test_box_containing():
    assert box_containing(0, 0) == {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)}
    assert box_containing(0, 3) == {(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)}
    assert box_containing(0, 6) == {(0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)}
    assert box_containing(3, 0) == box_containing(4, 0)
    assert box_containing(3, 0) == box_containing(3, 2)


def test_box_no_containing():
    assert box_no_containing(0, 0) == 0
    assert box_no_containing(1, 3) == 1
    assert box_no_containing(2, 6) == 2
    assert box_no_containing(1, 0) == 0
    assert box_no_containing(3, 1) == 3


def test_seen_by():
    assert seen_by(0, 0) == {(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
                             (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0),
                             (1, 1), (1, 2), (2, 1), (2, 2)}


def test_in_box():
    assert in_box(0) == [0, 1, 2]
    assert in_box(1) == [0, 1, 2]
    assert in_box(2) == [0, 1, 2]
    assert in_box(3) == [3, 4, 5]
    assert in_box(4) == [3, 4, 5]
    assert in_box(5) == [3, 4, 5]
    assert in_box(6) == [6, 7, 8]
    assert in_box(7) == [6, 7, 8]
    assert in_box(8) == [6, 7, 8]


def test_outside_box():
    assert outside_box(0) == [3, 4, 5, 6, 7, 8]
    assert outside_box(1) == [3, 4, 5, 6, 7, 8]
    assert outside_box(2) == [3, 4, 5, 6, 7, 8]
    assert outside_box(3) == [0, 1, 2, 6, 7, 8]
    assert outside_box(4) == [0, 1, 2, 6, 7, 8]
    assert outside_box(5) == [0, 1, 2, 6, 7, 8]
    assert outside_box(6) == [0, 1, 2, 3, 4, 5]
    assert outside_box(7) == [0, 1, 2, 3, 4, 5]
    assert outside_box(8) == [0, 1, 2, 3, 4, 5]


def test_cellname():
    assert cellname(0, 0) == 'A1'
    assert cellname(8, 8) == 'I9'


def test_blockname():
    assert blockname(0) == 'Row A'
    assert blockname(8) == 'Row I'
    assert blockname(9) == 'Col 1'
    assert blockname(17) == 'Col 9'
    assert blockname(18) == 'Box 1'
    assert blockname(26) == 'Box 9'


def test_init():
    s = Sudoku(TESTSTR1)
    s.fill_blank_cells()
    assert s.grid[0][0] == 3
    assert s.grid[0][4] == {2, 6, 7}

    with pytest.raises(ValueError) as e:
        Sudoku(TESTSTR1 + ',4')
    assert str(e.value) == "Check the initialization string"
    with pytest.raises(ValueError) as e:
        Sudoku('3' + TESTSTR1)
    assert str(e.value) == "Bad value 33 in cell A1"
    with pytest.raises(ValueError) as e:
        Sudoku('0' + TESTSTR2)
    assert str(e.value) == "Bad value 0 in cell A1"


def test_save():
    s = Sudoku(TESTSTR1)
    assert s.save() == TESTSTR1


def test_box():
    s = Sudoku(TESTSTR3)
    assert s.box(5) == [
        (3, 6, 5), (3, 7, 1), (3, 8, {4, 6, 7}),
        (4, 6, 9), (4, 7, {6, 7}), (4, 8, {6, 7, 8}),
        (5, 6, 2), (5, 7, {4, 7}), (5, 8, 3)
    ]


def test_fill_blank_cells():
    def cell_ok(cell_val) -> bool:
        return isinstance(cell_val, int) or (isinstance(cell_val, set) and len(cell_val) > 0)

    def row_ok(row) -> bool:
        return all(map(cell_ok, row))

    def grid_ok(grid) -> bool:
        return all(map(row_ok, grid))

    s = Sudoku(TESTSTR1)
    assert not grid_ok(s.grid)
    s.fill_blank_cells()
    assert grid_ok(s.grid)

    s = Sudoku(TESTSTR2)
    assert not grid_ok(s.grid)
    s.fill_blank_cells()
    assert grid_ok(s.grid)

    with pytest.raises(ValueError) as e:
        s = Sudoku('1,2,3,4,5,6,7,,9,,,,,,,,8,' + 63 * ',')
        s.fill_blank_cells()
    assert str(e.value) == "No solution for cell A8"


def test_all_blocks():
    s = Sudoku(TESTSTR1)
    s.fill_blank_cells()
    ab = list(s.all_blocks())
    assert all(map(lambda x: len(x) == 9, ab))
    assert len(ab) == 27
    assert ab[0][0] == (0, 0, 3)
    assert ab[1][0] == (1, 0, {4, 8, 9})
    assert ab[8][0] == (8, 0, 2)
    assert ab[9][0] == (0, 0, 3)
    assert ab[10][0] == (0, 1, {1, 7, 8})
    assert ab[26][0] == (6, 6, {1, 2, 5})


def test_fill_naked_singles():
    # 10427
    s = Sudoku(TESTSTR2)
    s.fill_blank_cells()
    s.fill_naked_singles()
    assert s.save() == TESTSTR3


def test_find_hidden_singles():
    s = Sudoku(TESTSTR4)
    s.fill_blank_cells()
    s.fill_naked_singles()
    s.find_hidden_singles()
    assert s.save() == TESTSTR5

    s = Sudoku(BACKTRACK)
    s.fill_blank_cells()
    while not s.solved():
        s.find_hidden_singles()
    assert s.save() == BACKTRACK_A


def test_pointing():
    # 4036
    s = Sudoku(TESTSTR5)
    s.pointing()
    s.pointing()
    assert s.save() == TESTSTR6


def test_find_naked_pairs():
    # 4036
    s = Sudoku(TESTSTR6)
    s.find_naked_pairs()
    assert s.save() == TESTSTR7


def test_find_naked_triples():
    s = Sudoku(TESTSTR15A)
    s.find_naked_triples()
    assert s.save() == TESTSTR15B
    s = Sudoku(NAKED_TRIPLES_BUG)
    s.find_naked_triples()
    assert s.save() == NAKED_TRIPLES_BUG_A


def test_find_naked_quads():
    s = Sudoku(TESTSTR16A)
    s.find_naked_quads()
    assert s.save() == TESTSTR16B
    s = Sudoku(TESTSTR17A)
    s.find_naked_quads()
    assert s.save() == TESTSTR17B


def test_valid():
    s = Sudoku(TESTSTR1)
    assert s.valid()
    s.grid[0][0] = 9
    assert not s.valid()
    s.grid[0][0] = 6
    assert not s.valid()
    s.grid[0][0] = 1
    assert not s.valid()


def test_xwing():
    # Find horizontal X-wing
    s = Sudoku(TESTSTR7)
    s.xwing()
    assert s.save() == TESTSTR8

    s = Sudoku(TESTSTR3700)
    s.xwing()
    s.find_hidden_singles()
    assert s.solved()
    assert s.valid()

    # Find vertical X-wing
    s = Sudoku(TESTSTR8571)
    s.xwing()
    assert s.save() == TESTSTR8571A
    assert s.solved()
    assert s.valid()


def flip_grid(s):
    # Create mirror image of grid
    for row in s.grid:
        row.reverse()


def rotate_grid_clockwise(s):
    # Rotate 90 degrees clockwise
    rotated = [[None for _ in range(GRIDSIZE)] for _ in range(GRIDSIZE)]
    for ii in range(GRIDSIZE):
        for jj in range(GRIDSIZE):
            rotated[jj][GRIDSIZE - 1 - ii] = s.grid[ii][jj]
    s.grid = rotated


def rotate_grid_anticlockwise(s):
    # Undo rotate_grid_clockwise
    rotated = [[None for _ in range(GRIDSIZE)] for _ in range(GRIDSIZE)]
    for ii in range(GRIDSIZE):
        for jj in range(GRIDSIZE):
            rotated[ii][jj] = s.grid[jj][GRIDSIZE - 1 - ii]
    s.grid = rotated


def test_swordfish_jellyfish():
    s = Sudoku(TESTSTR5605A)
    s.swordfish_jellyfish()
    assert s.save() == TESTSTR5605B
    assert s.solved()
    assert s.valid()
    s = Sudoku(TESTSTR18A)
    s.swordfish_jellyfish()
    assert s.save() == TESTSTR18B
    s = Sudoku(TESTSTR18A)
    rotate_grid_clockwise(s)
    s.swordfish_jellyfish()
    rotate_grid_anticlockwise(s)
    assert s.save() == TESTSTR18B


def test_lformation():
    s = Sudoku(TESTSTR8571)
    s.lformation()
    assert s.save() == TESTSTR8571A
    assert s.solved()
    assert s.valid()

    # To test backward L formation, flip the board
    s = Sudoku(TESTSTR8571)
    flip_grid(s)
    s.lformation()
    flip_grid(s)
    assert s.save() == TESTSTR8571A


def test_deadly_pattern():
    # Find all 4 orientations of deadly pattern
    # Cell to be reduced can be any corner of a square of cells
    s = Sudoku(TESTSTR8136)
    s.deadly_pattern()
    assert s.save() == TESTSTR8136A

    s = Sudoku(TESTSTR8136)
    flip_grid(s)
    s.deadly_pattern()
    flip_grid(s)
    assert s.save() == TESTSTR8136A

    s = Sudoku(TESTSTR8136)
    rotate_grid_clockwise(s)
    s.deadly_pattern()
    rotate_grid_anticlockwise(s)
    assert s.save() == TESTSTR8136A

    s = Sudoku(TESTSTR8136)
    flip_grid(s)
    rotate_grid_clockwise(s)
    s.deadly_pattern()
    rotate_grid_anticlockwise(s)
    flip_grid(s)
    assert s.save() == TESTSTR8136A


def test_find_hidden_pairs():
    # Find hidden pair in box
    s = Sudoku(TESTSTR15A)
    s.find_hidden_pairs()
    assert s.save() == TESTSTR15B

    # Find hidden pair in row
    s = Sudoku(TESTSTR16A)
    s.find_hidden_pairs()
    assert s.save() == TESTSTR16B

    # Find hidden pair in column
    s = Sudoku(TESTSTR17A)
    s.find_hidden_pairs()
    assert s.save() == TESTSTR17B


def test_find_hidden_triples():
    s = Sudoku(TESTSTR11)
    s.fill_blank_cells()
    s.find_hidden_triples()
    assert s.grid[0][3] == {2, 6, 8}
    assert s.grid[0][4] == {2, 6, 8}
    assert s.grid[0][6] == {2, 6}


def test_find_hidden_quads():
    s = Sudoku(TESTSTR12)
    s.find_hidden_quads()
    assert s.save() == TESTSTR13


def test_blr():
    s = Sudoku(TESTSTR13)
    s.blr()
    assert s.save() == TESTSTR14


def test_xy_wing():
    s = Sudoku(TESTSTR8136)
    s.xy_wing()
    assert s.save() == TESTSTR8136A

    s = Sudoku(TESTSTR8136)
    rotate_grid_clockwise(s)
    s.xy_wing()
    rotate_grid_anticlockwise(s)
    assert s.save() == TESTSTR8136A

    s = Sudoku(TESTSTR7169A)
    s.xy_wing()
    assert s.save() == TESTSTR7169B

    s = Sudoku(TESTSTR7169A)
    rotate_grid_clockwise(s)
    s.xy_wing()
    rotate_grid_anticlockwise(s)
    assert s.save() == TESTSTR7169B

    s = Sudoku(XY_WING_BUG)
    s.xy_wing()
    assert s.save() == XY_WING_BUG_A


def test_xyz_wing():
    s = Sudoku(TESTSTR3619)
    s.xyz_wing()
    assert s.save() == TESTSTR3619A

    s = Sudoku(TESTSTR3619)
    rotate_grid_clockwise(s)
    s.xyz_wing()
    rotate_grid_anticlockwise(s)
    assert s.save() == TESTSTR3619A


def test_simple_coloring():
    s = Sudoku(COLORING_A)
    s.simple_coloring()
    assert s.save() == COLORING_B
    s = Sudoku(COLORING_C)
    s.simple_coloring()
    assert s.save() == COLORING_D
    s = Sudoku(COLORING_BUG)
    s.simple_coloring()
    assert s.save() == COLORING_BUG_A


def test_bruteforce():
    s = Sudoku(TESTSTR3700)
    s.bruteforce()
    assert s.solved()
    s = Sudoku(TESTSTR8136)
    s.bruteforce()
    assert s.save() == TESTSTR8136A
    s = Sudoku(BACKTRACK_B)
    s.fill_blank_cells()
    s.bruteforce()
    assert s.save() == BACKTRACK_C


@pytest.mark.slow
def test_bruteforce_slow():
    s = Sudoku(BACKTRACK)
    s.fill_blank_cells()
    s.bruteforce()
    assert s.save() == BACKTRACK_A


def test_solved():
    # End-to-end test
    s = Sudoku(TESTSTR4)
    s.fill_blank_cells()
    s.fill_naked_singles()
    s.find_hidden_singles()
    s.pointing()
    s.pointing()
    s.find_naked_pairs()
    s.find_naked_triples()
    s.xwing()
    s.find_hidden_singles()
    s.find_hidden_singles()
    s.find_hidden_singles()
    s.find_hidden_singles()
    assert s.solved()
    assert s.valid()


def test_forced_chains():
    s = Sudoku(EVIL)
    s.fill_blank_cells()
    s.forced_chains()
    assert s.save() == EVIL_B
    s = Sudoku(EVIL_C)
    s.forced_chains()
    assert s.save() == EVIL_D


def test_kitchen_sink():
    s = Sudoku(TESTSTR2975)
    s.kitchen_sink()
    assert s.save() == TESTSTR2975A
    s = Sudoku(EVIL)
    s.kitchen_sink(24)
    assert s.save() == EVIL_A


def test_getitem():
    s = Sudoku(TESTSTR4766A)
    assert s['A2'] == 7
    assert s['B4'] == 8
    assert s['E'] == [{2, 7}, 4, {1, 5}, {2, 7}, 3, 8, {1, 5}, 9, 6]
    assert s[1] == [{4, 5, 9}, {4, 9}, {5, 9}, {3, 6, 9}, {2, 7}, 8, {2, 7}, 1, {4, 6, 9}]
    with pytest.raises(ValueError) as e:
        s['J']  # noqa
    assert str(e.value) == "Invalid index J"
    with pytest.raises(ValueError) as e:
        s[0]  # noqa
    assert str(e.value) == "Invalid index 0"
    with pytest.raises(ValueError) as e:
        s['a10']  # noqa
    assert str(e.value) == "Invalid index a10"
    with pytest.raises(ValueError) as e:
        s['D0']  # noqa
    assert str(e.value) == "Invalid index D0"
