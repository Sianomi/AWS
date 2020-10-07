import json
import os
import numpy as np
import imgaug as ia
import imgaug.augmenters as iaa
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import copy

multiple = {

}

font = ImageFont.truetype("arial.ttf", 50)

master_path = 
save_path =

split_manifest_path = os.path.join(os.getcwd(), "분류된manifest")
manifest_file_list = os.listdir(split_manifest_path)
# manifest_file_list = ['siteOne.manifest', 'siteTwo.manifest']
sometimes = lambda aug: iaa.Sometimes(0.5, aug)

seq = iaa.Sequential(
    [
        # apply the following augmenters to most images
        iaa.Fliplr(0.5),  # horizontally flip 50% of all images
        iaa.Flipud(0.2),  # vertically flip 20% of all images
        # crop images by -5% to 10% of their height/width
        sometimes(iaa.CropAndPad(
            percent=(-0.05, 0.1),
            pad_mode=ia.ALL,
            pad_cval=(0, 255)
        )),
        sometimes(iaa.Affine(
            scale={"x": (0.9, 1.1), "y": (0.9, 1.1)},  # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},  # translate by -20 to +20 percent (per axis)
            rotate=(-15, 15),  # rotate by -45 to +45 degrees
            shear=(-8, 8),  # shear by -16 to +16 degrees
            order=[0],  # use nearest neighbour or bilinear interpolation (fast)
            cval=(0, 255),  # if mode is constant, use a cval between 0 and 255
            mode='edge'  # use any of scikit-image's warping modes (see 2nd image from the top for examples)
        )),
    ],
    random_order=True
)


for manifest_file in manifest_file_list:
    count = 0
    new_manifest_list = []

    with open(os.path.join(split_manifest_path, manifest_file), "r") as f:
        manifest_list = [json.loads(line.strip()) for line in f.readlines()]

    class_name = os.path.splitext(manifest_file)[0]
    class_path = os.path.join(master_path, class_name)

    if not os.path.isdir(os.path.join(save_path, class_name)):
        os.mkdir(os.path.join(save_path, class_name))
    if not os.path.isdir(os.path.join(save_path, class_name + " view")):
        os.mkdir(os.path.join(save_path, class_name + " view"))

    for manifest in manifest_list:
        file_name = os.path.split(manifest["source-ref"])[1]
        file_path = os.path.join(class_path, file_name)
        image = np.array(Image.open(file_path))
        image = image.reshape((1,) + image.shape)

        bbs = []
        for annotation in manifest["BB"]["annotations"]:
            x1 = annotation["left"]
            y1 = annotation["top"]
            x2 = x1 + annotation["width"]
            y2 = y1 + annotation["height"]
            bbs.append(ia.BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2, label=annotation["class_id"]))

        for i in range(multiple[class_name]):
            new_file_name = os.path.splitext(file_name)[0] + "_" + str(i) + ".jpg"

            images_aug, bbs_aug_list = seq(images=image, bounding_boxes=bbs)
            images_aug = Image.fromarray(images_aug.squeeze(axis=0))
            images_aug.save(os.path.join(os.path.join(save_path, class_name), new_file_name), "JPEG")
            draw = ImageDraw.Draw(images_aug)

            new_annotations_list = []
            for bbs_aug in bbs_aug_list:
                x1_aug = int(bbs_aug.x1)
                y1_aug = int(bbs_aug.y1)
                x2_aug = int(bbs_aug.x2)
                y2_aug = int(bbs_aug.y2)

                annotation["left"] = x1_aug
                annotation["top"] = y1_aug
                annotation["width"] = x2_aug - x1_aug
                annotation["height"] = y2_aug - y1_aug
                annotation["class_id"] = bbs_aug.label
                new_annotations_list.append(copy.deepcopy(annotation))

                draw.rectangle(((x1_aug, y1_aug), (x2_aug, y2_aug)), outline='red', width=5)
                draw.text([x1_aug, int(y1_aug + (y2_aug - y1_aug) / 3)], str(bbs_aug.label), font=font)

            images_aug.save(os.path.join(os.path.join(save_path, class_name + " view"), new_file_name), "JPEG")
            manifest["source-ref"] = "s3://ksa-mgt-proj/dev-aug2/" + class_name + "/" + new_file_name
            manifest["BB"]["annotations"] = new_annotations_list
            new_manifest_list.append(copy.deepcopy(manifest))
            count = count + 1
            if count % 100 == 0:
                print(class_name + " : " + str(count))

    with open(os.path.join(save_path, class_name+".manifest"), 'a') as f:
        for manifest in new_manifest_list:
            f.write(json.dumps(manifest))
            f.write('\n')
