#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2019/11/19
# Last update:  2019/11/19

import os
import sys
import glob
import filecmp
import hashlib
import argparse

from pathlib import Path


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path")


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Duplicate File Removal Tool by Manuel M. M.', usage='Execute with [-p PATH] or [--path PATH] to delete all duplicated files inside a path.',
                                     description='A Python made script to delete duplicated files from a specified path. Built by own necessity.')
    parser.add_argument('-p', '--path', type=dir_path,
                        required=True, help='path name needed to execute the tool')

    return parser.parse_args()


def main():
    parsed_args = parse_arguments()
    print(parsed_args)


if __name__ == "__main__":
    main()
