from api.video_joints_positions import ProcessingVideoArgs
from api.video_joints_positions import process_video

import glob
import os
from datetime import datetime

input_dir = r'C:\Users\STIMO2-Admin\data\PDC_010_20160405_Problematic'

video_inputs = glob.glob(
    os.path.join(
        input_dir,
        '*.avi'
    )
)

output_dir = os.path.join(
    input_dir,
    '..',
    os.path.basename(input_dir)
    + '_tracked_'
    + datetime.now().strftime('%Y%m%d%H%M%S')
)

os.mkdir(output_dir)

extra_args = ProcessingVideoArgs()

for video_input in video_inputs:
    basename = os.path.basename(video_input).split(".")[0]
    video_output = os.path.join(
        output_dir,
        basename + "_skeleton.avi"
    )
    xls_output = os.path.join(
        output_dir,
        basename + "_skeleton.xlsx"
    )
    process_video(video_input, video_output, xls_output, extra_args)
