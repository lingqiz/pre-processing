# Cross-Validation for the DLC Pose Tracker

This folder runs a 5-fold cross-validation of the APT / DeepLabCut pose tracker
(37 keypoints, single view, 1024×1024). It estimates how well the tracker
generalizes by training on 90% of the hand-labeled frames and predicting on the
held-out 10%, repeated over 5 non-overlapping validation folds.

## Files

| File / dir            | Role                                                              |
|-----------------------|-------------------------------------------------------------------|
| `labels.json`         | APT training package — all hand-labeled frames (`locdata`/`pabs`). |
| `im/`                 | The labeled-frame image crops referenced by `labels.json`.        |
| `cross_validate.ipynb`| Makes the 5 train/val splits, then runs prediction on each fold.  |
| `cv/`                 | The split files: `train_{0..4}.json`, `val_{0..4}.json`.          |
| `train.cmd`           | Submits one APT training job per fold (bsub, GPU).                |
| `cv_track.sh`         | Submits one APT tracking job per fold on its validation video.    |
| `train_config.json`   | APT training config exported from the `.lbl` project.            |
| `.temp/`              | Validation videos, tracking output (`out_*.trk/.mat`), logs.      |

## Step 0 — Generate the cross-validation data (`labels.json` + `im/`)

`labels.json` + `im/` are an **APT training package**.

To regenerate the package from a newer `.lbl` project (e.g.
`/groups/dennis/dennislab/data/APT_Label/Tracking040126_DLC.lbl`):

1. Open the `.lbl` project in the APT GUI.
2. Start a DeepLabCut training run. As soon as it launches, APT's MATLAB side
   writes the training package into the model's cache directory
   (`dmc.dirProjLnx`):
   - the loc json (`dmc.trainLocLnx`) — this is the `labels.json` equivalent,
   - an `im/` folder of crops named `mov####_frm########_tgt#####_view#.png`.
   You can cancel the run once the package is written; only the export is needed.
3. Copy that json into this folder as `labels.json` and the `im/` folder
   alongside it.
