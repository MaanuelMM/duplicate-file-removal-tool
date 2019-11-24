#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2019/11/19
# Last update:  2019/11/24

import os
import sys
import glob
import json
import filecmp
import hashlib
import argparse

from datetime import datetime


BLOCKSIZE = 65536

hash_file_dict = dict()


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


def hash_calc(filename):
    sha1_hasher = hashlib.sha1()    # enough for file comparison and then filecmp if it is needed
    
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(BLOCKSIZE)
            if not chunk:
                break
            sha1_hasher.update(chunk)

    return sha1_hasher.hexdigest()


def insert_dict(filename):
    hash_file = hash_calc(filename)

    if hash_file not in hash_file_dict:
        hash_file_dict[hash_file] = [[filename]]
    else:
        for file in hash_file_dict[hash_file]:
            if filecmp.cmp(file[0], filename, shallow=False):
                file.append(filename)
                break
        else:
            hash_file_dict[hash_file].append([filename])


def recursive_path_read(path):
    for filename in glob.iglob(path + '**/**', recursive=True):
        if os.path.isfile(filename):
            insert_dict(filename)


def dump_file_list():
    with open('files-' + str(datetime.now()).replace(':', '.') + '.json', 'w', encoding='utf-8') as dump_file:
        json.dump(hash_file_dict, dump_file, indent=4)


def main():
    recursive_path_read(parse_arguments().path)
    dump_file_list()

if __name__ == "__main__":
    main()
