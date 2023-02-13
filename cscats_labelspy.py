#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tool for converting from/to Cityscapes label.py style category meta information
#
# example:
# cats = labelpy2cats('labels.py')
# cats_overwrite_trainids(cats, id2trainid) # optional: id2trainid contains custom mapping of id -> trainId
# with open('labels_new.py','w') as ofile:
#     ofile.writelines(cat2labelpy(cats))
#
# see https://github.com/ozendelait/wilddash_scripts
# by Oliver Zendel, AIT Austrian Institute of Technology GmbH
#
# Use this tool on your own risk!
# Copyright (C) 2023 AIT Austrian Institute of Technology GmbH
# All rights reserved.
#******************************************************************************
import json

# loads categories from json compatible with coco panoptic format
# as well as Mapillary Vistas/Wilddash2 meta json files
def cocojson2cats(json_path):
    jcont = json.load(open(json_path))
    cats = jcont.get('categories',jcont.get('labels'))
    # add supercategoryids ids
    sc_ids = {}
    for id0, cat in enumerate(cats):
        if not cat['supercategory'] in sc_ids:
            sc_ids[cat['supercategory']] = len(sc_ids)
        cat['supercategory_id'] = sc_ids[cat['supercategory']]
    return cats
        
# will overwrite train_id and evaluate with user-supplied trainids
def cats_overwrite_trainids(cats, id2trainid):
    for id0, cat in enumerate(cats):
        idcat = cat.get('id', id0)
        if not idcat in id2trainid:
            cat['train_id'] = 255 if idcat >= 0 else -1
            cat['evaluate'] = False
            continue
        cat['train_id'] = id2trainid[id0]
        cat['evaluate'] = cat['train_id'] >= 0 and idcat < cat['train_id']
    
# loads categories from python label structure compatible with Cityscapes-scripts file
# https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/helpers/labels.py
def labelpy2cats(labelpypath):
    ret_cats = []
    with open(labelpypath) as ifile:
        for line0 in ifile:
            if len(ret_cats) > 0 and ']' in line0:
                break
            if not 'Label(' in line0:
                continue
            spl = [l.replace('(','').replace(')','').strip() for l in line0.split(',')]
            name0, cat0 = spl[0].split("'")[1], spl[3].split("'")[1]
            ret_cats.append({'color':[int(spl[7]),int(spl[8]),int(spl[9])],
                             'instances': 'rue' in spl[5],
                             'readable': name0+'('+cat0+')',
                             'name': name0,
                             'evaluate': 'alse' in spl[6],
                             'id':int(spl[1]),
                             'train_id':int(spl[2]),
                             'supercategory':cat0,
                             'supercategory_id':int(spl[4])})
    return ret_cats

cs_labels_start = """
labels = [
    #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
"""
cs_labels_templ = "    Label(  '{name: <22},{id0:3d} ,      {tid:3d} , '{cat_name: <17},{cid:2d}       , {is_inst_str: <13}, {is_ignor_eval: <13}, ({col[0]:3d},{col[1]:3d},{col[2]:3d}) ),\n"
# creates python label structure compatible with Cityscapes-scripts file
# https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/helpers/labels.py
def cat2labelpy(cats):
    ret_str = cs_labels_start
    for id0, cat in enumerate(cats):
        ret_str += cs_labels_templ.format(name=cat['name']+"'", 
            id0= cat.get('id', id0),
            tid = cat.get('train_id',-1), 
            cat_name = cat.get('supercategory','void')+"'",
            cid = cat.get('supercategory_id',-1), 
            is_inst_str = str(cat.get('instances', cat.get('isthing',False))),
            is_ignor_eval = str(not cat.get('evaluate', True)),
            col = cat['color'])
    return ret_str+']\n'