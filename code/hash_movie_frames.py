#!/usr/bin/env python3
'''Reads in a given movie file frame-by-frame and outputs identifying
information for each

The script will write a CSV table to stdout with the following colums

1. zero-based frame index
2. frame-time in seconds
3. 144 bit (12x12 bins) perceptual hash (in hex form)
4. MD5 hash of the decoded frame image data (in hex form)

All hashing is done on a cropped-frame that excluded the horizontal
bars in the movie stimulus files. This should make results more
robust across different rendering of stimulus files (some use gray
bars)
'''

from moviepy.video.io.VideoFileClip import VideoFileClip
from fg_hashing import hash_frame
import argparse
import os


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='computes hashes for every movie frame ' +
        'of a stimulus segment'
    )

    parser.add_argument('-i',
                        default='inputs/media/stimuli/phase2/' +
                        'fg_av_ger_seg0.mkv',
                        help='input movie file')

    parser.add_argument('-o',
                        default='test/frame_hashes',
                        help='output directory')

    args = parser.parse_args()

    inDir = args.i
    outDir = args.o

    return inDir, outDir


def hash_movie_frames(moviefile):
    '''
    '''
    vs = VideoFileClip(moviefile)
    duration = vs.duration
    # time difference between two movie frames
    dt = 1. / vs.fps

    frame_idx = 0
    t = 0.0

    # initialize list
    all_frames = []

    # table header
    print('frame_idx,movie_time,phash,md5sum')

    while t <= duration:
        # grab frame from video file, ensure consistent dtype
        frame_arr = vs.get_frame(t).astype('uint8')

        md5sum, percep_hash = hash_frame(frame_arr)

        # print to stdout
        print('{:d},{:.2f},{},{}'.format(
            frame_idx,
            t,
            percep_hash,
            md5sum)
        )

        # create a line for the list that will be returned by this function
        cur_frame = '{:d}\t{:.2f}\t{}\t{}'.format(
            frame_idx,
            t,
            percep_hash,
            md5sum
        )

        # populate the list
        all_frames.append(cur_frame)

        # prepare next loop
        frame_idx += 1
        t += dt

    return all_frames


if __name__ == '__main__':
    # get command line argument
    in_fpath, out_path = parse_arguments()
    # create the output path
    os.makedirs(out_path, exist_ok=True)

    # prepare output path & filename
    in_file = os.path.basename(in_fpath)
    out_file = os.path.splitext(in_file)[0] + '_frame-hashes.tsv'
    out_fpath = os.path.join(out_path, out_file)

    results = hash_movie_frames(in_fpath)

    # save file
    with open(out_fpath, 'w') as f:
        # write header
        f.write('frame_idx\tmovie_time,\tphash,\tmd5sum\n')
        # write the value
        for line in results:
            f.write(line + '\n')
