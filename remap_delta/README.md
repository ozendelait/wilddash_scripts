## Delta dataset relabeling tool and json format

Tool to remap segmentation datasets inplace using a supplied delta remap information json (e.g. [downloaded from wilddash.cc](https://wilddash.cc/download/wd2_add_pickupvan.zip) to remap MVD, Cityscapes, or IDD to include pickup-truck and van labels).
Additional meta data in the remap files prevent mix-ups between datasets without requiring explicit file hashes (which could be a problem when starting with an already mixed/altered dataset).

### License ###

This tool is released under MIT license. It might rewrite/break json files, use it at your own risk. Changing a dataset using this tool might also change aspects of the resulting dataset's usage license. You have to check the license terms of the original source dataset and the remapping information for clarification.
If you create a remapping yourself, be sure you have the rights to publish the delta information as it contains parts of the original source material. CC-BY, CC-BY-NC should be fine; a CC-*-SA license means your relabeling information should probably be released under the exact same information.
If you want to distribute this tool jointly together with relabling information under a differnet license (e.g. CC-BY-NC-SA 4.0), then you are allowed to do so as long as no liability is generated for the original authors and a citation to this repository is added.

### Usage ###
```
python remap_delta.py --change_path file_s_to_be_changed.json --delta_path delta_remap_info.json
```

Note that warnings are generated for all delta annotation which could not be matched in the json(s) to be changed. Some delta relabel information files might contain more data that an individual dataset. For example: the WD2 relabel information for MVD is combined in a single mvdv1p2_remap.json file but can be applied to either the training panoptic json or the validation json. So in both cases some remappings will not be found in the respective target files and warnings are to be expected.

### Delta dataset relabeling json format ###

The relabeling format is derived from the COCO panoptic json format:
https://cocodataset.org/#format-data (4. Panoptic Segmentation)

Changes are:
* new categories for a specific dataset get the regular entries in the "categories" group but have no "id" attribute; ids are appended/assigned when relabeling an actual dataset which might use different orders etc.
* the image_id attribute per annotation is a string representing a unique identifier derived from the filename of the individual files to be remapped. The redundant Cityscapes postfixes _gtFine_polygon are removed.
* segment_info contain no category_id. Instead, the attributes "old" and "new" contain human-readable category names for the old and new categories.
* Cityscapes polygon files have no unique identifier per segment other than the order within the file. The "id" attribute of the segment_info entries are thus using this index position for Cityscapes polygon.json files (indices start with 0 for the entry).
* Polygon files can define shapes that will later be partially covered by other segments (based on z-order). To keep track of both states, the "bbox" and "area" attributes reflect the single original segment while "bbox_vis" and "area_vis" can optionally be added to reflect the visible extent of this segment after the full mask has been created.

### Citation: ###
If you use the WD2 relabeling information, please cite our associated paper:

    @InProceedings{Zendel_2022_CVPR,
    author = {Zendel, Oliver and Sch{\"o}rghuber, Matthias and Rainer, Bernhard and Murschitz, Markus and Beleznai, Csaba},
    title = {Unifying Panoptic Segmentation for Autonomous Driving},
    booktitle = {Conference on Computer Vision and Pattern Recognition (CVPR)},
    month = {June},
    year = {2022}
    }

If you like to use this tool/delta relabeling format for your project, please cite our repo:

    @misc{ZendelDeltaRelabel,
    author = {Zendel, Oliver and Sch{\"o}rghuber, Matthias},
    title = {Delta dataset relabeling tool},
    year = {2022},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/ozendelait/wilddash_scripts/remap_delta}},
    }
