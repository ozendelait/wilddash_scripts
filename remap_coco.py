#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tool for remapping panoptic COCO json files
# see https://github.com/ozendelait/wilddash_scripts
# by Oliver Zendel, AIT Austrian Institute of Technology GmbH based on 
# https://github.com/ozendelait/rvc_devkit/blob/master/common/remap_coco.py
#
# Use this tool on your own risk!
# Copyright (C) 2023 AIT Austrian Institute of Technology GmbH
# All rights reserved.
#******************************************************************************

import os
import sys
import argparse
import shutil
import json
import cv2
from pano2sem import bgrids_to_intids, intids_to_bgrids, tqdm_none, tqdm_nb, tqdm_con

def to_abspath(p):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(p)))

# Remap single annotation entry from COCO panoptic format json inplace
# combine labels with optinal correction for iscrowd flags 
# src_is_thing/trg_is_thing: 
#     trgid in trg_is_thing:0 -> trg is a stuff label; combine potentially multiple category labels into one
#     trgid in trg_is_thing:1 and srcid in src_is_thing:0 -> trg is a thing and src was stuff label (-> set s['iscrowd'] to 1)
# supply src_dir and trg_dir to allow joining of the same trg stuff labels by loading/saving masks
def remap_annotation(annot, src_to_trg, src_is_thing={}, trg_is_thing={}, src_dir=None, trg_dir=None, void_id=-1):
    join_annots = {}
    ret_annot, existing_ids = [], set()
    do_calc_masks = not src_dir is None and not trg_dir is None
    for s in annot['segments_info']:
        trg_cat = int(src_to_trg.get(s['category_id'],void_id))
        src_wasathing = src_is_thing.get(s['category_id'],-1)
        trg_isathing = trg_is_thing.get(trg_cat,-1)
        s['category_id'] = trg_cat
        if do_calc_masks and trg_isathing == 0:
            join_annots.setdefault(trg_cat,[]).append(s)
            continue
        if src_wasathing == 0 and trg_isathing == 1:
            s['iscrowd'] = 1 #set iscrowd to indicated potential multitude of instances
        existing_ids.add(s['id'])
        ret_annot.append(s)
    msk, maxint, max_num_join = None, 2**31, 0
    if do_calc_masks:
        max_num_join = max([len(s) for s in join_annots.values()])
    if do_calc_masks:
        if src_dir == trg_dir:
            print("Error: src_dir == trg_dir, skipping mask generation!")
        elif max_num_join > 1:
            msk = bgrids_to_intids(cv2.imread(src_dir+annot['file_name']))
        else:
            shutil.copy2(src_dir+annot['file_name'], trg_dir)
    for trg_id, segms in join_annots.items():
        if len(segms) == 1:
            ret_annot.append(segms[0])
            continue
        fix_mask_id = list(sorted([s['id'] for s in segms]))[-1] #use largest old id for joined label
        joined_segm = {'id':fix_mask_id,'category_id':trg_id,'iscrowd':0,'area':0}
        x0, y0, x1, y1 = maxint, maxint, -maxint, -maxint
        for s in segms:
            if not msk is None:
                msk[msk == s['id']] = fix_mask_id
            joined_segm['area'] += s['area']
            x0, y0, x1, y1 = min(x0, s['bbox'][0]), \
                             min(y0, s['bbox'][1]), \
                             max(x1, s['bbox'][0]+s['bbox'][2]), \
                             max(y1, s['bbox'][1]+s['bbox'][3])
        joined_segm['bbox'] = [x0, y0, x1-x0, y1-y0]
        ret_annot.append(joined_segm)
        if not msk is None:
            cv2.imwrite(trg_dir+annot['file_name'], intids_to_bgrids(msk))
    annot['segments_info'] =  ret_annot
    return annot
        
