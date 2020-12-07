import argparse
import json
import logging
import os
import time

import numpy as np
import matplotlib

import PIL
import torch

import cv2  # pylint: disable=import-error
from openpifpaf import decoder, network, transforms, visualizer, __version__
import openpifpaf as pifpaf

from openpyxl import Workbook

LOG = logging.getLogger(__name__)


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass

# but it really is too-many-statements, I shouldn't have to care about that stuff
def cli():  # pylint: disable=too-many-statements,too-many-branches 
    parser = argparse.ArgumentParser(
        prog='python3 -m openpifpaf.video',
        description=__doc__,
        formatter_class=CustomFormatter,
    )
    parser.add_argument('--version', action='version',
                        version='OpenPifPaf {version}'.format(version=__version__))

    network.cli(parser)
    decoder.cli(parser, force_complete_pose=True, instance_threshold=0.1, seed_threshold=0.5)
    pifpaf.show.cli(parser)

    parser.add_argument('--source', default='0',
                        help='OpenCV source url. Integer for webcams. Supports rtmp streams.')
    parser.add_argument('--video-output', default=None, nargs='?', const=True,
                        help='video with drawn skeleton output file')
    parser.add_argument('--start-frame', type=int, default=0)
    parser.add_argument('--skip-frames', type=int, default=1)
    parser.add_argument('--key-frequency-hz', type=int, default=10)
    parser.add_argument('--max-frames', type=int)
    # Set the threshold for something
    # parser.add_argument('--confidence-threshold', type=float, default=0.1,
    #                     help='Set the threshold needed for a face to be blurred')
    group = parser.add_argument_group('logging')
    group.add_argument('-q', '--quiet', default=False, action='store_true',
                       help='only show warning messages or above')
    group.add_argument('--debug', default=False, action='store_true',
                       help='print debug messages')
    args = parser.parse_args()

    return args

class ProcessingVideoArgs:
    def __init__(
        self,
        checkpoint=None,
        basenet=None,
        headnets=None,
        pretrained=True,
        two_scale=False,
        multi_scale=False,
        multi_scale_hflip=True,
        cross_talk=0.0,
        download_progress=True,
        head_dropout=0.0,
        head_quad=1,
        seed_threshold=0.5,
        instance_threshold=0.1,
        keypoint_threshold=None,
        decoder_workers=None,
        dense_connections=False,
        dense_coupling=0.01,
        caf_seeds=False,
        force_complete_pose=True,
        profile_decoder=None,
        cif_th=0.1,
        caf_th=0.1,
        connection_method="blend",
        greedy=False,
        video_output="",
        xls_output="",
        quiet=False,
        debug=False,
        skip_frames=1,
        max_frames=False,
        start_frame=0,
        confidence_threshold=0.1
    ):

        self.checkpoint = checkpoint
        self.basenet = basenet
        self.headnets = headnets
        self.pretrained = pretrained
        self.two_scale = two_scale
        self.multi_scale = multi_scale
        self.multi_scale_hflip = multi_scale_hflip
        self.cross_talk = cross_talk
        self.download_progress = download_progress
        self.head_dropout = head_dropout
        self.head_quad = head_quad
        self.seed_threshold = seed_threshold
        self.instance_threshold = instance_threshold
        self.keypoint_threshold = keypoint_threshold
        self.decoder_workers = decoder_workers
        self.dense_connections = dense_connections
        self.dense_coupling = dense_coupling
        self.caf_seeds = caf_seeds
        self.force_complete_pose = force_complete_pose
        self.profile_decoder = profile_decoder
        self.cif_th = cif_th
        self.caf_th = caf_th
        self.connection_method = connection_method
        self.greedy = greedy
        self.quiet = quiet
        self.debug = debug
        self.skip_frames = skip_frames
        self.max_frames = max_frames
        self.start_frame = start_frame
        self.confidence_threshold = confidence_threshold
        class InternalConfig:
            def __init__(self):
                self.debug_cifhr = None
                self.debug_cif_c = None
                self.debug_cif_v = None
                self.debug_cifdet_c = None
                self.debug_cifdet_v = None
                self.debug_caf_c = None
                self.debug_caf_v = None
                self.debug_indices = []
                self.debug_images = False
                self.show_box=False,
                self.show_joint_scales=False,
                self.show_decoding_order=False,
                self.show_frontier_order=False,
                self.show_only_decoded_connections=False,
                self.show_joint_confidences=False,

        # configure logging
        self.log_level = logging.INFO
        if quiet:
            self.log_level = logging.WARNING
        if debug:
            self.log_level = logging.DEBUG
        logging.basicConfig()
        logging.getLogger('openpifpaf').setLevel(self.log_level)
        LOG.setLevel(self.log_level)

        internal_config = InternalConfig()
        network.configure(self)
        pifpaf.show.configure(internal_config)
        visualizer.configure(internal_config)
        # pifpaf.show.AnimationFrame.video_fps = self.video_fps

        # add args.device
        self.device = torch.device('cpu')
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        LOG.debug('neural network device: %s', self.device)

        self.model, _ = network.factory_from_args(self)
        self.model = self.model.to(self.device)
        self.processor = decoder.factory_from_args(self, self.model)

