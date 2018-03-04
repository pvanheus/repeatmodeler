#!/usr/bin/python

from __future__ import print_function, division
import sys
import json
import subprocess
import os
import hashlib

# {"param_dict": {"__datatypes_config__": "/home/pvh/Documents/code/Masters/galaxy/database/jobs_directory/000/9/registry.xml", "GALAXY_DATA_INDEX_DIR": "/home/pvh/Documents/code/Masters/galaxy/tool-data", "userId": "1", "userEmail": "pvh@sanbi.ac.za", "dbke
# y": "?", "__get_data_table_entry__": "", "__admin_users__": "pvh@sanbi.ac.za", "input_fasta": "/home/pvh/Documents/code/Masters/galaxy/database/files/000/dataset_1.dat", "__user__": "galaxy.model:SafeStringW
# rapper(galaxy.model.User:,,,,,,,)", "input": "__lt__function input at 0x7fb3b424c050__gt__", "__app__": "galaxy.app:UniverseApplication", "__user_email__": "pvh@sanbi.ac.za", "GALAXY_DATATYPES_CONF_FILE": "/home/pvh/Documents/code/Masters/galaxy/database/jobs_directory/000/9/registry.
# xml", "__user_name__": "pvanheus", "__tool_directory__": "/home/pvh/Documents/code/Masters/galaxy/tools/data_manager/repeatmodeler", "__new_file_path__": "/home/pvh/Documents/code/Masters/galaxy/database/tmp", "__user_id__": "1", "out_file": "/home/pvh/Doc
#
#     #for $input_count, $input_dataset in enumerate($genome_fasta)
#       echo $input_dataset >> input_data.txt &&
#     #end for
#     BuildDatabase -engine ncbi -name repeatmodeler -batch input_data.txt &&
#     if [ ! -d '$output_db.extra_files_path' ] ; then mkdir '$output_db.extra_files_path' ; fi &&
#     mv repeatmodeler.* '$output_db.extra_files_path'
#


def GetHashofDirs(directory, chunksize=2**20):
    """GetHashofDirs - computes SHA256 hash for directory and its contents
    # from: https://stackoverflow.com/questions/24937495/how-can-i-calculate-a-hash-for-a-filesystem-directory-using-python

    Params:
    directory - directory name
    chunksize - size of chunk to read from files. default is 1 MB
    returns - a string with the hash of the files in the directory"""
    hash = hashlib.sha256()
    if not os.path.exists(directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in sorted(files):
                filepath = os.path.join(root, names)
            try:
                f1 = open(filepath, 'rb')
            except:
                # You can't open the file for some reason
                f1.close()
                continue

            while True:
                # Read file in as little chunks
                buf = f1.read(chunksize)
                if not buf:
                    break
                hash.update(hashlib.sha256(buf).hexdigest())
            f1.close()
    except:
        return -2

    return hash.hexdigest()


def valid_filename(name):
    """valid_filename - checks that the filename only contains
                        numbers, letters or '.', '_' and '-'.

    Params:
    name - str - filename to check
    returns True for valid filenames else False"""
    valid = True
    for char in name:
        if not char.isalnum() and char not in '._-':
            valid = False
            break
    return valid


json_filename = sys.argv[1]


with open(json_filename) as json_file:
    data = json.load(json_file)
    db_name = data['param_dict']['repeatmodeler_db_name'].strip()
    if not valid_filename(db_name):
        print("DB name ({}) is not a valid filename", file=sys.stderr)
        exit(1)
    db_description = data['param_dict']['db_description'].strip()
    fasta_input_filenames = data['param_dict']['input_fasta']
    if type(fasta_input_filenames) is not list:
        fasta_input_filenames = [fasta_input_filenames]
    # output path is extra_files_path of first and only output
    output_path = data['output_data'][0]['extra_files_path']
    os.mkdir(output_path)
    batch_input_filename = os.path.join(output_path, 'input_data.txt')
    with open(batch_input_filename, 'w') as inputs_file:
        for filename in fasta_input_filenames:
            print(filename, file=inputs_file)

    cmd = ["BuildDatabase", "-engine", "ncbi", "-name", db_name,
           "-batch", batch_input_filename]
    subprocess.check_call(cmd, cwd=output_path)
    os.unlink(batch_input_filename)

db_id = '{}_{}'.format(db_name, GetHashofDirs(output_path))
db_path = os.path.join(db_id, db_name)
if db_description.strip() == '':
    db_description = db_name
output_entry = dict(value=db_id, db_name=db_name,
                    description=db_description, path=db_path)
data_manager_dict = dict(data_tables=dict(repeatmodeler_db=[output_entry]))
with open('/tmp/out_file1.json', 'w') as output_file:
    json.dump(data_manager_dict, output_file)
with open(json_filename, 'w') as output_file:
    json.dump(data_manager_dict, output_file)
