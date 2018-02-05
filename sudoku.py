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
                #log.debug("Cell {} update is {},{}".format(cell._ndx, row, col))
                self.matrix[row][col] = cell
                cell.set_notification(mk_lambda(row, col))
        for row in range(9):
            for col in range(9):
                cell = self.matrix[row][col]
                init_val = init[row][col]
                if init_val != 0:
                    log.info("Init of {} = {}".format(cell._ndx, init_val))
                    cell.set(init_val)
        log.info("Initial uncertainty {}".format(self.get_uncertainty()))

    def get_uncertainty(self):
        uncertainty = 0
        for col in range(9):
            for row in range(9):
                cell = self.matrix[row][col]
                uncertainty += len(cell.options) - 1
        return uncertainty

    def show_known(self, max_options=1):
        lines = []
        row_fmt = "|{}{}{}|{}{}{}|{}{}{}|"
        for row in range(9):
            cells = [self.matrix[row][col] for col in range(9)]
            uses = [len(cell.options) <= max_options for cell in cells]
            vals = [''.join(str(x) for x in cell.options) if use else '' for cell, use in zip(cells, uses)]
            txt = ['{:^5}'.format(v) for v in vals]
            #log.debug("vals is {}".format(vals))
            lines.append(row_fmt.format(*txt))
            if row % 3 == 0:
                lw = len(lines[-1])
                lines.insert(-1, '-'*lw)
        lines.append('-'*lw)
        print('\n'.join(lines))

    def update(self, row, col, val):
        """ clear val from row, col and quadrant """
        log.debug("Clearing {} from row {}".format(val, row))
        for j in range(9):
            if j == col:
                continue
            #log.debug("Clearing {} from {}, {}".format(val, row, j))
            self.matrix[row][j].remove(val)

        log.debug("Clearing {} from col {}".format(val, col))
        for i in range(9):
            if i == row:
                continue
            #log.debug("Clearing {} from {}, {}".format(val, i, col))
            self.matrix[i][col].remove(val)

        box_row, box_col = row // 3, col // 3
        log.debug("Clearing {} from {} box".format(val, _BOX_LABELS[box_row][box_col]))
        for i in range(3*box_row, 3*box_row + 3):
            for j in range(3*box_col, 3*box_col + 3):
                if i == row and j == col:
                    continue
                #log.debug("Clearing {} from {}, {}".format(val, i, j))
                self.matrix[i][j].remove(val)

        cell = self.matrix[row][col]
        #log.debug("Setting value {} on cell {}".format(val, cell._ndx))
        cell.set(val)

    def yield_rows(self):
        for row in range(9):
            cells = [self.matrix[row][col] for col in range(9)]
            log.debug("testing row {}".format(row))
            yield cells

    def yield_cols(self):
        for col in range(9):
            cells = [self.matrix[row][col] for row in range(9)]
            log.debug("testing col {}".format(col))
            yield cells

    def yield_boxes(self):
        for box_row in range(3):
            for box_col in range(3):
                cells = []
                for i in range(3*box_row, 3*box_row + 3):
                    for j in range(3*box_col, 3*box_col + 3):
                        cells.append(self.matrix[i][j])
                log.debug("testing {} box".format(_BOX_LABELS[box_row][box_col]))
                yield cells

    def direct_elim(self):
        """ check when a number can't fit anywhere else in a row, col or box """
        def unique_check(cells):
            for val in range(1, 10):
                ndx_list = [c for c in cells if c.has(val)]
                if len(ndx_list) == 1:
                    cell, = ndx_list
                    if cell.solved:
                        continue
                    log.info("{} only fits at {}".format(val, cell._ndx))
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

            # NOTE: it doesn't seem that these tests are different from one
            # another
            new_uncertainty = self.get_uncertainty()
            if new_uncertainty < uncertainty:
                log.info("Uncertainty from {} to {}".format(uncertainty, new_uncertainty))
                uncertainty = new_uncertainty
            else:
                log.info("No uncertainty reduction, quitting at {}".format(uncertainty))
                keep_going = False

    def close_sets(self):
        """ set group of x options in x locations indicates these x numbers
            can only occur in these x locations -- so they can should be removed
            from the options list outside of the specific locations where they
            are found
        """
        def check_for_pairs(cells):
            unknowns = sum(1 for c in cells if not c.solved)
            log.debug("{} unknowns in this group".format(unknowns))
            for group_size in range(2, unknowns):
                """ this is only useful when there are unknowns to potentially remove """
                groups = [c.options for c in cells if len(c.options) == group_size]
                if len(groups) < group_size:
                    continue
                for template in groups:
                    matched = 0
                    for g in groups:
                        if template == g:
                            matched += 1
                    if matched == group_size:
                        """ we have a winner - the items in this group
                            can be eliminated from all other cells
                        """
                        log.info("matched group {} found".format(
                            ''.join(str(x) for x in template)))
                        for c in cells:
                            if c.solved or c.options == template:
                                continue
                            for val in template:
                                c.remove(val)


        uncertainty = self.get_uncertainty()
        keep_going = True
        while keep_going:
            for row in self.yield_rows():
                check_for_pairs(row)

            for col in self.yield_cols():
                check_for_pairs(col)

            for box in self.yield_boxes():
                check_for_pairs(box)

            new_uncertainty = self.get_uncertainty()
            if new_uncertainty < uncertainty:
                log.info("Uncertainty from {} to {}".format(uncertainty, new_uncertainty))
                uncertainty = new_uncertainty
            else:
                log.info("No uncertainty reduction, quitting at {}".format(uncertainty))
                keep_going = False

