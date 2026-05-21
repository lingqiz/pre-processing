"""
Step 3 — Run cross-validation prediction.

For each fold:
  1. Build .temp/val_${i}.mp4 from the frames in cv/val_${i}.json (5 fps).
  2. Find the latest deepnet-NNNNNN checkpoint in ../.apt/train/train_${i}/.
  3. SSH to login1 and submit a bsub tracking job that runs APT_interface.py
     `track` with that checkpoint on the val video. Output: .temp/out_${i}.trk.

Usage:
    python predict.py                       # all 5 folds
    python predict.py 1 3                   # only folds 1 and 3
    python predict.py --no-build            # reuse existing .temp/val_*.mp4
    python predict.py --checkpoint deepnet-540000 1   # override auto-pick (fold 1)

Frame order in the mp4 matches val_${i}.json order, so out_${i}.mat lines up
with pose.load_apt('cv/val_${i}.json') in downstream evaluation.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(HERE)
APT_DIR = "/groups/zhang/home/zhangl5/APT"
SIF = "/groups/branson/bransonlab/apt/sif/apt_20230427_tf211_pytorch113_ampere.sif"
MODEL_CONFIG = "/groups/zhang/home/zhangl5/Emily/apt_config.json"
TRACK_CONFIG = os.path.join(PROJ_ROOT, "tracking/apt_config.json")
TRAIN_ROOT = os.path.join(PROJ_ROOT, ".apt/train")
TRACK_CACHE = "/groups/zhang/home/zhangl5/.apt/apt_tracking_temp_files"

QUEUE = "gpu_a100"
WALLTIME = "1:00"
NCORES = 8
FPS = 5


def build_val_video(fold, cv_dir, temp_dir):
    """Concatenate val frames into an mp4. Frame order = val_${fold}.json order."""
    import cv2  # imported lazily so --help works without cv2

    val_path = os.path.join(cv_dir, f"val_{fold}.json")
    out_path = os.path.join(temp_dir, f"val_{fold}.mp4")
    val = json.load(open(val_path))

    first_img = cv2.imread(os.path.join(cv_dir, val['locdata'][0]['img'][0]))
    h, w = first_img.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, FPS, (w, h))
    for frame in val['locdata']:
        img = cv2.imread(os.path.join(cv_dir, frame['img'][0]))
        writer.write(img)
    writer.release()
    print(f"  built {out_path} ({len(val['locdata'])} frames, {w}x{h})")
    return out_path


def find_latest_checkpoint(fold):
    """Return the deepnet-NNNNNN name with the highest N in train_${fold}/."""
    train_dir = os.path.join(TRAIN_ROOT, f"train_{fold}")
    matches = glob.glob(os.path.join(train_dir, "**", "deepnet-*.index"), recursive=True)
    if not matches:
        raise FileNotFoundError(
            f"No deepnet-*.index files under {train_dir}. Training may not have "
            f"reached the first save (50k iters) yet."
        )
    def step(p):
        m = re.search(r"deepnet-(\d+)\.index$", p)
        return int(m.group(1)) if m else -1
    latest = max(matches, key=step)
    # APT's -model_files wants the prefix-with-step (without the trailing extension)
    return latest[:-len(".index")]


def submit_track(fold, model_files, val_mp4, temp_dir):
    out_trk = os.path.join(temp_dir, f"out_{fold}.trk")
    log = os.path.join(temp_dir, f"track_{fold}.log")
    err = os.path.join(temp_dir, f"track_{fold}.err")

    bsub_cmd = (
        f"bsub -n {NCORES} -gpu \"num=1\" -q {QUEUE} -W {WALLTIME} "
        f"-o \"{log}\" "
        f"-R\"affinity[core(1)]\" "
        f"-J DLC_Track_{fold} "
        f"\"singularity exec --nv -B \\\"/groups\\\" -B \\\"/nrs\\\" "
        f"\\\"{SIF}\\\" "
        f"bash -c \\\"TORCH_HOME='/groups/zhang/home/zhangl5/.apt/torch' "
        f"python '{APT_DIR}/deepnet/APT_interface.py' "
        f"'{MODEL_CONFIG}' -name track_{fold} "
        f"-err_file '{err}' "
        f"-type deeplabcut "
        f"-model_files '{model_files}' "
        f"-ignore_local 1 "
        f"-cache '{TRACK_CACHE}' "
        f"track "
        f"-config_file '{TRACK_CONFIG}' "
        f"-out '{out_trk}' "
        f"-mov '{val_mp4}'\\\"\""
    )

    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking no", "login1.int.janelia.org", bsub_cmd]
    print(f"  submitting tracking job for fold {fold} (model: {os.path.basename(model_files)})")
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise RuntimeError(f"bsub submission failed for fold {fold}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('folds', nargs='*', type=int, help='Fold indices (default: 0 1 2 3 4)')
    p.add_argument('--no-build', action='store_true', help='Skip rebuilding .temp/val_*.mp4')
    p.add_argument('--checkpoint', default=None,
                   help='Override checkpoint (e.g. deepnet-540000). Default: latest per fold.')
    p.add_argument('--cv-dir', default=os.path.join(HERE, 'cv'))
    p.add_argument('--temp-dir', default=os.path.join(HERE, '.temp'))
    args = p.parse_args()

    folds = args.folds if args.folds else [0, 1, 2, 3, 4]
    os.makedirs(args.temp_dir, exist_ok=True)

    for i in folds:
        print(f"fold {i}:")
        val_mp4 = os.path.join(args.temp_dir, f"val_{i}.mp4")
        if not args.no_build:
            val_mp4 = build_val_video(i, args.cv_dir, args.temp_dir)
        elif not os.path.exists(val_mp4):
            raise FileNotFoundError(f"{val_mp4} missing; drop --no-build to rebuild.")

        if args.checkpoint:
            model_files = os.path.join(TRAIN_ROOT, f"train_{i}", args.checkpoint)
        else:
            model_files = find_latest_checkpoint(i)

        submit_track(i, model_files, val_mp4, args.temp_dir)


if __name__ == '__main__':
    main()
