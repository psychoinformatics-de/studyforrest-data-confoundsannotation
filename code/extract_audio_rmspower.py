#!/usr/bin/env python3
'''
To Do:
    - writes a file but still prints all values to stdout
      which was probably originally used to redirect to a file
    - maybe change the standard output directory from 'test' to './'
'''


from moviepy.audio.io.readers import FFMPEG_AudioReader
import argparse
import numpy as np
import os


def parse_arguments():
    '''
    '''
    parser = argparse.ArgumentParser(
        description='computes the root mean square power across every movie' +
        'frame of a stimulus segment'
    )

    parser.add_argument('-i',
                        default='inputs/media/stimuli/phase2/' +
                        'fg_av_ger_seg0.mkv',
                        help='input movie file')

    parser.add_argument('-o',
                        default='test/audio_rmspower',
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

    # initialize list
    all_frames = []

    # table header
    print('movie_time,rms,lr_diff')

    while t <= duration:
        a = reader.read_chunk(chunk_size)
        rms = np.sqrt(np.mean(a ** 2, axis=0))
        rms_sum = np.sum(rms)
        lr_diff = np.diff(rms).item()

        # print to stdout
        print('{:.2f},{:.6e},{:.6e}'.format(t, rms_sum, lr_diff))
        # create a line for the list that will be returned by this function
        cur_frame = '{:.2f}\t{:.6e}\t{:.6e}'.format(t, rms_sum, lr_diff)

        # populate the list
        all_frames.append(cur_frame)
        # prepare next loop
        t += dt

    return all_frames


if __name__ == '__main__':
    # get command line arguments
    in_fpath, out_path = parse_arguments()
    # create the output path
    os.makedirs(out_path, exist_ok=True)

    # call the function that returns a list of lines with tab-separated values
    results = extract_audio_rmspower(in_fpath)

    # prepare output path & filename
    in_file = os.path.basename(in_fpath)
    out_file = os.path.splitext(in_file)[0] + '.tsv'
    out_fpath = os.path.join(out_path, out_file)

    # save file
    with open(out_fpath, 'w') as f:
        # write header
        f.write('movie_time\trms\tlr_diff\n')
        # write the value
        for line in results:
            f.write(line + '\n')
