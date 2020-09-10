import json
import os
import numpy as np
import pprint
import pandas as pd


FILE_PATH_IN_ORIGINAL_FOLDER = "train.manifest"




def read_manifest_file(file_path):
    with open(file_path, 'r') as f:
        output = [json.loads(line.strip()) for line in f.readlines()]
        return output

def train_validation_split(labels, split_factor=0.8):
    np.random.shuffle(labels)

    dataset_size = len(labels)
    train_test_split_index = round(dataset_size*split_factor)

    train_data = labels[:train_test_split_index]
    validation_data = labels[train_test_split_index:]
    return train_data, validation_data

manifest_list = read_manifest_file(os.path.join(os.getcwd(), "원본\\" + FILE_PATH_IN_ORIGINAL_FOLDER))
new_manifest_list = []
class_list = []

for manifest in manifest_list:
    key_list = list(manifest.keys())
    manifest['BB'] = manifest[key_list[1]]
    manifest['BB-metadata'] = manifest[key_list[2]]
    del manifest[key_list[1]]
    del manifest[key_list[2]]
    new_manifest_list.append(manifest)
    class_list.append(manifest['source-ref'].split('/')[4])

class_list = list(set(class_list))
split_manifest_list = {key:[] for key in class_list}

for manifest in new_manifest_list:
    split_manifest_list[manifest['source-ref'].split('/')[4]].append(manifest)



for class_name in class_list:

    trainset, testset = train_validation_split(split_manifest_list[class_name], 0.8)

    with open(os.path.join(os.getcwd(), "수정본\\train\\output.manifest"), 'a') as f:
        for line in trainset:
            f.write(json.dumps(line))
            f.write('\n')

    with open(os.path.join(os.getcwd(), "수정본\\validation\\output.manifest"), 'a') as f:
        for line in testset:
            f.write(json.dumps(line))
            f.write('\n')