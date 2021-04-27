#
# Compute perceptual difference if neighboring movie frames, by means of the
# Hamming distance of they perceptual hashes (phash).
#
# Input pHashes have 144 bit length, and the output distance is normalized by
# by this maximum, i.e. the maximum distance of 1.0 indicates that all
# 144 bits changes, the minim non-zero distance is 1/144 -> 0.00694
#
# The output file has one line per frame (plus header line). Each distance
# indicates the distance of the current frame with respect to the one
# immediately preceding it.
#

import imagehash as ih
import numpy as np
import os
from os.path import join as opj, exists, dirname
import sys

# load hash data
phdata = np.recfromcsv('test/visual/fg_av_ger_seg0_phash.tsv', delimiter='\t')  # sys.argv[1])
movie_time = phdata['onset']

# convert into bit arrays
# I hate the following line
phashes = np.array(
    [ih.hex_to_hash(i.decode()).hash.ravel() for i in phdata['phash']])

diff1 = [
    np.count_nonzero(p != phashes[i]) / phashes.shape[1]
    for i, p in enumerate(phashes[1:])]

odir = dirname(sys.argv[1])
if not exists(odir):
    os.makedirs(odir)

# header plus first frame diff set to 0
print('movie_time,norm_diff\n0.00,0.0')
for i, d in enumerate(diff1):
    print('%.2f,%f' % (movie_time[i + 1], d))
