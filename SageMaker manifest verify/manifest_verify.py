import json
import pprint

with open('.\\train\\output.manifest', 'r') as f:
    manifest_list = [json.loads(line.strip()) for line in f.readlines()]

for manifest in manifest_list:
    try:
        manifest["source-ref"]
        for list in manifest["BB"]["annotations"]:
            list["left"]
            list["top"]
            list["width"]
            list["height"]
            list["class_id"]
        for list in manifest["BB"]["image_size"]:
            list["width"]
            list["height"]
            list["depth"]

        manifest["BB-metadata"]["job-name"]
        manifest["BB-metadata"]["class-map"]
        manifest["BB-metadata"]["human-annotated"]
        for list in manifest["BB-metadata"]["objects"]:
            list["confidence"]
        manifest["BB-metadata"]["creation-date"]
        manifest["BB-metadata"]["type"]
    except:
        pprint.pprint(manifest)