def keypoint_painter_factory():
    keypoint_painter = pifpaf.show.KeypointPainter(color_connections=True, linewidth=4)
    # Patch to ensure that only the keypoints we want are drawn
    # todo: Source of this bug?
    keypoint_painter.show_joint_confidences = False
    keypoint_painter.show_joint_scales = False
    keypoint_painter.show_frontier_order = False
    keypoint_painter.show_joint_scales = False
    keypoint_painter.show_joint_confidences = False
    keypoint_painter.show_box = False
    keypoint_painter.show_decoding_order = False
    return keypoint_painter

def get_column_names(keypoint_names):
    column_names = []
    for name in keypoint_names:
        for postfix in ["x", "y", "confidence"]:
            column_names.append(name + "_" + postfix)
    return column_names

def flatten_keypoints_matrix(keypoint_matrix):
    data_row = []
    for position in keypoint_matrix:
        for point in position:
            data_row.append(point)
    return data_row

def process_video(
    source,
    video_output,
    xls_output,
    args
):
    keypoint_painter = keypoint_painter_factory()
        
    animation = pifpaf.show.AnimationFrame(
        show=False,
        video_output=video_output
    )

    # Set up input and output
    capture = cv2.VideoCapture(source)    
    
    # Used to report processing time per frame
    last_loop = time.time()

    workbook = Workbook()

    sheet = workbook.active

    first_frame = True

    for frame_i, (ax, _) in enumerate(animation.iter()):
        _, image = capture.read()

        # Determine if we will process this frame
        if image is None:
            LOG.info('no more images captured')
            break

        if frame_i < args.start_frame:
            animation.skip_frame()
            continue

        if args.max_frames and frame_i >= args.start_frame + args.max_frames:
            break

        if frame_i % args.skip_frames != 0:
            animation.skip_frame()
            continue

        image_pifpaf = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        def get_resize_pow2(max_allowed, image_dims):
            max_dim = max(image_dims[0], image_dims[1])
            # find x: max_allowed > max_dim / ( 2 ^ x)
            x = np.log2(max_dim/max_allowed)
            return 2 ** x


        image_rescale = get_resize_pow2(
            max_allowed = 1280,
            image_dims = image_pifpaf.shape
        )
        # with image_descale as 
        image_pifpaf = cv2.resize(
            image_pifpaf, 
            (0,0), 
            fx = 1 / image_rescale,
            fy = 1 / image_rescale
        )
            

        start = time.time()
        image_pil = PIL.Image.fromarray(image_pifpaf)
        processed_image, _, __ = transforms.EVAL_TRANSFORM(image_pil, [], None)
        LOG.debug('preprocessing time %.3fs', time.time() - start)

        preds = args.processor.batch(args.model, torch.unsqueeze(processed_image, 0), device=args.device)[0]

        if first_frame:
            sheet.append(get_column_names(preds[0].keypoints))
            ax, _ = animation.frame_init(image)
            keypoint_painter.xy_scale = image_rescale
            first_frame = False
            
        
        sheet.append(flatten_keypoints_matrix(preds[0].data))

        image_color_corrected = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ax.imshow(image_color_corrected) 
        keypoint_painter.annotations(ax, preds)

        current_time = time.time()
        elapsed_time = current_time - last_loop
        if(elapsed_time == 0):
            processed_fps = 1000
        else:
            processed_fps = 1.0 / elapsed_time

        LOG.info(
            'frame %d, loop time = %.3fs, processed FPS = %.3f',
            frame_i,
            elapsed_time,
            processed_fps
        )
        last_loop = current_time

    workbook.save(xls_output)
