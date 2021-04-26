
from imagehash import phash
from hashlib import md5
from PIL import Image

def hash_frame(arr):
    # crop to exclude the horizontal bars (plus few pixels of
    # safety margin), to enable valid comparison between
    # research cut movie and segment stimuli -- the latter had gray
    # bars
    frame_arr = arr[90:630]
    frame_img = Image.fromarray(frame_arr)
    # solid checksum, susceptible to any sort of noise in the encoding
    # decoding pipeline, but still useful to say what exactly we got
    md5sum = md5(frame_img.tobytes()).hexdigest()
    # perceptual hashing, cares less about negligible differences in
    # the physical image content, but should still reflect any relevant
    # change in the picture (cuts, motion). pHashes can be compared
    # using hamming distance (cumulative bit-wise differences between
    # hashes to quantify the amount of differences)
    # parameters are selected to have a somewhat good trade-off between
    # a reflection of frame-to-frame variability, but also some robustness
    # finding matching frames in reencoded material
    percep_hash = phash(frame_img, hash_size=12, highfreq_factor=4)
    return md5sum, percep_hash
