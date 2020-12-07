from . import blur_video
import json

if __name__ == '__main__':
    args = blur_video.cli()

    with open('cli_printout.txt', 'w') as file:
        for key, value in (args.__dict__).items() :
            file.write(key + '\n')
            if(value == None):
                file.write('-------' + 'None\n')
            else:
                file.write('--------' + str(value) + '\n')