class Cell(object):
    def __init__(self, row, col):
        self._ndx = "{},{}".format(row, col)
        #log.debug("initializing {}".format(self._ndx))
        self.solved = False
        self.options = [i + 1 for i in range(9)]
        self.notify_cb = None

    def __repr__(self):
        if self.solved:
            return "Cell({})={}".format(self._ndx, self.solved)
        return "Cell({})".format(self._ndx)

    def set(self, val):
        if self.solved:
            if self.solved != val:
                raise ValueError("{} solved value {} is not {}".format(
                    self._ndx, self.solved, val))
            return
        #log.info("Setting {} = {} -> SOLVED".format(self._ndx, val))
        if val not in self.options:
            raise ValueError("{} not an option: {}".format(val, self.options))
        self.options = [val]
        self.solved = val
        if self.notify_cb is not None:
            #log.debug("Running notify callback for {} = {}".format(self._ndx, val))
            self.notify_cb(val)

    def remove(self, val):
        if val in self.options:
            self.options.remove(val)
            if len(self.options) == 1:
                val = self.options[0]
                log.info("Found {} = {}, no other options".format(self._ndx, val))
                self.set(val)

    def has(self, val):
        return val in self.options

    def set_notification(self, fcn):
        self.notify_cb = fcn




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    X = [[0, 2, 0,  0, 3, 0,  0, 4, 0],
         [6, 0, 0,  0, 0, 0,  0, 0, 3],
         [0, 0, 4,  0, 0, 0,  5, 0, 0],
         [0, 0, 0,  8, 0, 6,  0, 0, 0],
         [8, 0, 0,  0, 1, 0,  0, 0, 6],
         [0, 0, 0,  7, 0, 5,  0, 0, 0],
         [0, 0, 7,  0, 0, 0,  6, 0, 0],
         [4, 0, 0,  0, 0, 0,  0, 0, 8],
         [0, 3, 0,  0, 4, 0,  0, 2, 0]]

    # test 1 - works w/ 2 tests
    # from http://www.forbeginners.info/sudoku-puzzles/
    X = [[0, 0, 9,  7, 4, 8,  0, 0, 0],
         [7, 0, 0,  0, 0, 0,  0, 0, 0],
         [0, 2, 0,  1, 0, 9,  0, 0, 0],
         [0, 0, 7,  0, 0, 0,  2, 4, 0],
         [0, 6, 4,  0, 1, 0,  5, 9, 0],
         [0, 9, 8,  0, 0, 0,  3, 0, 0],
         [0, 0, 0,  8, 0, 3,  0, 2, 0],
         [0, 0, 0,  0, 0, 0,  0, 0, 6],
         [0, 0, 0,  2, 7, 5,  9, 0, 0]]

    # test 2, - works w/ 1, test
    X = [[0, 0, 0,  3, 0, 8,  0, 7, 0],
         [3, 0, 0,  7, 1, 0,  0, 0, 4],
         [6, 0, 0,  0, 4, 0,  0, 0, 0],
         [1, 0, 0,  0, 0, 0,  6, 3, 0],
         [2, 0, 6,  0, 0, 0,  5, 0, 8],
         [0, 5, 3,  0, 0, 0,  0, 0, 7],
         [0, 0, 0,  0, 8, 0,  0, 0, 1],
         [7, 0, 0,  0, 6, 4,  0, 0, 5],
         [0, 1, 0,  2, 0, 7,  0, 0, 0]]

    # test 3, - 2, potential solutions, 1, complete, the incomplete doesnt work
    X = [[2, 0, 0,  0, 1, 0,  0, 5, 0],
         [3, 0, 5,  0, 4, 2,  0, 0, 0],
         [0, 1, 8,  0, 0, 9,  0, 0, 2],
         [0, 3, 2,  1, 0, 0,  8, 0, 0],
         [0, 0, 1,  0, 2, 0,  3, 0, 0],
         [0, 0, 9,  0, 0, 3,  2, 6, 0],
         [1, 0, 0,  7, 0, 0,  9, 8, 0],
         [0, 0, 0,  2, 6, 0,  5, 0, 7],
         [0, 6, 0,  0, 8, 0,  0, 0, 3]]

    # test 4, - works w/ 2, tests
    X = [[5, 0, 0,  9, 0, 7,  4, 0, 3],
         [0, 4, 0,  0, 0, 0,  6, 0, 7],
         [8, 0, 0,  0, 0, 2,  0, 1, 0],
         [0, 0, 8,  3, 0, 0,  0, 7, 0],
         [0, 0, 0,  0, 7, 0,  0, 0, 0],
         [0, 3, 0,  0, 0, 4,  2, 0, 0],
         [0, 8, 0,  2, 0, 0,  0, 0, 1],
         [7, 0, 3,  0, 0, 0,  0, 6, 0],
         [6, 0, 1,  7, 0, 3,  0, 0, 5]]

    # test 5, - works w/ 1, test
    X = [[5, 0, 3,  0, 1, 0,  8, 0, 0],
         [1, 0, 0,  0, 0, 5,  0, 0, 0],
         [0, 7, 0,  0, 0, 3,  2, 1, 0],
         [0, 0, 7,  0, 0, 0,  0, 5, 0],
         [2, 0, 1,  9, 0, 7,  6, 0, 4],
         [0, 3, 0,  0, 0, 0,  7, 0, 0],
         [0, 2, 9,  4, 0, 0,  0, 6, 0],
         [0, 0, 0,  3, 0, 0,  0, 0, 7],
         [0, 0, 5,  0, 7, 0,  4, 0, 9]]

    # test 6, - works w/ 1, test
    X = [[0, 0, 0,  0, 0, 2,  7, 0, 0],
         [0, 0, 0,  0, 1, 5,  0, 3, 2],
         [4, 0, 0,  0, 8, 0,  1, 6, 0],
         [0, 2, 0,  0, 0, 4,  0, 0, 0],
         [7, 5, 0,  0, 2, 0,  0, 4, 9],
         [0, 0, 0,  5, 0, 0,  0, 8, 0],
         [0, 4, 3,  0, 9, 0,  0, 0, 6],
         [5, 9, 0,  2, 4, 0,  0, 0, 0],
         [0, 0, 8,  1, 0, 0,  0, 0, 0]]

    # test 7, - 2, pot. sol., 1, comp., inc fails after 2, tests
    X = [[2, 0, 0,  0, 8, 0,  0, 7, 6],
         [0, 0, 0,  0, 0, 0,  4, 0, 0],
         [0, 0, 0,  2, 0, 0,  5, 0, 8],
         [5, 0, 0,  1, 0, 0,  8, 6, 0],
         [0, 0, 7,  6, 0, 9,  3, 0, 0],
         [0, 6, 2,  0, 0, 7,  0, 0, 4],
         [3, 0, 6,  0, 0, 1,  0, 0, 0],
         [0, 0, 1,  0, 0, 0,  0, 0, 0],
         [8, 5, 0,  0, 6, 0,  0, 0, 3]]

    # test 8, - works w/ 2, tests
    X = [[0, 5, 0,  3, 0, 0,  2, 0, 0],
         [2, 0, 3,  0, 0, 0,  0, 0, 0],
         [0, 4, 0,  0, 2, 0,  3, 8, 0],
         [0, 0, 5,  1, 9, 0,  0, 3, 0],
         [6, 0, 0,  7, 0, 5,  0, 0, 1],
         [0, 9, 0,  0, 3, 2,  8, 0, 0],
         [0, 2, 7,  0, 6, 0,  0, 4, 0],
         [0, 0, 0,  0, 0, 0,  1, 0, 9],
         [0, 0, 9,  0, 0, 8,  0, 2, 0]]

    # test 9, - works w/ 1, test
    X = [[0, 0, 5,  0, 0, 7,  0, 0, 2],
         [2, 0, 4,  0, 0, 0,  9, 0, 0],
         [9, 6, 0,  0, 0, 0,  0, 3, 0],
         [0, 0, 0,  7, 6, 0,  0, 0, 0],
         [7, 0, 0,  2, 4, 1,  0, 0, 6],
         [0, 0, 0,  0, 5, 9,  0, 0, 0],
         [0, 3, 0,  0, 0, 0,  0, 6, 8],
         [0, 0, 7,  0, 0, 0,  2, 0, 9],
         [1, 0, 0,  4, 0, 0,  7, 0, 0]]

    # test 10, - works w/ 1, test
    X = [[0, 0, 0,  0, 1, 5,  0, 7, 4],
         [0, 0, 0,  0, 3, 0,  8, 0, 0],
         [0, 8, 7,  0, 0, 0,  5, 0, 1],
         [0, 2, 3,  0, 0, 4,  0, 0, 0],
         [0, 1, 0,  0, 7, 0,  0, 2, 0],
         [0, 0, 0,  2, 0, 0,  7, 9, 0],
         [8, 0, 6,  0, 0, 0,  2, 4, 0],
         [0, 0, 1,  0, 2, 0,  0, 0, 0],
         [2, 3, 0,  6, 4, 0,  0, 0, 0]]

    b = Board(X)
