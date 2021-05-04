#!/usr/bin/env python3
'''Reads in a given movie file frame-by-frame and outputs average luminance
for each quadrant

To Do:

    - check why current phashes are different from formerly computed phashes
    - implement (on-the-fly) computing of perceptual differences
    - maybe change the standard output directory from 'test' to './'


1. frame-time in seconds
2. mean perceived luminance upper left quadrant
3. mean perceived luminance upper right quadrant
4. mean perceived luminance lower left quadrant
5. mean perceived luminance lower right quadrant

All computations are done on a cropped-frame that excluded the horizontal
bars in the movie stimulus files.

Perceived luminance as proposed: http://alienryderflex.com/hsp.html
'''

from moviepy.video.io.VideoFileClip import VideoFileClip
from fg_hashing import hash_frame
import argparse
import imagehash as ih
import numpy as np
import os


# constant(s)
CROP_SIZE = (90, 630)


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='computes low-level confounds per every movie frame' +
        'of a stimulus segment'
    )

    parser.add_argument('-i',
                        nargs='+',  # allow regular expression in argument
                        default='inputs/media/stimuli/phase2/' +
                        'fg_av_ger_seg0.mkv',
                        help='input movie file (or pattern)')

    parser.add_argument('-o',
                        default='test/visual',
                        help='output directory')

    args = parser.parse_args()

    in_files = sorted(args.i)
    out_dir = args.o

    return in_files, out_dir


def rgb2pluminance(frame):
    '''Convertes an RGB frame array into an array of perceived luminance
    with the same pixel dimensions'''
    # Perceived luminance as proposed: http://alienryderflex.com/hsp.html
    b = frame.astype('float64') ** 2
    b *= [.299, .587, .114]
    return np.sqrt(np.sum(b, axis=2))


def float2uint8(f):
    return int(np.round(f))


def extract_visual_information(moviefile, crop_size):
    '''
    '''
    vs = VideoFileClip(moviefile)
    duration = vs.duration
    # time difference between two movie frames
    dt = 1. / vs.fps
    t = 0.0

    # initialize list
    all_frames = []

    while t <= duration:
        # grab frame from video file, ensure consistent dtype
        frame_arr = vs.get_frame(t).astype('float64')
        # crop bars
        frame_arr = frame_arr[crop_size[0]:crop_size[1]]
        bness = rgb2pluminance(frame_arr)
        # upper left
        ul = float2uint8(bness[:270, :640].mean())
        # upper right
        ur = float2uint8(bness[:270, 640:].mean())
        # lower left
        ll = float2uint8(bness[270:, :640].mean())
        # lower right
        lr = float2uint8(bness[270:, 640:].mean())

        # mean
        mean = (ul + ur + ll + lr) / 4.0  # float2uint8(bness[:, :].mean())
        # difference upper half of frame minus lower halt
        ud_diff = (ul + ur) - (ll + lr)
        # difference left half of frame minus right half
        lr_diff = (ul + ll) - (ur + lr)

        # compute the phash and md5sum
        frame_arr = vs.get_frame(t).astype('uint8')

        md5sum, percep_hash = hash_frame(frame_arr)

        # gather info
        cur_frame = (mean, ud_diff, lr_diff, percep_hash, md5sum)
        # populate the list
        all_frames.append(cur_frame)
        # prepare next loop
        t += dt

    return all_frames


def compute_perceptual_differences(in_fpath):
    '''Main body of the former script 'compute_perceptual_difference.py' now as
    in this script. Needs to be implemented either above

    Compute perceptual difference if neighboring movie frames, by means of the
    Hamming distance of they perceptual hashes (phash).

    Input pHashes have 144 bit length, and the output distance is normalized by
    by this maximum, i.e. the maximum distance of 1.0 indicates that all
    144 bits changes, the minim non-zero distance is 1/144 -> 0.00694

    The output file has one line per frame (plus header line). Each distance
    indicates the distance of the current frame with respect to the one
    immediately preceding it.
    '''
    # load hash data
    phdata = np.recfromcsv(in_fpath, delimiter='\t')  # sys.argv[1])

    # ih.hex_to_hash takes only one argument in current imagehash module
    # previously, the line was
    # [ih.hex_to_hash(i.decode(), 12).hash.ravel() for i in phdata['phash']])
    phashes = np.array(
        [ih.hex_to_hash(i.decode()).hash.ravel() for i in phdata['phash']])

    diff1 = [
        np.count_nonzero(p != phashes[i]) / phashes.shape[1]
        for i, p in enumerate(phashes[1:])]

    # saving (as performed in the old script
    out_fpath = in_fpath.replace('_phash', '_normdiff')

    # header plus first frame diff set to 0
    lines = [f'{t*0.04:.2f}\t0.04\t{line:.6f}'
             for t, line in enumerate(diff1)]

    with open(out_fpath, 'w') as f:
        # write header
        f.write(f'onset\tduration\tnorm_diff\n')
        # write the value
        for line in lines:
            f.write(line + '\n')

    return None


if __name__ == '__main__':
    # get command line argument
    in_fpathes, out_path = parse_arguments()
    # create the output path
    os.makedirs(out_path, exist_ok=True)

    variables = ['brmean', 'brud', 'brlr', 'phash', 'md5sum']
    for in_fpath in in_fpathes:
        # get the results in a list of tuples representing the variables
        results = extract_visual_information(in_fpath, CROP_SIZE)

        # write one file per extracted info
        for idx, variable in enumerate(variables):
            # construct the lines to be written for the current variable
            lines = [f'{t*0.04:.2f}\t0.04\t{line[idx]}'
                     for t, line in enumerate(results)]

            # prepare output path & filename
            in_file = os.path.basename(in_fpath)
            out_file = os.path.splitext(in_file)[0] + f'_{variable}.tsv'
            out_fpath = os.path.join(out_path, out_file)

            # save the file
            with open(out_fpath, 'w') as f:
                # write header
                f.write(f'onset\tduration\t{variable}\n')
                # write the value
                for line in lines:
                    f.write(line + '\n')

        # compute perceptual differences (and write to file)
        in_phashes_f = os.path.splitext(in_file)[0] + f'_phash.tsv'
        in_phashes_fpath = os.path.join(out_path, in_phashes_f)
        compute_perceptual_differences(in_phashes_fpath)
        print(in_phashes_fpath)
