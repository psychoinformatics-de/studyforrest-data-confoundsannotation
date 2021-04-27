#!/usr/bin/env python3
'''extracts root mean square power and left-right volume from a given video's
audio track and saves it to a tab-separated values files
'''


from moviepy.audio.io.readers import FFMPEG_AudioReader
import argparse
import numpy as np
import os


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='computes the root mean square power and left-right' +
        'volume difference for every movie frame'
    )

    parser.add_argument('-i',
                        default='inputs/media/stimuli/phase2/' +
                        'fg_av_ger_seg0.mkv',
                        help='input movie file')

    parser.add_argument('-o',
                        default='test/audio',
                        help='output directory')

    args = parser.parse_args()

inDir = args.i
    outDir = args.o

    return inDir, outDir


def extract_audio_rmspower(movie_fpath):
    '''
    '''
    fps = 48000
    dt = 0.04
    chunk_size = int(dt * fps)
    t = 0.0

    reader = FFMPEG_AudioReader(
        movie_fpath,
        500,
        fps=fps)
    # last few frame after fade-out have no audio
    duration = reader.duration - 0.120

    # initialize list using the file header
    rms_lines = ['onset\tduration\trms']
    lrdiff_lines = ['onset\tduration\tlrdiff']

    while t <= duration:
        a = reader.read_chunk(chunk_size)

        rms = np.sqrt(np.mean(a ** 2, axis=0))
        rms_sum = np.sum(rms)
        # write line with start, frame duration, value
        rms_line = f'{t:.2f}\t{dt}\t{rms_sum:.8f}'
        rms_lines.append(rms_line)

        lr_diff = np.diff(rms).item()
        # write line with start, frame duration, value
        lrdiff_line = f'{t:.2f}\t{dt}\t{lr_diff:.8f}'
        lrdiff_lines.append(lrdiff_line)

        # prepare next loop
        t += dt

    return rms_lines, lrdiff_lines


if __name__ == '__main__':
    # get command line arguments
    in_fpath, out_path = parse_arguments()
    # create the output path
    os.makedirs(out_path, exist_ok=True)

    # call the function that returns a list of lines with tab-separated values
    rms_lines, lrdiff_lines = extract_audio_rmspower(in_fpath)

    for variable, lines in zip(['rms', 'lrdiff'], [rms_lines, lrdiff_lines]):
        # prepare output path & filename
        in_file = os.path.basename(in_fpath)
        out_file = os.path.splitext(in_file)[0] + f'_{variable}.tsv'
        out_fpath = os.path.join(out_path, out_file)

        # save file
        with open(out_fpath, 'w') as f:
            # write the value
            for line in lines:
                f.write(line + '\n')
