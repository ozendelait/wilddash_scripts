# wilddash_scripts
Support scripts for datasets and benchmark hosted on wilddash.cc (WildDash and RailSem)

### download_helper ###

Scripts for automatic downloading of Wilddash/RailSem datasets (see subfolder)

### pano2sem.py ###

Simple script to transform panoptic GT into semantic/instance segmentation GT

### remap_delta ###

Tool and json format for relabeling of other datasets (see subfolder)

### cscats_labelspy.py ###

Simple script to convert category meta data between Cityscapes labels.py format and COCO panoptic category json format

### remap_coco.py / wd2_unified_label_policy.json ###

Tool and meta-data to convert Wilddash2 into MVD v1.2, Cityscapes, IDD, and WD2_eval categories.
The json file contains the unified panoptic segmentation label policy as discribed by the Wilddash2 paper ([Table 1 in Supplemental](https://openaccess.thecvf.com/content/CVPR2022/supplemental/Zendel_Unifying_Panoptic_Segmentation_CVPR_2022_supplemental.pdf) ).

Combine remap_coco.py with pano2sem.py to create converted semantic segmentation (uint8) data.
