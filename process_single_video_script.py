from api.video_joints_positions import ProcessingVideoArgs
from api.video_joints_positions import process_video

extra_args = ProcessingVideoArgs(max_frames=50)

source = "C:\\Users\\STIMO2-Admin\\data\\DSCF1240_stim-off.mp4"
dest = "C:\\Users\\STIMO2-Admin\\data\\DSCF1240_stim-off_skeleton.mp4"

process_video(source, dest, extra_args)
