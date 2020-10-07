import json
import copy


def read_manifest_file(file_path):
    with open(file_path, 'r') as f:
        output = [json.loads(line.strip()) for line in f.readlines()]
        for line in f.readlines():
            print(line)
        return output

manifest_file_name = 

correct_classmap =
correct_classmap_reverse =

manifest_list = read_manifest_file(".\\"+manifest_file_name)
new_manifest_list = []
for manifest in manifest_list:
    original_classmap = manifest['BB-metadata']['class-map']

    new_annotation = []
    for annotation in manifest['BB']['annotations']:
        annotation['class_id'] = correct_classmap_reverse[original_classmap[str(annotation['class_id'])]]
        new_annotation.append(copy.deepcopy(annotation))

    manifest['BB']['annotations'] = new_annotation
    manifest['BB-metadata']['class-map'] = correct_classmap
    new_manifest_list.append(copy.deepcopy(manifest))

with open("..\\클래스맵정정\\"+manifest_file_name, "w") as f:
    for manifest in new_manifest_list:
        f.write(json.dumps(manifest))
        f.write('\n')
