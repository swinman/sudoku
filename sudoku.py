#!/usr/bin/python3
"""
Solve a sudoku puzzle

A [row][col] = A[i][j]

A = [[a11 a12 a13],
     [a21 a22 a23],
     [a31 a32 a33]]
"""

import os
import re
import math
import cmath
import random
import itertools
import logging
import argparse
import numpy as np
from matplotlib import pyplot as plt

log = logging.getLogger(__name__)

_BOX_LABELS = [["top left", "top center", "top right"],
        ["middle left", "central", "middle right"],
        ["bottom left", "bottom center", "bottom right"]]


class Board(object):
    def __init__(self, init):
        self.matrix = [list(range(9)) for _ in range(9)]
        def mk_lambda(r, c):
            return lambda val : self.update(r, c, val)
        for row in range(9):
            for col in range(9):
                cell = Cell(row, col)
                #log.debug("Cell {} update is {},{}".format(cell.ndx, row, col))
                self.matrix[row][col] = cell
                cell.set_notification(mk_lambda(row, col))
        for row in range(9):
            for col in range(9):
                cell = self.matrix[row][col]
                init_val = init[row][col]
                if init_val != 0:
                    log.debug("Init of {} = {}".format(cell.ndx, init_val))
                    cell.set(init_val)
        log.info("Initial uncertainty {}".format(self.get_uncertainty()))

    def get_uncertainty(self):
        uncertainty = 0
        for cell in self.yield_cells():
            if cell.solved:
                log.debug("Cell {} is solved".format(cell.ndx))
                continue
            if len(cell.options) == 1:
                v = cell.options[0]
                log.info("Only {} for cell {}, solving".format(v, cell.ndx))
                cell.set(v)
                continue
            uncertainty += len(cell.options)
        if uncertainty == 0:
            uncertainty = self.test_solution()
        return uncertainty

    def test_solution(self):
        """ 0 on success otherwise negative for numbers missing """
        def test(cells):
            errors = 0
            FULL_SET = set(list(range(1, 10)))
            options = set()
            fixed = set()
            for cell in cells:
                options.update(cell.options)
                if cell.solved:
                    if cell.solved in fixed:
                        errors += 1
                    fixed.update([cell.solved])
            if len(options.difference(FULL_SET)):
                errors += 1
            return errors

        rv = 0
        for row in self.yield_rows():
            rv -= test(row)
            for cell in row:
                if len(cell.options) == 0:
                    rv -= 1
        for col in self.yield_cols():
            rv -= test(col)
        for box in self.yield_boxes():
            rv -= test(box)
        if rv == 0:
            log.info("Solution is correct")
        return rv

    def show_known(self, max_options=1):
        lines = []
        row_fmt = "|{}{}{}|{}{}{}|{}{}{}|"
        for row in range(9):
            cells = [self.matrix[row][col] for col in range(9)]
            txt = ['{:^7}'.format(cell.fmt_options(max_options)) for cell in cells]
            lines.append(row_fmt.format(*txt))
            if row % 3 == 0:
                lw = len(lines[-1])
                lines.insert(-1, '-'*lw)
        lines.append('-'*lw)
        print('\n' + '\n'.join(lines))

    def export(self):
        return [[c.solved if c.solved else 0 for c in row] for row in self.matrix]

    def guess(self, row, col, val):
        for cell in self.yield_cells():
            if cell.guessing_mode:
                continue
            cell.set_guessing_mode(True)
        self.update(row, col, val)

    def clear_guesses(self, cheat=True, clear_mistakes=False):
        uncertainty = self.get_uncertainty()
        for cell in self.yield_cells():
            if cheat and uncertainty == 0:
                cell.cheat()
            elif cheat == False:
                cell.clear_cheats()
                cell.clear_mistakes()
            if clear_mistakes:
                cell.clear_mistakes()
            cell.set_guessing_mode(False)

    def update(self, row, col, val):
        """ clear val from row, col and quadrant """
        cell = self.matrix[row][col]
        log.debug("setting {} to {} from {} options".format(cell.ndx, val, cell.options))
        log.debug("Clearing {} from row {}".format(val, row))
        err = False
        for j in range(9):
            if j == col:
                continue
            #log.debug("Clearing {} from {}, {}".format(val, row, j))
            try:
                ocell = self.matrix[row][j]
                ocell.remove(val)
            except ValueError as exception:
                msg = "Error removing {} from {}".format(val, ocell.ndx)
                if ocell.guessing_mode:
                    log.debug(msg)
                else:
                    log.error(msg)
                err = True

        log.debug("Clearing {} from col {}".format(val, col))
        for i in range(9):
            if i == row:
                continue
            #log.debug("Clearing {} from {}, {}".format(val, i, col))
            try:
                ocell = self.matrix[i][col]
                ocell.remove(val)
            except ValueError as exception:
                msg = "Error removing {} from {}".format(val, ocell.ndx)
                if ocell.guessing_mode:
                    log.debug(msg)
                else:
                    log.error(msg)
                err = True

        box_row, box_col = row // 3, col // 3
        log.debug("Clearing {} from {} box".format(val, _BOX_LABELS[box_row][box_col]))
        for i in range(3*box_row, 3*box_row + 3):
            for j in range(3*box_col, 3*box_col + 3):
                if i == row and j == col:
                    continue
                #log.debug("Clearing {} from {}, {}".format(val, i, j))
                try:
                    ocell = self.matrix[i][j]
                    ocell.remove(val)
                except ValueError as exception:
                    msg = "Error removing {} from {}".format(val, ocell.ndx)
                    if ocell.guessing_mode:
                        log.debug(msg)
                    else:
                        log.error(msg)
                    err = True

        log.debug("Setting value {} on cell {}".format(val, cell.ndx))
        cell.set(val)
        if err:
            raise ValueError("Error setting {} to {}".format(cell.ndx, val))

    def yield_rows(self):
        for row in range(9):
            cells = [self.matrix[row][col] for col in range(9)]
            #log.debug("testing row {}".format(row))
            yield cells

    def yield_cols(self):
        for col in range(9):
            cells = [self.matrix[row][col] for row in range(9)]
            #log.debug("testing col {}".format(col))
            yield cells

    def yield_boxes(self, rowwise=False):
        for box_row in range(3):
            for box_col in range(3):
                cells = []
                if rowwise:
                    for j in range(3*box_col, 3*box_col + 3):
                        for i in range(3*box_row, 3*box_row + 3):
                            cells.append(self.matrix[i][j])
                else:
                    for i in range(3*box_row, 3*box_row + 3):
                        for j in range(3*box_col, 3*box_col + 3):
                            cells.append(self.matrix[i][j])
                log.debug("testing {} box".format(_BOX_LABELS[box_row][box_col]))
                yield cells

    def yield_cells(self):
        for row in range(9):
            for col in range(9):
                yield self.matrix[row][col]

    def direct_elim(self):
        """ check when a number can't fit anywhere else in a row, col or box """
        def unique_check(cells):
            for val in range(1, 10):
                ndx_list = [c for c in cells if c.has(val)]
                if len(ndx_list) == 1:
                    cell, = ndx_list
                    if cell.solved:
                        continue
                    log.debug("{} only fits at {}".format(val, cell.ndx))
                    cell.set(val)

        uncertainty = self.get_uncertainty()
        keep_going = True
        while keep_going:
            for row in self.yield_rows():
                unique_check(row)

            for col in self.yield_cols():
                unique_check(col)

            for box in self.yield_boxes():
                unique_check(box)

            # NOTE: it doesn't seem that these tests have different results
            # from one another
            new_uncertainty = self.get_uncertainty()
            if new_uncertainty == 0:
                log.info("finished")
                keep_going = False
            if new_uncertainty < uncertainty:
                log.debug("Uncertainty from {} to {}".format(uncertainty, new_uncertainty))
                uncertainty = new_uncertainty
            else:
                log.debug("No uncertainty reduction, quitting at {}".format(uncertainty))
                keep_going = False

    def close_sets(self):
        """ set group of x options in x locations indicates these x numbers
            can only occur in these x locations -- so they can should be removed
            from the options list outside of the specific locations where they
            are found
        """
        """ when two boxes of a row or column are known, this forces whatever fills
            the remainder of the row or column to exist as is and it excludes these
            numbers from being anywhere other than this particular row or col
        """
        def check_for_pairs(cells):
            unknowns = sum(1 for c in cells if not c.solved)
            log.debug(" {} unknowns in this group".format(unknowns))
            for group_size in range(2, unknowns):
                """ this is only useful when there are unknowns to potentially remove """
                #log.debug(" checking groups of {}".format(group_size))
                groups = [c.options for c in cells if not c.solved and len(c.options) <= group_size]
                #log.debug(" groups are {}".format(groups))
                vals = set()
                for g in groups:
                    vals.update(g)

                if len(groups) < group_size:
                    continue
                for template in itertools.combinations(vals, group_size):
                    matched = 0
                    for g in groups:
                        #log.debug("  testing if {} is contained in {}".format(g, template))
                        if set(g).issubset(template):
                            matched += 1
                            #log.debug("  matches increased to {}".format(matched))
                    if matched == group_size:
                        """ we have a winner - the items in this group
                            can be eliminated from all other cells
                        """
                        log.debug("matched group {} found".format(
                            ''.join(str(x) for x in template)))
                        for c in cells:
                            if c.solved or set(c.options).issubset(template):
                                continue
                            for val in template:
                                c.remove(val)

        uncertainty = self.get_uncertainty()
        keep_going = True
        while keep_going:
            for row in self.yield_rows():
                check_for_pairs(row)

            for col in self.yield_cols():
                c = log.debug("Checking: {}".format(','.join(c.ndx for c in col)))
                check_for_pairs(col)

            for box in self.yield_boxes():
                check_for_pairs(box)

            new_uncertainty = self.get_uncertainty()
            if new_uncertainty < uncertainty:
                log.debug("Uncertainty from {} to {}".format(uncertainty, new_uncertainty))
                uncertainty = new_uncertainty
            else:
                log.debug("No uncertainty reduction, quitting at {}".format(uncertainty))
                keep_going = False

    def box_sets(self):
        """ check within a box if there is only one row / col where a number
            can occur and remove number from that row / col in adjoining boxes

            check within a row, if there is only one box where a number can occur,
            remove that number from the other rows in the box

            check within a col, if there is only one box where a number can occur,
            remove that number from the other cols within the box

            if a number is in two rows or columns and two quads, it can't be in
            those rows or columns in the 3rd quad.. this is likely not useful

            consider when you have a total # of remaining variables & remaining
            spots spread through multiple rows / col / boxes, if you can
            determine which variable must go in a certain spot
        """
        _COL_BOX_NAMES = ["top", "center", "bottom"]
        _ROW_BOX_NAMES = ["left", "middle", "right"]


        def find_limited_blocks(cells):
            """ find values that must be located in a group of three within
                a row / col / box list of 9 values
                yield the group index where value must reside and the value
            """
            groups = [cells[i*3:i*3+3] for i in range(3)]
            group_options = [set() for _ in range(3)]
            for options, group in zip(group_options, groups):
                for cell in group:
                    options.update(cell.options)

            solved = [c.solved for c in cells if c.solved]
            for val in range(1, 10):
                if val in solved:
                    continue
                for this in range(3):
                    others = [x for x in range(3) if x != this]
                    if not any(val in group_options[n] for n in others):
                        log.debug("{} must be in set {}".format(val, this))
                        yield (this, val)


        for row, cells in enumerate(self.yield_rows()):
            for block, val in find_limited_blocks(cells):
                log.debug("Row {}, {} must be in box {}".format(row, val, block))
                """ remove val from other rows in this block """
                for i in range((row//3)*3, (row//3)*3 + 3):
                    if row == i:
                        continue
                    for col in range(block*3, block*3 + 3):
                        self.matrix[i][col].remove(val)

        for col, cells in enumerate(self.yield_cols()):
            for block, val in find_limited_blocks(cells):
                log.debug("Col {}, {} must be in box {}".format(col, val, block))
                """ remove val from other cols in this block """
                for j in range((col//3)*3, (col//3)*3 + 3):
                    if col == j:
                        continue
                    for row in range(block*3, block*3 + 3):
                        self.matrix[row][j].remove(val)


        # FIXME : try doing the same thing, but yielding column wise
        # instead of row-wise
        for box_row in range(3):
            for box_col in range(3):
                solved = []
                box_row_options = [set() for x in range(3)]   # fill with all options from row
                box_col_options = [set() for x in range(3)]
                for i in range(3*box_row, 3*box_row + 3):
                    for j in range(3*box_col, 3*box_col + 3):
                        cell = self.matrix[i][j]
                        box_row_options[i-3*box_row].update(cell.options)
                        box_col_options[j-3*box_col].update(cell.options)
                        if cell.solved:
                            solved.append(cell.solved)
                log.debug("box {}, {} row options: {}".format(box_row, box_col, box_row_options))
                log.debug("box {}, {} col options: {}".format(box_row, box_col, box_col_options))
                for val in range(1, 10):
                    if val in solved:
                        continue
                    for this in range(3):
                        others = [x for x in range(3) if x != this]
# NOTE : this should only check the larger numbers? because order isn't important?
                        if not any(val in box_row_options[n] for n in others):
                            """ only row for a value, remove from rest of row """
                            row = this + box_row * 3
                            log.debug("Row {}, {} box is the only place for {}".format(
                                row, _ROW_BOX_NAMES[box_col], val))
                            for col in range(9):
                                if col // 3 == box_col:
                                    """ don't remove value from this box """
                                    continue
                                self.matrix[row][col].remove(val)
                        if not any(val in box_col_options[n] for n in others):
                            """ only col for a value, remove from rest of col """
                            col = this + box_col * 3
                            log.debug("Col {}, {} box is the only place for {}".format(
                                col, _COL_BOX_NAMES[box_row], val))
                            for row in range(9):
                                if row // 3 == box_row:
                                    """ don't remove value from this box """
                                    continue
                                self.matrix[row][col].remove(val)

        log.debug("Uncertainty at {}".format(self.get_uncertainty()))

    def solve(self):
        uncertainty = self.get_uncertainty()
        keep_going = True
        while keep_going:
            self.direct_elim()
            self.close_sets()
            self.box_sets()

            new_uncertainty = self.get_uncertainty()
            if new_uncertainty < uncertainty:
                log.debug("Uncertainty from {} to {}".format(uncertainty, new_uncertainty))
                uncertainty = new_uncertainty
            else:
                log.debug("No uncertainty reduction, quitting at {}".format(uncertainty))
                keep_going = False


        self.guess_solution()
        self.clear_guesses()
        self.show_known(5)

    def guess_solution(self, previous_guesses=None):
        """ recursively guess solutions, storing previous guesses that were
            not unsuccessful because a clear operation must clear everything
        """
        if previous_guesses is None:
            previous_guesses = []
        for row in range(9):
            for col in range(9):
                cell = self.matrix[row][col]
                if cell.solved:
                    continue
                log.debug("{}About to go through {} for cell {}".format(
                    ' '*len(previous_guesses), cell.options, cell.ndx))
                options = list(cell.options)
                for val in options:
                    log.debug("{}Guessing {} for cell {}".format(
                        ' '*len(previous_guesses), val, cell.ndx))
                    try:
                        guess = [row, col, val]
                        self.guess(*guess)
                        uncertainty = self.get_uncertainty()
                        if uncertainty == 0:
                            return 0
                        log.debug("{}Uncertainty now at {}".format(
                            ' '*len(previous_guesses), uncertainty))
                        self.guess_solution(previous_guesses=previous_guesses + [guess])
                        """ if this doesn't cause an exception it solved """
                        return 0
                    except ValueError:
                        log.debug("{}Guess {} on {} failed, resetting".format(
                            ' '*len(previous_guesses), val, cell.ndx))
                        self.clear_guesses(clear_mistakes=True)
                        log.debug("{}Clearing all guesses".format(
                            ' '*len(previous_guesses)))
                        for guess in previous_guesses:
                            log.debug("{0}Applying {3} to {1},{2}".format(
                                ' '*len(previous_guesses), *guess))
                            self.guess(*guess)
                log.debug("{}End of options for {}".format(
                    ' '*len(previous_guesses), cell.ndx))
                raise ValueError("No valid options for cell {}".format(cell.ndx))


class Cell(object):
    def __init__(self, row, col):
        self.ndx = "{},{}".format(row, col)
        #log.debug("initializing {}".format(self.ndx))
        self._solved = False
        self._options = [i + 1 for i in range(9)]
        self.notify_cb = None
        self.known = False      # if value has been set because it was guessed
        self.failed = 0         # if the cell has failed during a guess
        self.guessing_mode = False
        self.guess = False
        self.guesses = None

    def _getSolved(self): return self.guess if self.guessing_mode else self._solved
    solved = property(fget=_getSolved)

    def _getOptions(self): return self.guesses if self.guessing_mode else self._options
    options = property(fget=_getOptions)

    def __repr__(self):
        if self._solved:
            return "Cell({})={}".format(self.ndx, self._solved)
        return "Cell({})".format(self.ndx)

    def set(self, val):
        if self.solved:
            log.debug("{} is already solved: {}".format(self.ndx, self.solved))
            log.debug('{} options are {}'.format(self.ndx, self.options))
            if self.solved != val:
                self.failed += 1
                raise ValueError("{} solved value {} is not {}".format(
                    self.ndx, self.solved, val))
            return
        log.debug("Setting {} = {} -> SOLVED".format(self.ndx, val))
        if val not in self.options:
            raise ValueError("{} not an option: {}".format(val, self.options))
        if self.guessing_mode:
            self.guesses = [val]
            self.guess = val
        else:
            self._options = [val]
            self._solved = val
        if self.notify_cb is not None:
            #log.debug("Running notify callback for {} = {}".format(self.ndx, val))
            self.notify_cb(val)

    def remove(self, val):
        if val == self.solved:
            msg = "{} can't remove {}, last option".format(self.ndx, val)
            if self.guessing_mode:
                log.debug(msg)
            else:
                log.error(msg)
            self.failed += 1
            raise ValueError(msg)
        if val in self.options:
            self.options.remove(val)
            if len(self.options) == 1:
                val = self.options[0]
                log.debug("Found {} = {}, no other options".format(self.ndx, val))
                self.set(val)

    def has(self, val):
        return val in self.options

    def set_notification(self, fcn):
        self.notify_cb = fcn

    def fmt_options(self, max_vals=5):
        if self.solved:
            rv = str(self.solved)
        elif len(self.options) > max_vals:
            rv = ''
        else:
            rv = ''.join(str(x) for x in self.options)
        if self.known and not self.solved:
            rv = '{}:{}'.format(self.known, rv[1:])
        if self.failed:
            rv += 'x'
        return rv

    def cheat(self, val=None):
        """ tells the cell that it's value should be a certain number, this
            does not impact solved status, only the display of options
        """
        if val is None and self.guessing_mode:
            val = self.guess
        elif self.guessing_mode:
            raise ValueError("Remove guessing mode before explicitly cheating")
        elif self._solved:
            log.info("{} is already solved: {}".format(self.ndx, self._solved))
            #raise ValueError("Solution to {} is already known".format(self.ndx))
            return
        if val not in self.options:
            raise ValueError("{} not an option: {}".format(val, self.options))
        log.debug("Setting {} = {} -> WAS TOLD".format(self.ndx, val))
        self.known = val
        self._options.remove(val)
        self._options.insert(0, val)

    def clear_mistakes(self):
        self.failed = 0

    def clear_cheats(self):
        self.known = False

    def set_guessing_mode(self, on=True):
        if on:
            self.guess = self._solved
            self.guesses = list(self._options)
            self.guessing_mode = True
        else:
            self.guesses = None
            self.guess = False
            self.guessing_mode = False


if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.WARNING)
    # from http://www.forbeginners.info/sudoku-puzzles/

    def run_all(puzzles):
        initial_unc = []
        uncertainties = []
        boards = []
        for p in puzzles:
            b = Board(p)
            initial_unc.append(b.get_uncertainty())
            b.solve()
            uncertainties.append(b.get_uncertainty())
            boards.append(b)
        avg_unc_begin = sum(initial_unc)/len(initial_unc)
        avg_unc = sum(uncertainties)/len(uncertainties)
        log.info("Average Starting Uncertainty: {:5.1f}".format(avg_unc_begin))
        log.info("Average Final Uncertainty   : {:5.1f}".format(avg_unc))
        return boards, uncertainties

    puzzle = [
        # 2, potential solutions, 1, complete, the incomplete doesnt work
           [[2, 0, 0,  0, 1, 0,  0, 5, 0],
            [3, 0, 5,  0, 4, 2,  0, 0, 0],
            [0, 1, 8,  0, 0, 9,  0, 0, 2],
            [0, 3, 2,  1, 0, 0,  8, 0, 0],
            [0, 0, 1,  0, 2, 0,  3, 0, 0],
            [0, 0, 9,  0, 0, 3,  2, 6, 0],
            [1, 0, 0,  7, 0, 0,  9, 8, 0],
            [0, 0, 0,  2, 6, 0,  5, 0, 7],
            [0, 6, 0,  0, 8, 0,  0, 0, 3]],

        # 2, pot. sol., 1, comp., inc fails after 2, tests
           [[2, 0, 0,  0, 8, 0,  0, 7, 6],
            [0, 0, 0,  0, 0, 0,  4, 0, 0],
            [0, 0, 0,  2, 0, 0,  5, 0, 8],
            [5, 0, 0,  1, 0, 0,  8, 6, 0],
            [0, 0, 7,  6, 0, 9,  3, 0, 0],
            [0, 6, 2,  0, 0, 7,  0, 0, 4],
            [3, 0, 6,  0, 0, 1,  0, 0, 0],
            [0, 0, 1,  0, 0, 0,  0, 0, 0],
            [8, 5, 0,  0, 6, 0,  0, 0, 3]],

            [[0, 2, 0,  0, 3, 0,  0, 4, 0],
             [6, 0, 0,  0, 0, 0,  0, 0, 3],
             [0, 0, 4,  0, 0, 0,  5, 0, 0],
             [0, 0, 0,  8, 0, 6,  0, 0, 0],
             [8, 0, 0,  0, 1, 0,  0, 0, 6],
             [0, 0, 0,  7, 0, 5,  0, 0, 0],
             [0, 0, 7,  0, 0, 0,  6, 0, 0],
             [4, 0, 0,  0, 0, 0,  0, 0, 8],
             [0, 3, 0,  0, 4, 0,  0, 2, 0]],

            [[0, 0, 9,  7, 4, 8,  0, 0, 0],
             [7, 0, 0,  0, 0, 0,  0, 0, 0],
             [0, 2, 0,  1, 0, 9,  0, 0, 0],
             [0, 0, 7,  0, 0, 0,  2, 4, 0],
             [0, 6, 4,  0, 1, 0,  5, 9, 0],
             [0, 9, 8,  0, 0, 0,  3, 0, 0],
             [0, 0, 0,  8, 0, 3,  0, 2, 0],
             [0, 0, 0,  0, 0, 0,  0, 0, 6],
             [0, 0, 0,  2, 7, 5,  9, 0, 0]],

           [[0, 0, 0,  3, 0, 8,  0, 7, 0],
            [3, 0, 0,  7, 1, 0,  0, 0, 4],
            [6, 0, 0,  0, 4, 0,  0, 0, 0],
            [1, 0, 0,  0, 0, 0,  6, 3, 0],
            [2, 0, 6,  0, 0, 0,  5, 0, 8],
            [0, 5, 3,  0, 0, 0,  0, 0, 7],
            [0, 0, 0,  0, 8, 0,  0, 0, 1],
            [7, 0, 0,  0, 6, 4,  0, 0, 5],
            [0, 1, 0,  2, 0, 7,  0, 0, 0]],

           [[5, 0, 0,  9, 0, 7,  4, 0, 3],
            [0, 4, 0,  0, 0, 0,  6, 0, 7],
            [8, 0, 0,  0, 0, 2,  0, 1, 0],
            [0, 0, 8,  3, 0, 0,  0, 7, 0],
            [0, 0, 0,  0, 7, 0,  0, 0, 0],
            [0, 3, 0,  0, 0, 4,  2, 0, 0],
            [0, 8, 0,  2, 0, 0,  0, 0, 1],
            [7, 0, 3,  0, 0, 0,  0, 6, 0],
            [6, 0, 1,  7, 0, 3,  0, 0, 5]],

           [[5, 0, 3,  0, 1, 0,  8, 0, 0],
            [1, 0, 0,  0, 0, 5,  0, 0, 0],
            [0, 7, 0,  0, 0, 3,  2, 1, 0],
            [0, 0, 7,  0, 0, 0,  0, 5, 0],
            [2, 0, 1,  9, 0, 7,  6, 0, 4],
            [0, 3, 0,  0, 0, 0,  7, 0, 0],
            [0, 2, 9,  4, 0, 0,  0, 6, 0],
            [0, 0, 0,  3, 0, 0,  0, 0, 7],
            [0, 0, 5,  0, 7, 0,  4, 0, 9]],

           [[0, 0, 0,  0, 0, 2,  7, 0, 0],
            [0, 0, 0,  0, 1, 5,  0, 3, 2],
            [4, 0, 0,  0, 8, 0,  1, 6, 0],
            [0, 2, 0,  0, 0, 4,  0, 0, 0],
            [7, 5, 0,  0, 2, 0,  0, 4, 9],
            [0, 0, 0,  5, 0, 0,  0, 8, 0],
            [0, 4, 3,  0, 9, 0,  0, 0, 6],
            [5, 9, 0,  2, 4, 0,  0, 0, 0],
            [0, 0, 8,  1, 0, 0,  0, 0, 0]],

           [[0, 5, 0,  3, 0, 0,  2, 0, 0],
            [2, 0, 3,  0, 0, 0,  0, 0, 0],
            [0, 4, 0,  0, 2, 0,  3, 8, 0],
            [0, 0, 5,  1, 9, 0,  0, 3, 0],
            [6, 0, 0,  7, 0, 5,  0, 0, 1],
            [0, 9, 0,  0, 3, 2,  8, 0, 0],
            [0, 2, 7,  0, 6, 0,  0, 4, 0],
            [0, 0, 0,  0, 0, 0,  1, 0, 9],
            [0, 0, 9,  0, 0, 8,  0, 2, 0]],

           [[0, 0, 5,  0, 0, 7,  0, 0, 2],
            [2, 0, 4,  0, 0, 0,  9, 0, 0],
            [9, 6, 0,  0, 0, 0,  0, 3, 0],
            [0, 0, 0,  7, 6, 0,  0, 0, 0],
            [7, 0, 0,  2, 4, 1,  0, 0, 6],
            [0, 0, 0,  0, 5, 9,  0, 0, 0],
            [0, 3, 0,  0, 0, 0,  0, 6, 8],
            [0, 0, 7,  0, 0, 0,  2, 0, 9],
            [1, 0, 0,  4, 0, 0,  7, 0, 0]],

           [[0, 0, 0,  0, 1, 5,  0, 7, 4],
            [0, 0, 0,  0, 3, 0,  8, 0, 0],
            [0, 8, 7,  0, 0, 0,  5, 0, 1],
            [0, 2, 3,  0, 0, 4,  0, 0, 0],
            [0, 1, 0,  0, 7, 0,  0, 2, 0],
            [0, 0, 0,  2, 0, 0,  7, 9, 0],
            [8, 0, 6,  0, 0, 0,  2, 4, 0],
            [0, 0, 1,  0, 2, 0,  0, 0, 0],
            [2, 3, 0,  6, 4, 0,  0, 0, 0]],

           [[2, 0, 0,  0, 1, 0,  0, 5, 0],
            [3, 0, 5,  0, 4, 2,  0, 0, 0],
            [0, 1, 8,  0, 0, 9,  0, 0, 2],
            [0, 3, 2,  1, 0, 0,  8, 0, 0],
            [0, 0, 1,  0, 2, 0,  3, 0, 0],
            [0, 0, 9,  0, 0, 3,  2, 6, 0],
            [1, 0, 0,  7, 0, 0,  9, 8, 0],
            [0, 0, 0,  2, 6, 0,  5, 0, 7],
            [0, 6, 0,  0, 8, 0,  0, 0, 3]],

           [[3, 0, 0,  8, 0, 1,  5, 0, 0],
            [0, 0, 2,  3, 0, 0,  0, 0, 0],
            [9, 0, 0,  0, 5, 0,  0, 3, 0],
            [0, 0, 5,  0, 7, 0,  0, 0, 3],
            [8, 0, 0,  0, 0, 0,  0, 7, 0],
            [0, 0, 6,  0, 2, 0,  0, 0, 1],
            [2, 0, 0,  0, 8, 0,  0, 1, 0],
            [0, 0, 3,  1, 0, 0,  0, 0, 0],
            [1, 0, 0,  4, 0, 5,  6, 0, 0]],

           [[4, 9, 0,  0, 7, 2,  0, 0, 0],
            [5, 0, 0,  4, 0, 0,  0, 0, 0],
            [8, 0, 7,  0, 0, 0,  4, 3, 0],
            [0, 0, 0,  0, 8, 0,  0, 0, 5],
            [0, 0, 1,  0, 0, 9,  2, 0, 7],
            [0, 0, 0,  0, 6, 0,  0, 0, 4],
            [7, 0, 5,  0, 0, 0,  8, 9, 0],
            [1, 0, 0,  9, 0, 0,  0, 0, 0],
            [9, 3, 0,  0, 2, 6,  0, 0, 0]],
           ]


    boards, uncertainties = run_all(puzzle)
    b = boards[2]
    exports = [b.export() for b in boards]
    print("Uncertainties are:")
    print(", ".join('{}'.format(u) for u in uncertainties))
