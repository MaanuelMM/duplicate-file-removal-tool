#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2019/11/19
# Last update:  2019/11/29

import os
import re
import sys
import glob
import json
import shutil
import filecmp
import hashlib
import argparse

from datetime import datetime
from tqdm import tqdm


hash_file_dict = dict()

estimated_free_space = 0


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


def is_same_node(file_1, file_2):
    return os.stat(file_1).st_ino == os.stat(file_2).st_ino


def is_same_file(file_1, file_2):
    return filecmp.cmp(file_1, file_2, shallow=False)


def get_size(file):
    return os.path.getsize(file)


def hash_calc(filename):
    # enough for file comparison and then filecmp if it is needed
    sha1_hasher = hashlib.sha1()

    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(sha1_hasher.block_size)
            if not chunk:
                break
            sha1_hasher.update(chunk)

    return sha1_hasher.hexdigest()


def insert_dict(filename):
    global estimated_free_space     # must be specified as global due to Python behavior

    hash_file = hash_calc(filename)

    if hash_file not in hash_file_dict:
        hash_file_dict[hash_file] = [[filename]]
    else:
        for file in hash_file_dict[hash_file]:
            if is_same_file(file[0], filename):
                file.append(filename)
                if not is_same_node(file[0], filename) and get_size(filename) != 0:
                    estimated_free_space += get_size(filename)
                break
        else:
            hash_file_dict[hash_file].append([filename])


def get_files(path):
    return [element for element in tqdm(glob.glob(path + '**/*', recursive=True), desc='Files retrieval') if os.path.isfile(element)]


def recursive_hash_calc(path):
    for filename in tqdm(get_files(path), desc='Files comparison'):
        insert_dict(filename)


def dump_file_list():
    with open('files-' + str(datetime.now()).replace(':', '.') + '.json', 'w', encoding='utf-8') as dump_file:
        json.dump(hash_file_dict, dump_file, indent=4)


def link_replacer(original_file, duplicated_file):
    os.link(original_file, duplicated_file)


def duplicate_file_removal():
    for file_list_list in hash_file_dict.values():
        for file_list in file_list_list:
            first_file = ""
            for file in file_list:
                if not first_file:      # if is empty ("")
                    if get_size(file) != 0:
                        first_file = file
                    else:
                        break
                elif not is_same_node(first_file, file):
                    os.remove(file)
                    link_replacer(first_file, file)


def formatted_data_str(value):
    return (re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(value)) + ' bytes')


def print_estimated_free_space():
    print('Estimated free space after executing the script: ' +
          formatted_data_str(estimated_free_space) + '.')


def main():
    recursive_hash_calc(parse_arguments().path)
    dump_file_list()
    print_estimated_free_space()
    duplicate_file_removal()


if __name__ == "__main__":
    main()
