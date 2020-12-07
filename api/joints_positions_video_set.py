import argparse
import glob
import os
from datetime import datetime

from . import blur_video

def cli():
    parser = argparse.ArgumentParser(
        prog='python -m anonymise_video.blur_video_set',
        description=__doc__,
    )

    parser.add_argument('--input-dir',
                        required=True,
                        help='Path to folder of videos to be anonymised.')

    parser.add_argument('--confidence-threshold', type=float, default=0.1,
                        help='Set the threshold needed for a face to be blurred')


    return parser.parse_args()
if __name__ == '__main__':

    args = cli()

    interpretted_args = blur_video.InterprettedBlurVideoArgs(
        key_frequency_hz = 10,
        connection_method = "max",
        confidence_threshold = args.confidence_threshold
    )

    input_videos = glob.glob(
        os.path.join(
            args.input_dir,
            '*.avi'
        )
    )
    
    input_videos += glob.glob(
        os.path.join(
            args.input_dir,
            '*.mov'
        )
    )
    input_videos += glob.glob(
        os.path.join(
            args.input_dir,
            '*.mp4'
        )
    )

    # make an ouput folder on the same level as the input folder
    output_dir = os.path.join(
        args.input_dir,
        '..',
        os.path.basename(args.input_dir)
        + '_blur_'
        + datetime.now().strftime('%Y%m%d%H%M%S')
    )

    os.mkdir(output_dir)
    

    for input_video in input_videos:
        output_video = os.path.join(
            output_dir,
            os.path.basename(input_video)
        )
        blur_video.blur_video( 
            input_video, 
            output_video, 
            interpretted_args 
        ) 

 # .prof for the profiling visualiser
