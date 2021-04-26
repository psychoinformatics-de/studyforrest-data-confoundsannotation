#!/usr/bin/env python3
'''Reads in a given movie file frame-by-frame and outputs average luminance for each quadrant

To Do:
    - writes a file but still prints all values to stdout
      which was probably originally used to redirect to a file
    - maybe change the standard output directory from 'test' to './'


The script will write a CSV table to stdout with the following colums

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
import argparse
import numpy as np
import os

# constant(s)
CROP_SIZE = (90, 630)


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='computes the luminance per quadrant for every movie' +
        'frame of a stimulus segment'
    )

    parser.add_argument('-i',
                        default='inputs/media/stimuli/phase2/' +
                        'fg_av_ger_seg0.mkv',
                        help='input movie file')

    parser.add_argument('-o',
                        default='test/luminance',
                        help='output directory')

    args = parser.parse_args()

    inDir = args.i
    outDir = args.o

    return inDir, outDir


def rgb2pluminance(frame):
    '''Convertes an RGB frame array into an array of perceived luminance
    with the same pixel dimensions'''
    # Perceived luminance as proposed: http://alienryderflex.com/hsp.html
    b = frame.astype('float64') ** 2
    b *= [.299, .587, .114]
    return np.sqrt(np.sum(b, axis=2))


def float2uint8(f):
    return int(np.round(f))


def extract_luminance(moviefile, crop_size):
    '''
    '''
    vs = VideoFileClip(moviefile)
    duration = vs.duration
    # time difference between two movie frames
    dt = 1. / vs.fps
    t = 0.0

    # initialize list
    all_frames = []

    # table header
    print('movie_time,ul,ur,ll,lr')

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

        # print to stdout
        print('{:.2f},{:d},{:d},{:d},{:d}'.format(t, ul, ur, ll, lr))
        # create a line for the list that will be returned by this function
        cur_frame = '{:.2f}\t{:d}\t{:d}\t{:d}\t{:d}'.format(t, ul, ur, ll, lr)

        # populate the list
        all_frames.append(cur_frame)
        # prepare next loop
        t += dt

    return all_frames


if __name__ == '__main__':
    # cl argument
    in_fpath, out_path = parse_arguments()
    # create the output path
    os.makedirs(out_path, exist_ok=True)

    # prepare output path & filename
    in_file = os.path.basename(in_fpath)
    out_file = os.path.splitext(in_file)[0] + '.tsv'
    out_fpath = os.path.join(out_path, out_file)

    results = extract_luminance(in_fpath, CROP_SIZE)

    # save file
    with open(out_fpath, 'w') as f:
        # write header
        f.write('movie_time\tul\tur\tll\tlr\n')
        # write the value
        for line in results:
            f.write(line + '\n')
