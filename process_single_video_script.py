from api.video_joints_positions import ProcessingVideoArgs
from api.video_joints_positions import process_video


source = "C:\\Users\\STIMO2-Admin\\data\\DSCF1240_stim-off.mp4"
video_output = "C:\\Users\\STIMO2-Admin\\data\\DSCF1240_stim-off_skeleton.mp4"
xls_output = "C:\\Users\\STIMO2-Admin\\data\\DSCF1240_stim-off_skeleton.xls"

extra_args = ProcessingVideoArgs()
process_video(source, video_output, xls_output, extra_args)
