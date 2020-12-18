OpenPifPaf API
=====================
The goal of this software is to have a usable version of OpenPifPaf, which requires no interaction with the commandline

Environment to build openpifpaf
--------------------------
OpenPifPaf was developed for MacOS, but this project shall run on windows and as such the required dependencies to build on windows are documented.

### Git
It is assumed git is installed to the path of your machine. (how did you get this repo otherwise?) Certain pip installs further down the line will fail if it isn't.

### Visual Studio
Visual Studio 2019 community edition was downloaded and installed from https://visualstudio.microsoft.com. In the installer select

    individual component - MSVC v140 - VS 2015 C++ build tools (v14.00)

If visual studio is already installed, you can open the installer to modify your installation and add this component.

### Python
We chose to use version 3.6.7 of python in its own virtual environment. This is the python version which Katia notes as necessary to run the 3D camera recording app which she used in her minor project. It can be downloaded and installed from https://www.python.org/downloads/release/python-367/ , we chose the Windows x86-64 executable installer. Run the executable, note the location of the installation of python, in this instance it was C:\Users\harte\AppData\Local\Programs\Python\Python36. **Do not select** "Add Python 3.6 to PATH". Select Install Now. We also installed the latest python **selecting** "Add Python 3.8 to PATH" for our convenience. This is to be avoided on machines that you do not own.

Open powershell in the repository folder to create a virtual environment for this project. Virtualenv installs with its own gitignore, which is good, we don't want virtual environments in the repository.

    python -m pip install --upgrade pip
    pip install virtualenv
    virtualenv project_python_env -p C:\Users\your_username\AppData\Local\Programs\Python\Python36\python.exe
    Set-ExecutionPolicy Unrestricted
    .\project_python_env\Scripts\activate.ps1
    python -m pip install --upgrade pip
	pip install numpy cython
	pip install torch===1.5.0 torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
    pip install opencv-python
	pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"
    pip install matplotlib
    pip install openpifpaf===0.11.5
    pip install openpyxl

To confirm that the installation was successful close the powershell, open a new one, set up the virtual env again, and run the example given in openpifpaf's README.md

    .\path\to\python_env\project_python_env\Scripts\activate.ps1
    cd C:\path\to\this\repo\anonymise_video\openpifpaf
    python -m openpifpaf.predict --show docs/coco/000000081988.jpg

### Important Patch
For the tracked output video, we use OpenPifPaf's own video export. Unfortunately the writer class has frame rate set to a constant of 10Hz.
It is necessary to edit the constructor of AnimationFrame in ```openpifpaf\show\animation_frame.py``` to allow this to be set to the correct frequency of the input video. Code below

class AnimationFrame:
    video_fps = 10
    video_dpi = 100

    def __init__(self, *,
                 fig_width=8.0,
                 fig_init_args=None,
                 show=False,
                 video_output=None,
                 second_visual=False,
                 video_fps=10):
        self.video_fps = video_fps
        self.fig_width = fig_width
        self.fig_init_args = fig_init_args or {}
        self.show = show
        self.video_output = video_output
        self.video_writer = None
        if self.video_output:
            self.video_writer = matplotlib.animation.writers['ffmpeg'](fps=self.video_fps)



### CUDA
If you have a CUDA compatible GPU, install CUDA from https://developer.nvidia.com/cuda-downloads to accelerate the openpifpaf processing. You can verify that the installation was successful by navigating to the powershell, running python, and querying

	.\project_python_env\Scripts\activate.ps1
	python
	import torch
	torch.cuda.is_available()

### Visual Studio Code
Finally we use visual studio code as a development and debugging environment, downloaded from here https://code.visualstudio.com/Download. It is chosen for its simple transparent open source design, where all configuration can be acheived through .json files. The args variable of anonymise_video.blur_video configuration in launch.json should be edited to include a path to an input folder present on the developers laptop, for example:

	"-i", "..\\..\\data\\cathal_bobbing",

The filestructure seen above is suggested, if you have a repo folder with all git repositories in it, on the same level you could have a data folder with all the data you might need for development in it.

```text
username
├── repo
│   ├── repo1
│	├── repo2
│	└── etc
└── data
    ├── data1
 	├── data2
 	└── etc
```
The settings.json file should already point to the python virtual environment you have created, if you have created the correct folder in the correct place.

### SnakeVis
There now exists a profiling script to determine bottlenecks. Simply launch it with ```python profile_blur.py```. Use snakeVis to view the output file generated by the profiling script. Note: as of 17.06.2020, the pip install appears broken, but you can still manually download and install the wheel from https://pypi.org/project/snakeviz/#files .

    pip install snakevis
    # or
    pip install snakeviz-2.1.0-py2.py3-none-any.whl

### Animotica
OpenPifPaf isn't really designed for videos, as such it doesn't consistently index the skeletons. A simple free tool to crop out physiotherapists is animotica, which can be downloaded from the microsoft store. It

Inputs and Outputs
------------------
It is recommended to write scripts to interact with this library. An example of such is ```process_folder_script.py```. This avoids losing config info to the command line history.