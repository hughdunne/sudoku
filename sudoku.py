import logging
from string import ascii_uppercase
from collections import Counter, defaultdict

BOXSIZE = 3
GRIDSIZE = BOXSIZE * BOXSIZE
ALL_DIGITS = frozenset(range(1, GRIDSIZE + 1))

logging.basicConfig(level=logging.DEBUG, format='%(lineno)d: %(message)s')


def all_cells(grid):
    for ii, row in enumerate(grid):
        for jj, cell_val in enumerate(row):
            yield ii, jj, cell_val


def all_pairs(base=0):
    # Use base = 0 to get all possible pairs of coordinates
    # Use base = 1 to get all possible pairs of candidates
    for ii in range(base, base + GRIDSIZE):
        for jj in range(ii + 1, base + GRIDSIZE):
            yield {ii, jj}


def all_triples(base=0):
    for pp in all_pairs(base):
        for kk in range(max(pp) + 1, base + GRIDSIZE):
            yield pp.union({kk})


def all_quads(base=0):
    for tt in all_triples(base):
        for ll in range(max(tt) + 1, base + GRIDSIZE):
            yield tt.union({ll})


def box_containing(ii, jj):
    # Return the set of coordinates
    retval = set()
    x_box = (ii // BOXSIZE) * BOXSIZE
    y_box = (jj // BOXSIZE) * BOXSIZE
    for row in range(x_box, x_box + BOXSIZE):
        for col in range(y_box, y_box + BOXSIZE):
            retval.add((row, col))
    return retval


def box_no_containing(ii, jj) -> int:
    # Return the box number
    return BOXSIZE * (ii // BOXSIZE) + (jj // BOXSIZE)


def seen_by(ii, jj):
    retval = set()
    for row in range(GRIDSIZE):
        retval.add((row, jj))
    for col in range(GRIDSIZE):
        retval.add((ii, col))
    retval.update(box_containing(ii, jj))
    retval.remove((ii, jj))
    return retval


def in_box(idx):
    # For a given row or column, return all row or column numbers in the same box.
    box_start = BOXSIZE * (idx // BOXSIZE)
    box_end = box_start + BOXSIZE
    return [*range(box_start, box_end)]


def outside_box(idx):
    # For a given row or column, return all row or column numbers in a different box.
    box_start = BOXSIZE * (idx // BOXSIZE)
    box_end = box_start + BOXSIZE
    return [*range(0, box_start), *range(box_end, GRIDSIZE)]


def cellname(ii, jj) -> str:
    return ascii_uppercase[ii] + str(jj + 1)


def blockname(bb) -> str:
    blocktype = ["Row", "Col", "Box"][bb // GRIDSIZE]
    ii = bb % GRIDSIZE
    if blocktype == "Row":
        ii = ascii_uppercase[ii]
    else:
        ii += 1
    return blocktype + ' ' + str(ii)


class Sudoku:
    def __init__(self, initstr):
        self.grid = []
        self.stack = []
        self.load(initstr)

    def load(self, initstr):
        cells = initstr.strip().replace(' ', '').split(',')
        if len(cells) != GRIDSIZE * GRIDSIZE:
            raise ValueError("Check the initialization string")
        self.grid = []
        offset = 0
        for ii in range(GRIDSIZE):
            self.grid.append(cells[offset:offset + GRIDSIZE])
            offset += GRIDSIZE
        for ii, jj, cell_val in all_cells(self.grid):
            if not (cell_val == '' or
                    (cell_val.isdecimal() and '0' not in cell_val and len(set(cell_val)) == len(cell_val))):
                raise ValueError("Bad value {0} in cell {1}".format(cell_val, cellname(ii, jj)))
            if len(cell_val) == 1:
                self.grid[ii][jj] = int(cell_val)
            else:
                self.grid[ii][jj] = set(map(int, set(cell_val)))

    def save(self) -> str:
        chars = []
        for row in self.grid:
            for cell in row:
                if isinstance(cell, int):
                    chars.append(str(cell))
                else:
                    chars.append(''.join(map(str, sorted(cell))))
        return ','.join(chars)

    def push(self):
        logging.debug("Pushing")
        self.stack.append(self.save())

    def pop(self):
        logging.debug("Popping")
        self.load(self.stack.pop(-1))

    def __getitem__(self, item):
        # Get a row, column or cell value, e.g:
        # self['A'] returns row A
        # self['B3'] returns cell B3
        # self[N] returns column N (1-9)
        if isinstance(item, str):
            slen = len(item)
            if slen == 1 and item in ascii_uppercase and item <= 'I':
                return self.grid[ascii_uppercase.index(item)]
            if slen == 2 and item[0].isalpha() and item[1].isdecimal():
                row = item[0]
                if row <= 'I':
                    row = ascii_uppercase.index(row)
                    col = int(item[1]) - 1
                    if 0 <= col < GRIDSIZE:
                        return self.grid[row][col]
        elif isinstance(item, int) and item in ALL_DIGITS:
            return [self.grid[ii][item - 1] for ii in range(GRIDSIZE)]
        raise ValueError("Invalid index {0}".format(item))

    def box(self, box_no):
        # Box 0: upper left, box 1: upper center etc.
        retval = []
        box_ii, box_jj = box_no // BOXSIZE, box_no % BOXSIZE
        for ii in range(BOXSIZE * box_ii, BOXSIZE * (box_ii + 1)):
            for jj in range(BOXSIZE * box_jj, BOXSIZE * (box_jj + 1)):
                retval.append((ii, jj, self.grid[ii][jj]))
        return retval

    def fill_blank_cells(self):
        for ii, jj, cell_val in all_cells(self.grid):
            if isinstance(cell_val, set) and len(cell_val) == 0:
                cell_val = set(ALL_DIGITS)
                for other_ii, other_jj in seen_by(ii, jj):
                    other_val = self.grid[other_ii][other_jj]
                    if isinstance(other_val, int):
                        cell_val.discard(other_val)
                if len(cell_val) == 0:
                    raise ValueError("No solution for cell {0}".format(cellname(ii, jj)))
                self.grid[ii][jj] = cell_val

    def fill_naked_singles(self):
        # Solving a cell (replacing a candidate singleton set with its value) should only happen here.
        # Also, once the grid has been loaded and blank cells filled, exceptions should only be raised
        # here so that the brute force method works properly.
        reduced = True
        while reduced:
            reduced = False
            for ii, jj, cell_val in all_cells(self.grid):
                if isinstance(cell_val, set) and len(cell_val) == 1:
                    cell_val = max(cell_val)
                    self.grid[ii][jj] = cell_val
                    logging.debug("{0} -> {1}".format(cellname(ii, jj), cell_val))
                    reduced = True
                    for i2, j2 in seen_by(ii, jj):
                        other_val = self.grid[i2][j2]
                        if isinstance(other_val, set):
                            other_val.discard(cell_val)
                            if len(other_val) == 0:
                                raise ValueError("No solution for cell {0}".format(cellname(i2, j2)))
                        elif cell_val == other_val:
                            raise ValueError("Duplicate digit {0} in {1}, {2}".format(
                                cell_val, cellname(ii, jj), cellname(i2, j2)
                            ))
        if self.solved():
            logging.debug("Puzzle solved!")

    def solved(self) -> bool:
        return all(map(lambda x: isinstance(x[2], int), all_cells(self.grid)))

    def valid(self) -> bool:
        for bb, block in enumerate(self.all_blocks()):
            digits = set()
            for _, _, cell_val in block:
                if isinstance(cell_val, int):
                    if cell_val in digits:
                        logging.warning('Duplicate digit {0} in {1}'.format(cell_val, blockname(bb)))
                        return False
                    digits.add(cell_val)
        return True

    def digits_solved(self):
        ctr = [0 for _ in range(GRIDSIZE + 1)]
        for row in self.grid:
            for cell in row:
                if isinstance(cell, int):
                    ctr[cell] += 1
        return ctr

    def all_blocks(self):
        for ii in range(GRIDSIZE):
            yield [(ii, jj, self.grid[ii][jj]) for jj in range(GRIDSIZE)]
        for jj in range(GRIDSIZE):
            yield [(ii, jj, self.grid[ii][jj]) for ii in range(GRIDSIZE)]
        for box_no in range(GRIDSIZE):
            yield self.box(box_no)

    #
    # Solvers
    #

    def find_hidden_singles(self):
        for d in ALL_DIGITS:
            for bb, block in enumerate(self.all_blocks()):
                contained = set()
                for ii, jj, cell_val in block:
                    if cell_val == d:
                        contained = set()
                        break
                    if isinstance(cell_val, set) and d in cell_val:
                        contained.add((ii, jj))
                if len(contained) == 1:
                    ii, jj = max(contained)
                    self.grid[ii][jj] = {d}
                    logging.debug("{0}: {1} -> {{{2}}}".format(blockname(bb), cellname(ii, jj), d))
        self.fill_naked_singles()

    def find_naked_pairs(self):
        for bb, block in enumerate(self.all_blocks()):
            reduced = False
            c = Counter()
            for ii, jj, cell_val in block:
                if isinstance(cell_val, set):
                    c[tuple(cell_val)] += 1
            for k, v in c.items():
                kl = len(k)
                if kl == 2 and v == kl:
                    ks = set(k)
                    for ii, jj, cell_val in block:
                        if isinstance(cell_val, set) and cell_val != ks and not cell_val.isdisjoint(ks):
                            self.grid[ii][jj].difference_update(ks)
                            reduced = True
                    if reduced:
                        logging.debug("Found naked pair {0} in {1}".format(k, blockname(bb)))
        self.fill_naked_singles()

    def find_naked_triples(self):
        for bb, block in enumerate(self.all_blocks()):
            reduced = False
            c = Counter()
            unsolved = 0
            for ii, jj, cell_val in block:
                if isinstance(cell_val, set):
                    unsolved += 1
                    c[tuple(cell_val)] += 1
            if unsolved <= 3:
                continue
            cc = Counter()
            for t in all_triples(1):
                for k, v in c.items():
                    if set(k).issubset(t):
                        cc[tuple(t)] += v
            for key, nr_occurrences in cc.items():
                if nr_occurrences == 3:
                    for ii, jj, cell_val in block:
                        if isinstance(cell_val, set):
                            ks = set(key)
                            if not (cell_val.issubset(ks) or cell_val.isdisjoint(ks)):
                                self.grid[ii][jj].difference_update(ks)
                                reduced = True
                    if reduced:
                        logging.debug("Found triple: {0} in {1}".format(key, blockname(bb)))
        self.fill_naked_singles()

    def find_naked_quads(self):
        for bb, block in enumerate(self.all_blocks()):
            reduced = False
            c = Counter()
            unsolved = 0
            for ii, jj, cell_val in block:
                if isinstance(cell_val, set):
                    unsolved += 1
                    c[tuple(cell_val)] += 1
            if unsolved <= 4:
                continue
            cc = Counter()
            for t in all_quads(1):
                for k, v in c.items():
                    if set(k).issubset(t):
                        cc[tuple(t)] += v
            for key, nr_occurrences in cc.items():
                if nr_occurrences == 4:
                    for ii, jj, cell_val in block:
                        if isinstance(cell_val, set):
                            ks = set(key)
                            if not (cell_val.issubset(ks) or cell_val.isdisjoint(ks)):
                                logging.debug("Remove {0} from {1}".format(ks, cellname(ii, jj)))
                                self.grid[ii][jj].difference_update(ks)
                                reduced = True
                    if reduced:
                        logging.debug("Found quad: {0} in {1}".format(key, blockname(bb)))
        self.fill_naked_singles()

    def find_hidden_pairs(self):
        tuple_len = 2
        for p in all_pairs(1):
            for bb, block in enumerate(self.all_blocks()):
                occurrences = [[] for _ in p]
                for idx, d in enumerate(p):
                    for ii, jj, cell_val in block:
                        if isinstance(cell_val, set) and d in cell_val:
                            occurrences[idx].append((ii, jj))
                if all(map(lambda x: len(x) == tuple_len, occurrences)) and \
                        len(set([tuple(t) for t in occurrences])) == 1:
                    occurrences = occurrences[0]
                    reduced = False
                    for ii, jj in occurrences:
                        if len(self.grid[ii][jj]) > tuple_len:
                            reduced = True
                            self.grid[ii][jj] = set(p)
                    if reduced:
                        logging.debug("Hidden pair {0} in {1}: {2}".format(
                            p, blockname(bb),
                            [*map(lambda tt: cellname(*tt), occurrences)]))
        self.fill_naked_singles()

    def find_hidden_triples(self):
        tuple_len = 3
        for trp in all_triples(1):
            for bb, block in enumerate(self.all_blocks()):
                unsolved = 0
                present = []
                hidden = False
                for ii, jj, cell_val in block:
                    if isinstance(cell_val, set):
                        unsolved += 1
                        if not trp.isdisjoint(cell_val):
                            present.append((ii, jj, cell_val))
                            if not cell_val.issubset(trp):
                                # At least one cell must not be a subset of trp,
                                # to avoid marking naked triple as hidden.
                                hidden = True
                if unsolved <= tuple_len:
                    continue
                all_present = all(map(lambda y: any(map(lambda x: y in x[2], present)), trp))
                if hidden and all_present and len(present) == tuple_len:
                    logging.debug("Hidden triple {0} in {1}".format(trp, blockname(bb)))
                    for ii, jj, cell_val in present:
                        self.grid[ii][jj] = cell_val.intersection(trp)
        self.fill_naked_singles()

    def find_hidden_quads(self):
        tuple_len = 4
        for quad in all_quads(1):
            for bb, block in enumerate(self.all_blocks()):
                unsolved = 0
                present = []
                hidden = False
                for ii, jj, cell_val in block:
                    if isinstance(cell_val, set):
                        unsolved += 1
                        if not quad.isdisjoint(cell_val):
                            present.append((ii, jj, cell_val))
                            if not cell_val.issubset(quad):
                                # At least one cell must not be a subset of quad,
                                # to avoid marking naked quad as hidden.
                                hidden = True
                if unsolved <= tuple_len:
                    continue
                all_present = all(map(lambda y: any(map(lambda x: y in x[2], present)), quad))
                if hidden and all_present and len(present) == tuple_len:
                    logging.debug("Hidden quad {0} in {1}".format(quad, blockname(bb)))
                    for ii, jj, cell_val in present:
                        self.grid[ii][jj] = cell_val.intersection(quad)
        self.fill_naked_singles()

    def blr(self):
        for d in ALL_DIGITS:

            # If all occurrences of d in a row are in the same box
            # delete all other occurrences of d in that box but different row
            for ii in range(GRIDSIZE):
                reduced = False
                box_no = set()
                for jj in range(GRIDSIZE):
                    cell_val = self.grid[ii][jj]
                    if isinstance(cell_val, set) and d in cell_val:
                        box_no.add(box_no_containing(ii, jj))
                if len(box_no) == 1:
                    box_no = max(box_no)
                    for i2, j2, cell_val in self.box(box_no):
                        if i2 != ii:
                            if isinstance(cell_val, set) and d in cell_val:
                                self.grid[i2][j2].remove(d)
                                reduced = True
                    if reduced:
                        logging.debug(("BLR: digit {0} in row {1} only occurs" +
                                       " in box {2}").format(d, ascii_uppercase[ii], box_no + 1))

            # Repeat for each column
            for jj in range(GRIDSIZE):
                reduced = False
                box_no = set()
                for ii in range(GRIDSIZE):
                    cell_val = self.grid[ii][jj]
                    if isinstance(cell_val, set) and d in cell_val:
                        box_no.add(box_no_containing(ii, jj))
                if len(box_no) == 1:
                    box_no = max(box_no)
                    for i2, j2, cell_val in self.box(box_no):
                        if j2 != jj:
                            if isinstance(cell_val, set) and d in cell_val:
                                self.grid[i2][j2].remove(d)
                                reduced = True
                    if reduced:
                        logging.debug(("BLR: digit {0} in column {1} only occurs" +
                                       " in box {2}").format(d, jj + 1, box_no + 1))

        self.fill_naked_singles()

    def pointing(self):
        for d in ALL_DIGITS:

            # If all occurrences of d in a box are in the same row
            # delete all other occurrences of d in that row but different box
            # Same for columns

            for box_no in range(GRIDSIZE):
                msgs = []
                rows = set()
                cols = set()
                for ii, jj, cell_val in self.box(box_no):
                    if isinstance(cell_val, set) and d in cell_val:
                        rows.add(ii)
                        cols.add(jj)
                if len(rows) == 1:
                    ii = max(rows)
                    for jj in range(GRIDSIZE):
                        if box_no_containing(ii, jj) != box_no and isinstance(self.grid[ii][jj], set) and d in \
                                self.grid[ii][jj]:
                            msgs.append("Remove {0} from {1}".format(d, cellname(ii, jj)))
                            self.grid[ii][jj].remove(d)
                    if len(msgs) > 0:
                        logging.debug(("Pointing: digit {0} in box {1} only occurs" +
                                       " in row {2}").format(d, box_no + 1, ascii_uppercase[ii]))
                        for msg in msgs:
                            logging.debug(msg)
                msgs = []
                if len(cols) == 1:
                    jj = max(cols)
                    for ii in range(GRIDSIZE):
                        if box_no_containing(ii, jj) != box_no and isinstance(self.grid[ii][jj], set) and d in \
                                self.grid[ii][jj]:
                            msgs.append("Remove {0} from {1}".format(d, cellname(ii, jj)))
                            self.grid[ii][jj].remove(d)
                    if len(msgs) > 0:
                        logging.debug(("Pointing: digit {0} in box {1} only occurs" +
                                       " in column {2}").format(d, box_no + 1, jj + 1))
                        for msg in msgs:
                            logging.debug(msg)
        self.fill_naked_singles()

    def xwing(self):
        cands = [[[] for _ in range(GRIDSIZE)] for _ in range(GRIDSIZE + 1)]
        for d in ALL_DIGITS:
            reduced = False
            for ii, jj, cell_val in all_cells(self.grid):
                if isinstance(cell_val, set) and d in cell_val:
                    cands[d][ii].append(jj)
            # Invert the list into a dict
            occurrences = defaultdict(list)
            for ii, val in enumerate(cands[d]):
                kt = tuple(val)
                occurrences[kt].append(ii)
            for key, val in occurrences.items():
                if len(key) == 2 and len(val) == 2:
                    for ii in range(GRIDSIZE):
                        if ii != val[0] and ii != val[1]:
                            if isinstance(self.grid[ii][key[0]], set) and d in self.grid[ii][key[0]]:
                                self.grid[ii][key[0]].remove(d)
                                reduced = True
                            if isinstance(self.grid[ii][key[1]], set) and d in self.grid[ii][key[1]]:
                                self.grid[ii][key[1]].remove(d)
                                reduced = True
                    if reduced:
                        nw = cellname(val[0], key[0])
                        ne = cellname(val[0], key[1])
                        sw = cellname(val[1], key[0])
                        se = cellname(val[1], key[1])
                        logging.debug("Found horizontal xwing for {0}: {1}, {2}, {3}, {4}".format(d, nw, ne, sw, se))

        cands = [[[] for _ in range(GRIDSIZE)] for _ in range(GRIDSIZE + 1)]
        for d in ALL_DIGITS:
            reduced = False
            for ii, jj, cell_val in all_cells(self.grid):
                if isinstance(cell_val, set) and d in cell_val:
                    cands[d][jj].append(ii)
            # Invert the list into a dict
            occurrences = defaultdict(list)
            for ii, val in enumerate(cands[d]):
                kt = tuple(val)
                occurrences[kt].append(ii)
            for key, val in occurrences.items():
                if len(key) == 2 and len(val) == 2:
                    for jj in range(GRIDSIZE):
                        if jj != val[0] and jj != val[1]:
                            if isinstance(self.grid[key[0]][jj], set) and d in self.grid[key[0]][jj]:
                                self.grid[key[0]][jj].remove(d)
                                reduced = True
                            if isinstance(self.grid[key[1]][jj], set) and d in self.grid[key[1]][jj]:
                                self.grid[key[1]][jj].remove(d)
                                reduced = True
                    if reduced:
                        nw = cellname(key[0], val[0])
                        ne = cellname(key[0], val[1])
                        sw = cellname(key[1], val[0])
                        se = cellname(key[1], val[1])
                        logging.debug("Found vertical xwing for {0}: {1}, {2}, {3}, {4}".format(d, nw, ne, sw, se))

        self.fill_naked_singles()

    def swordfish_jellyfish(self):
        cands = [{'h': [[] for _ in range(GRIDSIZE)], 'v': [[] for _ in range(GRIDSIZE)]}
                 for _ in range(GRIDSIZE + 1)]
        ctr = self.digits_solved()
        for d in ALL_DIGITS:
            if ctr[d] >= 6:
                continue
            for ii, jj, cell_val in all_cells(self.grid):
                if isinstance(cell_val, set) and d in cell_val:
                    cands[d]['h'][ii].append(jj)
                    cands[d]['v'][jj].append(ii)
            h_occurrences = defaultdict(lambda: {'rows': set(), 'cols': set()})
            for ii, jj, kk in all_triples():
                for i1, val in enumerate(cands[d]['h']):
                    if len(val) > 0 and {ii, jj, kk}.issuperset(val):
                        h_occurrences[(ii, jj, kk)]['rows'].update({i1})
                        h_occurrences[(ii, jj, kk)]['cols'].update(val)
                for ll in range(max(ii, jj, kk) + 1, GRIDSIZE):
                    for i1, val in enumerate(cands[d]['h']):
                        if len(val) > 0 and {ii, jj, kk, ll}.issuperset(val):
                            h_occurrences[(ii, jj, kk, ll)]['rows'].update({i1})
                            h_occurrences[(ii, jj, kk, ll)]['cols'].update(val)

            for key, val in h_occurrences.items():
                if val['cols'] == set(key) and len(val['rows']) == len(key):
                    reduced = False
                    for ii in set(range(GRIDSIZE)).symmetric_difference(val['rows']):
                        for jj in val['cols']:
                            cell_val = self.grid[ii][jj]
                            if isinstance(cell_val, set) and d in cell_val:
                                self.grid[ii][jj].remove(d)
                                reduced = True
                    if reduced:
                        logging.debug("Horizontal swordfish/jellyfish for {0}: {1}: {2}".format(
                            d,
                            ', '.join(sorted(list(map(lambda x: ascii_uppercase[x], val['rows'])))),
                            ', '.join(sorted(list(map(lambda x: str(x + 1), val['cols']))))
                        ))

            v_occurrences = defaultdict(lambda: {'rows': set(), 'cols': set()})
            for ii, jj, kk in all_triples():
                for i1, val in enumerate(cands[d]['v']):
                    if len(val) > 0 and {ii, jj, kk}.issuperset(val):
                        v_occurrences[(ii, jj, kk)]['cols'].update({i1})
                        v_occurrences[(ii, jj, kk)]['rows'].update(val)
                for ll in range(max(ii, jj, kk) + 1, GRIDSIZE):
                    for i1, val in enumerate(cands[d]['v']):
                        if len(val) > 0 and {ii, jj, kk, ll}.issuperset(val):
                            v_occurrences[(ii, jj, kk, ll)]['cols'].update({i1})
                            v_occurrences[(ii, jj, kk, ll)]['rows'].update(val)

            for key, val in v_occurrences.items():
                if val['rows'] == set(key) and len(val['cols']) == len(key):
                    reduced = False
                    for jj in set(range(GRIDSIZE)).symmetric_difference(val['cols']):
                        for ii in val['rows']:
                            cell_val = self.grid[ii][jj]
                            if isinstance(cell_val, set) and d in cell_val:
                                self.grid[ii][jj].remove(d)
                                reduced = True
                    if reduced:
                        logging.debug("Vertical swordfish/jellyfish for {0}: {1}: {2}".format(
                            d,
                            ', '.join(sorted(list(map(lambda x: ascii_uppercase[x], val['rows'])))),
                            ', '.join(sorted(list(map(lambda x: str(x + 1), val['cols']))))
                        ))

        self.fill_naked_singles()

    def lformation(self):
        for ii, row in enumerate(self.grid):
            for jj, cell_val in enumerate(row):
                if isinstance(cell_val, set) and len(cell_val) == 2:
                    for j2 in range(jj + 1, GRIDSIZE):
                        cell_val2 = self.grid[ii][j2]
                        if isinstance(cell_val2, set) and len(cell_val2) == 2:
                            common = cell_val.intersection(cell_val2)
                            if len(common) == 1:
                                search_for = cell_val.symmetric_difference(cell_val2)
                                digit_to_remove = max(cell_val2.symmetric_difference(common))
                                for i2 in [row for row in range(GRIDSIZE) if row != ii]:
                                    cell_val3 = self.grid[i2][jj]
                                    if isinstance(cell_val3, set) and cell_val3 == search_for:
                                        cell_val4 = self.grid[i2][j2]
                                        if isinstance(cell_val4, set) and digit_to_remove in cell_val4:
                                            self.grid[i2][j2].remove(digit_to_remove)
                                            logging.debug("L-formation: {0} {1} {2}".format(
                                                cellname(ii, jj), cellname(ii, j2), cellname(i2, jj)
                                            ))
                                digit_to_remove = max(cell_val.symmetric_difference(common))
                                for i2 in [row for row in range(GRIDSIZE) if row != ii]:
                                    cell_val3 = self.grid[i2][j2]
                                    if isinstance(cell_val3, set) and cell_val3 == search_for:
                                        cell_val4 = self.grid[i2][jj]
                                        if isinstance(cell_val4, set) and digit_to_remove in cell_val4:
                                            self.grid[i2][jj].remove(digit_to_remove)
                                            logging.debug("L-formation: {0} {1} {2}".format(
                                                cellname(ii, jj), cellname(ii, j2), cellname(i2, jj)
                                            ))

        self.fill_naked_singles()

    def deadly_pattern(self):
        pairwise_rows = [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (6, 7), (6, 8), (7, 8)]
        pairwise_cols = [(0, 3), (0, 6), (3, 6), (1, 4), (1, 7), (4, 7), (2, 5), (2, 8), (5, 8)]
        for bb in range(GRIDSIZE):
            box = self.box(bb)
            for pair in pairwise_rows:
                i1, j1, cell_val1, _, j2, cell_val2 = box[pair[0]] + box[pair[1]]
                if isinstance(cell_val1, set) and len(cell_val1) == 2 and cell_val1 == cell_val2:
                    for ii in range(GRIDSIZE):
                        if box_no_containing(ii, j1) != bb:
                            if self.grid[ii][j1] == cell_val1:
                                cell_val3 = self.grid[ii][j2]
                                if isinstance(cell_val3, set) and not cell_val3.isdisjoint(cell_val1):
                                    self.grid[ii][j2].difference_update(cell_val1)
                                    logging.debug("Deadly pattern: {0} {1} {2} {3}".format(
                                        cellname(ii, j1), cellname(ii, j2), cellname(i1, j1), cellname(i1, j2)
                                    ))
                            elif self.grid[ii][j2] == cell_val1:
                                cell_val3 = self.grid[ii][j1]
                                if isinstance(cell_val3, set) and not cell_val3.isdisjoint(cell_val1):
                                    self.grid[ii][j1].difference_update(cell_val1)
                                    logging.debug("Deadly pattern: {0} {1} {2} {3}".format(
                                        cellname(ii, j1), cellname(ii, j2), cellname(i1, j1), cellname(i1, j2)
                                    ))
            for pair in pairwise_cols:
                i1, j1, cell_val1, i2, _, cell_val2 = box[pair[0]] + box[pair[1]]
                if isinstance(cell_val1, set) and len(cell_val1) == 2 and cell_val1 == cell_val2:
                    for jj in range(GRIDSIZE):
                        if box_no_containing(i1, jj) != bb:
                            if self.grid[i1][jj] == cell_val1:
                                cell_val3 = self.grid[i2][jj]
                                if isinstance(cell_val3, set) and not cell_val3.isdisjoint(cell_val1):
                                    self.grid[i2][jj].difference_update(cell_val1)
                                    logging.debug("Deadly pattern: {0} {1} {2} {3}".format(
                                        cellname(i1, j1), cellname(i2, j1), cellname(i1, jj), cellname(i2, jj)
                                    ))
                            elif self.grid[i2][jj] == cell_val1:
                                cell_val3 = self.grid[i1][jj]
                                if isinstance(cell_val3, set) and not cell_val3.isdisjoint(cell_val1):
                                    self.grid[i1][jj].difference_update(cell_val1)
                                    logging.debug("Deadly pattern: {0} {1} {2} {3}".format(
                                        cellname(i1, j1), cellname(i2, j1), cellname(i1, jj), cellname(i2, jj)
                                    ))
        self.fill_naked_singles()

    def xy_wing(self):
        for bb in range(GRIDSIZE):
            cells = self.box(bb)
            unsolved = [cell for cell in cells if isinstance(cell[2], set)]
            for i1, j1, cell_val1 in unsolved:
                if len(cell_val1) == 2:
                    for i2, j2, cell_val2 in unsolved:
                        if len(cell_val2) == 2:
                            common = cell_val1.intersection(cell_val2)
                            if len(common) == 1:
                                search_for = cell_val1.symmetric_difference(cell_val2)
                                digit_to_remove = max(cell_val2.symmetric_difference(common))
                                seenby2 = seen_by(i2, j2)
                                if j1 != j2:
                                    for j3 in outside_box(j1):
                                        cell_val3 = self.grid[i1][j3]
                                        if cell_val3 == search_for:
                                            msgs = []
                                            # Find all cells seen by both (i1,j3) and (i2,j2)
                                            for i4, j4 in seen_by(i1, j3):
                                                if (i4, j4) in seenby2:
                                                    cell_val4 = self.grid[i4][j4]
                                                    if isinstance(cell_val4, set) and digit_to_remove in cell_val4:
                                                        self.grid[i4][j4].remove(digit_to_remove)
                                                        msgs.append("Remove {0} from {1}".format(
                                                            digit_to_remove, cellname(i4, j4)
                                                        ))
                                            if len(msgs) > 0:
                                                msgs.insert(0, "Found XY wing: {0}, {1}, {2}".format(
                                                    cellname(i1, j1), cellname(i2, j2), cellname(i1, j3)
                                                ))
                                                for msg in msgs:
                                                    logging.debug(msg)
                                if i1 != i2:
                                    for i3 in outside_box(i1):
                                        cell_val3 = self.grid[i3][j1]
                                        if cell_val3 == search_for:
                                            msgs = []
                                            # Find all cells seen by both (i3,j1) and (i2,j2)
                                            for i4, j4 in seen_by(i3, j1):
                                                if (i4, j4) in seenby2:
                                                    cell_val4 = self.grid[i4][j4]
                                                    if isinstance(cell_val4, set) and digit_to_remove in cell_val4:
                                                        self.grid[i4][j4].remove(digit_to_remove)
                                                        msgs.append("Remove {0} from {1}".format(
                                                            digit_to_remove, cellname(i4, j4)
                                                        ))
                                            if len(msgs) > 0:
                                                msgs.insert(0, "Found XY wing: {0}, {1}, {2}".format(
                                                    cellname(i1, j1), cellname(i2, j2), cellname(i3, j1)
                                                ))
                                                for msg in msgs:
                                                    logging.debug(msg)
        self.fill_naked_singles()

    def xyz_wing(self):
        for bb in range(GRIDSIZE):
            cells = self.box(bb)
            unsolved = [cell for cell in cells if isinstance(cell[2], set)]
            for i1, j1, t in unsolved:
                if len(t) == 3:
                    for i2, j2, p in unsolved:
                        if len(p) == 2:
                            if p.issubset(t):
                                extra = t.symmetric_difference(p)
                                for d in p:
                                    search_for = extra.union({d})
                                    # Search the row
                                    if i1 != i2:
                                        for j3 in outside_box(j1):
                                            if self.grid[i1][j3] == search_for:
                                                for j4 in in_box(j1):
                                                    if j4 != j1:
                                                        if isinstance(self.grid[i1][j4], set) and \
                                                                d in self.grid[i1][j4]:
                                                            self.grid[i1][j4].remove(d)
                                                            logging.debug("Found xyz wing: {0}, {1}, {2}".format(
                                                                cellname(i1, j1), cellname(i2, j2), cellname(i1, j3)
                                                            ))

                                    # Search the column
                                    if j1 != j2:
                                        for i3 in outside_box(i1):
                                            if self.grid[i3][j1] == search_for:
                                                for i4 in in_box(i1):
                                                    if i4 != i1:
                                                        if isinstance(self.grid[i4][j1], set) and \
                                                                d in self.grid[i4][j1]:
                                                            self.grid[i4][j1].remove(d)
                                                            logging.debug("Found xyz wing: {0}, {1}, {2}".format(
                                                                cellname(i1, j1), cellname(i2, j2), cellname(i3, j1)
                                                            ))
        self.fill_naked_singles()

    def bruteforce(self):
        # Operates using a stack, so we can roll back changes.
        while True:
            finished = True
            for ii, jj, cell_val in all_cells(self.grid):
                if isinstance(cell_val, set):
                    finished = False
                    d = self.grid[ii][jj].pop()
                    self.push()
                    self.grid[ii][jj] = {d}
                    try:
                        self.fill_naked_singles()
                    except ValueError:
                        # Roll back. Wrong digit has already been popped off so try the next digit.
                        while True:
                            self.pop()
                            if self.valid():
                                break
                    break
            if finished:
                break

    def kitchen_sink(self):
        # Try simple rules, then more advanced ones, then brute force.
        solvers = [
            'find_hidden_singles', 'find_naked_pairs', 'find_hidden_pairs', 'find_naked_triples',
            'find_hidden_triples', 'find_naked_quads', 'find_hidden_quads', 'blr', 'pointing',
            'xwing', 'swordfish_jellyfish', 'lformation', 'deadly_pattern', 'xy_wing',
            'xyz_wing', 'bruteforce'
        ]
        idx = 0
        self.fill_blank_cells()
        while not self.solved():
            logging.debug(solvers[idx])
            method = getattr(self, solvers[idx])
            old_state = self.save()
            method()
            if self.save() == old_state:
                # No progress has been made. Try a more advanced method.
                idx += 1
            else:
                idx = 0
