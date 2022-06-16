#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tool for converting panoptic GT into semantic segmentation uint8 pngs and/or instance segmentation uint16 pngs
# see https://github.com/ozendelait/wilddash_scripts
# by Oliver Zendel and Bernhard Rainer, AIT Austrian Institute of Technology GmbH
#
# Use this tool on your own risk!
# Copyright (C) 2022 AIT Austrian Institute of Technology GmbH
# All rights reserved.
#******************************************************************************

import cv2
import numpy as np
import os
import sys
import glob
import json
import argparse

def tqdm_none(l, total=None):
    return l
try:
    from tqdm import tqdm as tqdm_con
    from tqdm.notebook import tqdm as tqdm_nb
except:
    #install/update tqdm needed
    tqdm_con = tqdm_nb = tqdm_none

def bgrids_to_intids(orig_mask_bgr):
    return  orig_mask_bgr[:, :, 0].astype(np.uint32) * 65536 + \
            orig_mask_bgr[:, :, 1].astype(np.uint32) * 256 + \
            orig_mask_bgr[:, :, 2].astype(np.uint32)

def panoptic2segm(json_path, outp_dir_sem=None, outp_dir_inst=None, label_png_dir=None, tqdm_vers=tqdm_nb):
    #default: masks are in a directory with the same name as the panoptic json filename
    if label_png_dir is None: label_png_dir = json_path[:json_path.rfind('.')]
    pano0 = json.load(open(json_path))
    id2image = {image["id"]: image for image in pano0["images"]}
    is_thing = {cat["id"]: cat["isthing"] for cat in pano0["categories"]}
    if outp_dir_sem and not os.path.exists(outp_dir_sem): os.makedirs(outp_dir_sem)
    if outp_dir_inst and not os.path.exists(outp_dir_inst): os.makedirs(outp_dir_inst)
    cnt_success = 0
    for a in tqdm_vers(pano0["annotations"]): 
        image_id = a["image_id"]
        if image_id in id2image: 
            ids_path = label_png_dir+'/'+ a["file_name"]
            bgr_labels = cv2.imread(ids_path)
            ids = bgrids_to_intids(np.asarray(bgr_labels))
            semantic = np.zeros_like(ids, dtype="uint8")
            instances = np.zeros_like(ids, dtype="uint16")
            num_things = 1
            for s in a["segments_info"]: 
                id0 = s["id"]
                category_id = s["category_id"]
                semantic[ids == id0] = category_id
                if is_thing[category_id]: 
                    instances[ids == id0] = category_id * 1000 + num_things
                    num_things += 1
                else: 
                    instances[ids == id0] = category_id
            if outp_dir_sem:
                semantic_name = id2image[image_id]["file_name"].replace(".jpg", "_labelIds.png")
                cv2.imwrite(outp_dir_sem+'/'+semantic_name, semantic)
            if outp_dir_inst:
                instance_name = semantic_name.replace("_labelIds.png", "_instanceIds.png")
                cv2.imwrite(outp_dir_inst+'/'+instance_name, instances)
            cnt_success += 1
    return cnt_success
    
def pano2sem_main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_path', type=str, default="panoptic.json",
                        help="Path to panoptic COCO json")
    parser.add_argument('--outp_dir_sem', type=str, default=None,
                        help="Target directory for semantic uint8 pngs")
    parser.add_argument('--outp_dir_inst', type=str, default=None,
                        help="Target directory for instance uint16 pngs")
    parser.add_argument('--label_png_dir', type=str, default=None,
                        help="Specify directory of panoptic COCO png BGR masks (default: use json_path as hint)")
    parser.add_argument('--silent', action='store_true', help="Suppress all outputs")
    parser.add_argument('--verbose', action='store_true', help="Print extra information")
    args = parser.parse_args(argv)
    if not args.outp_dir_sem and not args.outp_dir_inst:
        if not args.silent:
            print("Error: no output operation selected.")
        return -1
    tqdm_vers = tqdm_none if args.silent else tqdm_con
    cnt_success = panoptic2segm(json_path=args.json_path, outp_dir_sem=args.outp_dir_sem, outp_dir_inst=args.outp_dir_inst, label_png_dir=args.label_png_dir, tqdm_vers=tqdm_vers)
    if not args.silent:
        print("Finished converting panoptic COCO GT with %i successes."%(success_cnt))

if __name__ == "__main__":
    sys.exit(pano2sem_main())