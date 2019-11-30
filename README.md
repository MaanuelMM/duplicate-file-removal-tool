# duplicate-file-removal-tool
A Python made program to remove duplicate files and replace them with hard links.

## Requirements
Python 3.8 or newer it is necessary to execute this program. In addition, it is necessary to install the packages contained in the ``requirements.txt`` file.

## Usage
Open a terminal session in the ``main.py`` path and execute the program with these [optional] parameters:
```
python main.py (-p|--path) PATH (-r|--root)* (-v|--view)*
```

### Parameters explanation
- ``-p OR --path``. It is mandatory to use this parameter to specify the path in which the program will be executed.
- ``-r OR --root``. Must be specified if the given path is the root of a device. The reason is that the program will exclude the 'System Volume Information' folder and its content usually found on Windows filesystems.
- ``-v OR --view``. An optional parameter to only estimate the freeable space without deleting duplicate files.