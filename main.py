#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2019/11/19
# Last update:  2019/12/04

import os
import re
import json
import filecmp
import hashlib
import argparse

from datetime import datetime
from pathlib import Path
from glob import glob
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
    parser = argparse.ArgumentParser(prog='Duplicate File Removal Tool by Manuel M. M.',
                                     usage='\nExecute with [-p PATH] or [--path PATH] to delete all duplicated files inside a path.' +
                                     '\nExecute with [-a] or [--all] if you want to execute the program including hidden files (NOT RECOMMENDED!!).' +
                                     '\nExecute with [-r] or [--root] if the given path is the root of a drive.' +
                                     '\nExecute with [-v] or [--view] if you only need to know how much space you could save.',
                                     description='A Python made script to delete duplicated files from a specified path. Built by own necessity.')
    parser.add_argument('-p', '--path', type=dir_path,
                        required=True, help='path name needed to execute the tool')
    parser.add_argument('-a', '--all', action='store_true',
                        help='if you want to include hidden files (NOT RECOMMENDED!!)')
    parser.add_argument('-r', '--root', action='store_true',
                        help='needed if the given path is the root of a drive')
    parser.add_argument('-v', '--view', action='store_true',
                        help='if you only want to know how much space you could save')

    return parser.parse_args()


def backslash_replacer(path):
    return path.replace('\\', '/')


def path_sanitizer(path):
    if re.search('/$', path):
        return path
    else:
        return path + '/'


def is_same_node(file_1, file_2):
    return os.stat(file_1).st_ino == os.stat(file_2).st_ino


def is_same_file(file_1, file_2):
    return filecmp.cmp(file_1, file_2, shallow=False)


def get_size(file):
    return os.path.getsize(file)


def hash_calc(filename):
    # enough for file comparison and then filecmp if it is needed
    hasher = hashlib.sha1()

    with open(filename, 'rb') as file:
        for chunk in file:
            hasher.update(chunk)

    return hasher.hexdigest()


def insert_dict(filename):
    global estimated_free_space     # must be specified as global due to Python behavior

    hash_file = hash_calc(filename)

    if hash_file not in hash_file_dict:
        hash_file_dict[hash_file] = [[filename]]
    else:
        for file_list in hash_file_dict[hash_file]:
            if is_same_file(file_list[0], filename):
                file_list.append(filename)
                if not is_same_node(file_list[0], filename) and get_size(filename) != 0:
                    estimated_free_space += get_size(filename)
                break
        else:
            hash_file_dict[hash_file].append([filename])


def get_files(path, hidden_files):
    if hidden_files:
        return [backslash_replacer(str(element)) for element in tqdm(list(Path(path).glob('**/*')), desc='Files retrieval') if os.path.isfile(element)]
    else:
        return [backslash_replacer(str(element)) for element in tqdm(glob(path + '**/*', recursive=True), desc='Files retrieval') if os.path.isfile(element)]


def get_filtered_files(path, hidden_files, is_root):
    if is_root:
        return list(filter(lambda x: not re.search(f'^{path}(System Volume Information|\$RECYCLE.BIN)/*', x, re.IGNORECASE), get_files(path, hidden_files)))
    else:
        return get_files(path, hidden_files)


def recursive_hash_calc(path, hidden_files, is_root):
    for filename in tqdm(get_filtered_files(path, hidden_files, is_root), desc='Files comparison'):
        insert_dict(filename)


def dump_file_list(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as dump_file:
        json.dump(hash_file_dict, dump_file, indent=4)


def link_replacer(original_file, duplicate_file):
    os.remove(duplicate_file)
    os.link(original_file, duplicate_file)


def duplicate_file_removal():
    for file_list_list in tqdm(hash_file_dict.values(), desc='Files removal'):
        for file_list in file_list_list:
            first_file = ""
            for file in file_list:
                if not first_file:      # if it's empty ("")
                    if get_size(file) != 0:
                        first_file = file
                    else:
                        break
                elif not is_same_node(first_file, file):
                    link_replacer(first_file, file)


def formatted_data_str(value):
    return (re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(value)) + ' bytes')


def print_estimated_free_space():
    print('Estimated free space after executing the script: ' +
          formatted_data_str(estimated_free_space) + '.')


def main():
    recursive_hash_calc(path_sanitizer(backslash_replacer(
        parse_arguments().path)), parse_arguments().all, parse_arguments().root)
    dump_file_list('logs/files-' + str(datetime.now()).replace(':', '-') + '.json')
    print_estimated_free_space()
    if not parse_arguments().view:
        duplicate_file_removal()


if __name__ == "__main__":
    main()
