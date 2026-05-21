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
| `make_splits.py`      | **Step 1**: shuffles `labels.json` into 5 train/val fold jsons.   |
| `cv/`                 | The split files: `train_{0..4}.json`, `val_{0..4}.json`.          |
| `submit_train.sh`     | **Step 2**: submits one bsub training job per fold (GPU).         |
| `validation.py`          | **Step 3**: builds val mp4s and submits tracking bsub jobs.       |
| `convert.sh`          | **Step 4**: bsub MATLAB job to convert `.trk` → `.mat`.           |
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

## Step 1 — Make the train/val splits

```bash
python make_splits.py
```

Shuffles `labels.json` (fixed seed = 42) and writes 5 folds into `cv/`.
Also creates `cv/im -> ../im` as a symlink. 
Options:
- `--seed N` — change the shuffle seed (different split).
- `--labels PATH` / `--out-dir DIR` — override the defaults.
- `--n-fold` / `--val-frac` — change the fold layout (defaults: 5, 0.1).

## Step 2 — Submit training jobs

```bash
bash submit_train.sh                  # all 5 folds
bash submit_train.sh 1 3              # only folds 1 and 3
```

Submits one bsub GPU job per fold, all
running in parallel. Each fold:
- reads `cv/train_${i}.json` (from Step 1),
- runs APT's `APT_interface.py` in DeepLabCut mode inside the
  `apt_20230427_tf211_pytorch113_ampere.sif` Singularity image,
- writes checkpoints to `../.apt/train/train_${i}/`,
- logs to `../.apt/train/train_${i}.log` (+ `.err`, `.aptsnapshot`).

## Step 3 — Validate on the held-out frames

```bash
python validation.py                          # all 5 folds
python validation.py 1 3                      # only folds 1 and 3
python validation.py --no-build               # reuse existing .temp/val_*.mp4
python validation.py --checkpoint deepnet-540000 1   # override auto-pick (fold 1)
```

For each fold:
1. **Builds** `.temp/val_${i}.mp4` from the frames in `cv/val_${i}.json` (5 fps,
   mp4v). Frame order matches `val_${i}.json`, so `out_${i}.mat` indexing lines
   up with `pose.load_apt('cv/val_${i}.json')` downstream.
2. **Picks the latest checkpoint** — scans `../.apt/train/train_${i}/`
   recursively for `deepnet-NNNNNN.index` and takes the highest `N`. Override
   with `--checkpoint deepnet-NNNNNN`. If no checkpoint exists yet (training
   hasn't hit its first 50k save), the script errors out with a clear message.
3. **Submits a bsub tracking job** (`-q gpu_a100 -W 1:00 -n 8 -gpu "num=1"`)
   that runs `APT_interface.py track` and writes `.temp/out_${i}.trk`. Job name
   is `DLC_Track_${i}`; log goes to `.temp/track_${i}.log`.

## Step 4 — Convert `.trk` → `.mat`

```bash
bash convert.sh                            # all 5 folds
bash convert.sh 0 3                        # only folds 0 and 3
```

Submits one bsub MATLAB job that loads each `.temp/out_${i}.trk` (which is a
MAT-format file) and writes `.temp/out_${i}.mat` with fields `points`, `conf`,
`start_frame`, `end_frame` — the format `pose.load_pred()` expects.

The temp MATLAB script and log live in `~/.tmp/matlab/cv_convert_<timestamp>.{m,log}`.

## Downstream evaluation

After Step 4, the cross-validation accuracy is computed by
`Cricket-Hunting/utils/notebook/pose_tracking.ipynb` (Evaluation section). Its
loader (`pose.load_data`) reads:
- `training/cv/val_${i}.json` for ground-truth `pabs`,
- `training/.temp/out_${i}.mat` for predicted `points`.
