# sudoku
Tool to solve sudoku puzzles using logic or brute force

## Prerequisites

Should work with any recent version of Python.

## Usage

Start a python shell in the directory where you have installed this code, and type:

    from sudoku import *
    s = Sudoku(initstr)

The initialization string is a comma-separated string representing the value or set of candidates for each cell.
Use two consecutive commas for a blank cell. See the file test_strings.py for some examples.

Your next step should be:

    s.fill_blank_cells()

This will ensure that any blank cells will be filled with the set of candidates, i.e. all possible values for
this cell, eliminating any solved digits in other cells that are seen by this cell (i.e. in the same row, column or box).

Now try out various rules, e.g:

    s.find_hidden_singles()

Use the "kitchen sink" method to try all known rules.

    s.kitchen_sink()

This method starts with simple rules, and if they don't help, it tries more
advanced rules, reverting to the simplest rule when progress is made. If all else fails, it uses brute force.

    s.bruteforce()

This method tries all possible solutions, rolling back if an error is encountered.

The complete list of rules is:

* find_hidden_singles
* find_naked_pairs
* find_hidden_pairs
* find_naked_triples
* find_hidden_triples
* find_naked_quads
* find_hidden_quads
* blr (Box-line reduction)
* pointing
* xwing
* swordfish_jellyfish
* lformation
* deadly_pattern
* xy_wing
* xyz_wing
* bruteforce

Each method will print out debugging information on cells solved or candidates eliminated. For example:

    BLR: digit 7 in row E only occurs in box 4

When the puzzle is solved, you will see the output:

    Puzzle solved!

## Developer Notes

The board is represented by the `grid` attribute, which is a 9-element list (one for each row: 0 -> Row A,
1 -> Row B etc.) of 9-element lists (one for each cell in the row). A cell value is either an  integer if
the cell has been solved, or a set of integers representing the possible candidates for that cell.

To add a logical rule to the above list, it must obey the following convention:

* It takes no arguments apart from the implicit `self` argument.
* It does not solve any cells, i.e. replace a set with an integer as a cell value. This should only happen
  in the method `fill_naked_singles` to ensure that `bruteforce` and `kitchen_sink` work correctly.
* It must be decorated with `@solver(N)` where `N` is an integer representing the rank of the rule.
  A rule with a higher rank is considered more advanced. The `kitchen_sink` method tries rules in increasing
  rank order. The `bruteforce` rule must always have the highest rank so that it is tried last in `kitchen_sink`
  when all other rules have failed to make progress.
* It must call `fill_naked_singles` as the last step before exiting.