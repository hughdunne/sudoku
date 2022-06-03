# sudoku
Tool to solve sudoku puzzles using logic or brute force

## Prerequisites

Should work with any recent version of Python.

## Usage

Start a python shell in the directory where you have installed this code, and type:

    from sudoku import Sudoku
    s = Sudoku(initstr)

The initialization string is a comma-separated string representing the value or set of candidates for each cell.
Use two consecutive commas for a blank cell. See the file test_strings.py for some examples.

Your next step should be:

    s.fill_blank_cells()

This will ensure that any blank cells will be filled with the set of candidates, i.e. all possible values for this cell,
eliminating any solved digits in other cells that are seen by this cell (i.e. in the same row, column or box).

Now try out various rules, e.g:

    s.find_hidden_singles()

Use the "kitchen sink" method to try all known rules.

    s.kitchen_sink()

This method starts with simple rules, and if they don't help, it tries more
advanced rules, reverting to the simplest rule when progress is made. If all else fails, it uses brute force.

    s.bruteforce()

This method tries all possible solutions, rolling back if an error is encountered.

Note that each rule has a rank, and the higher the rank, the more advanced the rule is considered to be. You can 
suppress advanced rules in `kitchen_sink` by specifying the maximum rank to try. E.g. to suppress the brute force
method, give the command:

    s.kitchen_sink(99)

Since the rank of `bruteforce` is 100, `kitchen_sink` will exit if it cannot solve the puzzle with lower-ranked rules.

The complete list of rules and their ranks is:

| Name                |   Rank | Notes              |
|---------------------|-------:|--------------------|
| find_hidden_singles |      1 |                    |
| find_naked_pairs    |      2 |                    |
| find_naked_triples  |      3 |                    |
| find_naked_quads    |      4 |                    |
| find_hidden_pairs   |      5 |                    |
| find_hidden_triples |      6 |                    |
| find_hidden_quads   |      7 |                    |
| blr                 |      8 | Box-line reduction |
| pointing            |      9 |                    |
| xwing               |     10 |                    |
| swordfish_jellyfish |     11 |                    |
| lformation          |     12 | L-formation        |
| deadly_pattern      |     13 |                    |
| xy_wing             |     14 |                    |
| xyz_wing            |     15 |                    |
| simple_coloring     |     20 |                    |
| bruteforce          |    100 |                    |

Each method will print out debugging information on cells solved or candidates eliminated. For example:

    BLR: digit 7 in row E only occurs in box 4

When the puzzle is solved, you will see the output:

    Puzzle solved!

## Testing

Quick test:

    pytest -m "not slow" test_sudoku.py

This runs all tests except `test_bruteforce_slow` (see below).

Complete test (may take several minutes):

    pytest test_sudoku.py

This runs all tests including `test_bruteforce_slow`, which tests the brute force solver on a puzzle
which was designed to defeat backtracking algorithms.
See this page on [Wikipedia](https://en.wikipedia.org/wiki/Sudoku_solving_algorithms#Backtracking).

## Developer Notes

The board is represented by the `grid` attribute of a Sudoku object. This is a 9-element list (one for each row:
0 &#8594; Row A, 1 &#8594; Row B etc.) of 9-element lists (one for each cell in the row). A cell value is either an 
integer if the cell has been solved, or a set of integers representing the possible candidates for that cell.

To add a logical rule to the above list, it must obey the following convention:

* It should take no arguments apart from the implicit `self` argument.
* It should not solve any cells, i.e. replace a set with an integer as a cell value. Instead, it should
 eliminate candidates, and should call `fill_naked_singles` as the last step before exiting.
* It must be decorated with `@solver(N)` where `N` is an integer representing the rank of the rule.
  A rule with a higher rank is considered more advanced. The `kitchen_sink` method tries rules in increasing
  rank order. The `bruteforce` rule must always have the highest rank so that it is tried last in `kitchen_sink`
  when all other rules have failed to make progress.