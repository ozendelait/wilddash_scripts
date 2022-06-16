#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tool for relabeling datasets using a delta relabel information json file     
# see https://github.com/ozendelait/wilddash_scripts
# by Oliver Zendel, AIT Austrian Institute of Technology GmbH
#
# Use this tool on your own risk!
# Copyright (C) 2022 AIT Austrian Institute of Technology GmbH
# All rights reserved.
#******************************************************************************

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

#return only filename without extension; remove _gtFine_polygons; check_folder is needed for IDD special cases
def path2fn(p, check_folder=False):
    if p is None: return None
    p0 = os.path.splitext(os.path.basename(p))[0].lower().replace('_polygons','').replace('_gtfine','').replace('_gtcoarse','')
    #necessary path augmentation as IDD reuses the same file names multiple times in different folders
    if check_folder and p0.replace('_','').replace('frame','').isnumeric():
        p_spl = p.replace('\\','/').split('/')
        p0 = p_spl[-2]+'_'+p0 if len(p_spl) > 1 else p0
    return p0
#remove special characters; use only last part for MVD names
def canonize_name(n):
    if '--' in n: n = n.split('--')[-1]
    return "".join([c for c in n.lower() if c.isalnum()])
#calc largest bbox contained in two bbox
def bbox_overlap(bboxs):
    p_max = [[bbox[i]+ bbox[i+2] for i in range(2)] for bbox in bboxs]
    top_left = [max(bboxs[0][i], bboxs[1][i]) for i in range(2)]
    if any([top_left[i//2]>p_max[i%2][i//2] for i in range(4)]):
        return None
    bottom_right = [min(p_max[0][i], p_max[1][i]) for i in range(2)]
    return [top_left[0], top_left[1], bottom_right[0]-top_left[0], bottom_right[1]-top_left[1]]
#maximum difference in pixel between multiple bbox
def bbox_diff(bboxs):
    ov, n = bbox_overlap(bboxs), len(bboxs)
    if ov is None:
        return sys.maxsize
    br = [[ov[i]+ ov[i+2] for i in range(2)]] + \
         [[bbox[i]+ bbox[i+2] for i in range(2)] for bbox in bboxs]
    lt_diff = max([abs(ov[i%2]-bboxs[i//2][i%2]) for i in range(n*2)])
    br_diff = max([abs(br[0][i%2]-br[1+i//2][i%2]) for i in range(n*2)])
    return max(lt_diff, br_diff)

#calculate bbox from polygon vertices vector
def poly2bbox(poly0):
    poly_c = [[v[i] for v in poly0] for i in range(2)]
    ret_coords = [min(poly_c[0]), min(poly_c[1]), max(poly_c[0]), max(poly_c[1])]
    ret_coords = [int(c+0.5) for c in ret_coords]
    return ret_coords[0:2]+[ret_coords[2]-ret_coords[0]+1, ret_coords[3]-ret_coords[1]+1]

#change category_id/label of dict change_segminfo inplace using delta infomtation from delta_segminfo
def remap_inplace_onefrm(change_segminfo, delta_segminfo, cross_check_delta=1):
    if len(change_segminfo) == 0 or "label" in change_segminfo[0]:
        id2idx = {i:i for i in range(len(change_segminfo))} #Cityscape uses index in list instead of ids
    else:
        id2idx = {a['id']:i for i,a in enumerate(change_segminfo)}
    ret_errors, success_cnt = [], 0
    for d in delta_segminfo:
        src0 = change_segminfo[id2idx[d['id']]]
        trg_attr = 'label' if 'label' in src0 else 'category_id'
        bbox_check = src0.get('bbox')
        if bbox_check is None and 'polygon' in src0:
            bbox_check = poly2bbox(src0['polygon'])
        if cross_check_delta >= 0 and not bbox_check is None:
            diff = bbox_diff([d['bbox'],bbox_check])
            #check visible rendered bbox (after occlusions)
            if diff > cross_check_delta and 'bbox_vis' in d:
                diff = bbox_diff([d['bbox_vis'],bbox_check])
            #reject if delta information is not matching
            if diff > cross_check_delta:
                ret_errors.append((d['id'],'Mismatch of bbox'))
                continue
            if d['old'] != src0[trg_attr]:
                ret_errors.append((d['id'],'Mismatch of category_id'))
                continue
        src0[trg_attr] = d['new']
        success_cnt += 1
        if 'is_crowd' in src0 and 'is_crowd' in d:
            src0['is_crowd'] = d['is_crowd']
    return ret_errors, success_cnt

def json_read(p):
    return json.load(open(p))
        
#change old/new attribute labels to category ids
def delta_label2catid_inplace(delta_segminfo, cats2ids):
    for d in delta_segminfo:
        d['old'] = cats2ids[d['old']]
        d['new'] = cats2ids[d['new']]

# change_path: a panoptic json (MVD, WD2) or a folder of polygon jsons (Cityscapes, IDD) to be changed (inplace!)
# delta_path: path to delta remap information file
# cross_check_delta: ensures that only delta infomation matching the src information which will be applied; use -1 to turn off
#                    (the default of 1 ensures that rounding errors at bbox are ignored)
# tqdm_vers: call with tqdm_nb from jupyter notebooks for correct tqdm repr. or tqdm_none for silence
def remap_inplace_json(change_path, delta_path, cross_check_delta=1, tqdm_vers=tqdm_con):
    delta0 = json_read(delta_path)
    is_json_dir = os.path.isdir(change_path)
    success_cnt = 0
    if is_json_dir:
        jsons = glob.glob(change_path+'/**/*.json', recursive=True)
        #find json file per delta change request
        id2annot = {path2fn(p, check_folder=True):p for p in jsons}
    else:
        json0 = json_read(change_path)
        add_cats = delta0['categories']
        trg_cats = json0['categories']
        #add new categories to old list
        id_nxt = max(max([c.get('id',0) for c in trg_cats])+1,len(trg_cats))
        for c in add_cats:
            c['id'] = id_nxt
            trg_cats.append(c)
            id_nxt += 1
        #find annotation per delta change request
        cats2ids = {canonize_name(c['name']):c.get('id',i) for i,c in enumerate(trg_cats)}
        id2annot = {path2fn(str(a['image_id'])):a for a in json0['annotations']}
        
    errors, warnings = [], []
    for d in tqdm_vers(delta0['annotations']):
        dfn = path2fn(d['image_id'])
        if not dfn in id2annot:
            warnings.append((dfn,"image_id not found in src"))
            continue
        if not is_json_dir:
            delta_label2catid_inplace(d['segments_info'], cats2ids)
            src_change = id2annot[dfn]['segments_info']
        else:
            src_one_json = json_read(id2annot[dfn])
            src_change = src_one_json['objects']
        errors0, success0 = remap_inplace_onefrm(src_change, d['segments_info'], cross_check_delta=cross_check_delta)
        errors += [[dfn,e[0],e[1]] for e in errors0]
        success_cnt += success0
        if is_json_dir:
            json.dump(src_one_json,open(id2annot[dfn],'wt'))
    if not is_json_dir:
        #store result inplace (make dublicates before calling this function if you want to keep the original!)
        json0['categories'] = trg_cats
        json.dump(json0,open(change_path,'wt'))
    return errors, warnings, success_cnt

def downl_main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--change_path', type=str, default=None,
                        help="Changes are applied directly to this file or json files if supplied a folder. Either path to a panoptic COCO json (MVD, WD2) or a folder of polygon information jsons (Cityscapes, IDD)")
    parser.add_argument('--delta_path', type=str, default=None,
                        help="Delta remap information json file")
    parser.add_argument('--cross_check_delta', type=int, default=1,
                        help="Cross check delta information to ensure correct segments are mapped. Use -1 to turn off")
    parser.add_argument('--silent', action='store_true', help="Suppress all outputs")
    parser.add_argument('--verbose', action='store_true', help="Print extra information")
    args = parser.parse_args(argv)
    tqdm_vers = tqdm_none if args.silent else tqdm_con
    errors, warnings, success_cnt = remap_inplace_json(change_path = args.change_path, 
                                                       delta_path = args.delta_path, 
                                                       cross_check_delta = args.cross_check_delta,
                                                       tqdm_vers = tqdm_vers)
    if not args.silent:
        print("Finished delta remapping opertation with %i successes, %i warnings, and %i errors."%(success_cnt, len(warnings), len(errors)))
        if args.verbose and len(warnings) > 0:
            print("Generated these warnings: ", warnings)
        if args.verbose and len(errors) > 0:
            print("Generated these errors: ", warnings)

if __name__ == "__main__":
    sys.exit(downl_main())