#calculate src->trg dataset transformations based on meta data (e.g. supplied by wd2_unified_label_policy.json)
def remapings_from_json(meta0, trg_dataset, src_dataset='wd2', src_fallback_name='unlabeled'):
    if not 'mapping' in meta0 or not 'per_ds' in meta0 or not trg_dataset:
        print("Invalid meta json file!")
        return None, None, None, None
    if not src_dataset in meta0['per_ds'] or not trg_dataset in meta0['per_ds']:
        print("Meta json file is missing src or target dataset information!", src_dataset, trg_dataset)
        print("Potential datasets found: ",meta0['per_ds'].keys())
        return None, None, None, None
    src_cats, trg_cats = meta0['per_ds'][src_dataset], meta0['per_ds'][trg_dataset]
    src_cats = {c['name']:c for c in src_cats}
    trg_cats = {c['name']:c for c in trg_cats}

    trgcats = {}
    src_name_field = src_dataset+'_name'
    trg_name_field = trg_dataset+'_name'
    trg_fallback_name = src_fallback_name
    for c in meta0['mapping']:
        if src_fallback_name in c.get(src_name_field,{}):
            trg_fallback_name = c[trg_name_field]
            break
    src_to_trg, src_is_thing, trg_is_thing = {}, {}, {}
    for c in meta0['mapping']:
        trg_name = c[trg_name_field] if trg_name_field in c else trg_fallback_name
        src_idx, trg_idx = src_cats[c[src_name_field]]['id'], trg_cats[trg_name]['id']
        src_to_trg[src_idx] = trg_idx
        src_is_thing[src_idx] = src_cats[c[src_name_field]].get('isthing',c.get("instances"))
        trg_is_thing[src_idx] = trg_cats[trg_name].get('isthing',c.get("instances"))
        trgcats[trg_idx] = trg_cats[trg_name]
    trgcats = [trgcats[k] for k in sorted(trgcats.keys())]
    return src_to_trg, src_is_thing, trg_is_thing, trgcats

def main(argv=sys.argv[1:], tqdm_vers=tqdm_con):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, 
                        help="source json file containing coco annotations")
    parser.add_argument('--meta_json', type=str, default='wd2_unified_label_policy.json',
                        help="category meta json file")
    parser.add_argument('--trg_dataset', type=str, default="wd2eval",
                        help="category meta json file")
    parser.add_argument('--annotation_root', type=str, default=None,
                        help="annotation masks root directory")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    parser.add_argument('--skip_masks', action='store_true', help="Skips consolidation of stuff segments. Only creates a new json file.")
    
    args = parser.parse_args(argv)
    args.input, args.output = to_abspath(args.input), to_abspath(args.output)
    if args.annotation_root is None:
        args.annotation_root = args.input[:-5]+'/'
    else:
        args.annotation_root = to_abspath(args.annotation_root)+'/'
    if not os.path.exists(args.annotation_root):
        print("Error: mask directory "+args.annotation_root+" is invalid!")
        return -1
    trg_dir = args.output[:-5]+'/' if not args.skip_masks else None
    if not trg_dir is None and not os.path.exists(trg_dir):
        os.makedirs(trg_dir)
    
    meta0 = json.load(open(args.meta_json))
    src_to_trg, src_is_thing, trg_is_thing, trgcats =  remapings_from_json(meta0, args.trg_dataset)
    if not src_to_trg:
      return -2
    print("Loading source annotation file " + args.input + "...")
    annots = json.load(open(args.input))
    annots['categories'] = trgcats
    annots_fixed = []
    for annot in tqdm_vers(annots['annotations'], desc='Remapping annotations'):
        remap0 = remap_annotation(annot, src_to_trg=src_to_trg, src_is_thing=src_is_thing, trg_is_thing=trg_is_thing, src_dir=args.annotation_root, trg_dir=trg_dir)
        annots_fixed.append(remap0)
    annots['annotations']=annots_fixed
    
    print("Writing output to: "+args.output)
    json.dump(annots, open(args.output,'w'))
    
    return 0
    
if __name__ == "__main__":
    sys.exit(main())