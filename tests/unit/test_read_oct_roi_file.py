# Copyright (C) 2019 Harvard University. All Rights Reserved. Unauthorized
# copying of this file, via any medium is strictly prohibited Proprietary and
# confidential
# Developed by Mohammad Haft-Javaherian <mhaft_javaherian@mgh.harvard.edu>,
#                                       <7javaherian@gmail.com>.
# ==============================================================================

"""Test read_oct_roi_file"""

from __future__ import absolute_import, division, print_function

import os

import numpy as np
import tifffile

from ...util.read_oct_roi_file import read_oct_roi_file, lumen_iel_mask


def test_read_oct_roi_file():
    file_path = os.path.dirname(os.path.realpath(__file__)) + '/fixtures/test_read_oct_roi_fileROI.txt'
    im_shape = [5, 10, 10]
    out = read_oct_roi_file(file_path, im_shape)
    tifffile.imwrite(file_path[:-4] + '-out.tif', out)
    np.testing.assert_array_equal(out[1, 2, 1:4], [3, 3, 3])


def test_small_obj_list():
    _ = lumen_iel_mask([[1, 1, 1]], (2, 10, 10, 2))
