"""
Generate 5-fold cross-validation splits from labels.json.

Writes cv/train_{0..4}.json and cv/val_{0..4}.json. Each fold holds out a
non-overlapping 10% block as validation; the other 90% is training. Output
format = {'splitnames', 'locdata'} — what APT_interface.py (-json_trn_file) and
Cricket-Hunting's pose.load_apt() consume.

Usage:
    python make_splits.py                  # default: labels.json, seed=42
    python make_splits.py --seed 0
    python make_splits.py --labels other.json --out-dir cv2
"""

import argparse
import json
import os
import random


def make_splits(labels_path, out_dir, seed, n_fold=5, val_frac=0.1):
    with open(labels_path) as f:
        labels = json.load(f)

    locdata = list(labels['locdata'])
    rng = random.Random(seed)
    rng.shuffle(locdata)

    n = len(locdata)
    n_val = int(n * val_frac)
    if n_fold * 2 * n_val > n:
        raise ValueError(
            f"n_fold * 2 * n_val = {n_fold * 2 * n_val} exceeds n_locdata = {n}; "
            f"non-overlapping fold layout cannot fit."
        )

    os.makedirs(out_dir, exist_ok=True)

    # APT reads images via os.path.join(pack_dir, img_path) where
    # pack_dir = dirname(train_i.json) = cv/. The img paths in locdata are
    # "im/<name>.png", so APT needs cv/im/<name>.png. Symlink cv/im -> ../im
    # so it resolves to training/im/ without copying ~320 MB of PNGs.
    im_link = os.path.join(out_dir, 'im')
    if not os.path.lexists(im_link):
        os.symlink('../im', im_link)
        print(f"created symlink {im_link} -> ../im")

    for i in range(n_fold):
        # validation block = the i-th of every-other 10% slice (matches old notebook)
        v0 = (i * 2) * n_val
        v1 = (i * 2 + 1) * n_val
        val = locdata[v0:v1]
        train = locdata[:v0] + locdata[v1:]

        train_path = os.path.join(out_dir, f"train_{i}.json")
        val_path = os.path.join(out_dir, f"val_{i}.json")
        with open(train_path, 'w') as f:
            json.dump({'splitnames': ['train'], 'locdata': train}, f)
        with open(val_path, 'w') as f:
            json.dump({'splitnames': ['val'], 'locdata': val}, f)
        print(f"fold {i}: train={len(train)}  val={len(val)}  -> {train_path}, {val_path}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--labels', default=os.path.join(here, 'labels.json'),
                   help='Path to labels.json (default: ./labels.json next to this script)')
    p.add_argument('--out-dir', default=os.path.join(here, 'cv'),
                   help='Output directory for split jsons (default: ./cv)')
    p.add_argument('--seed', type=int, default=42, help='Shuffle seed (default: 42)')
    p.add_argument('--n-fold', type=int, default=5)
    p.add_argument('--val-frac', type=float, default=0.1)
    args = p.parse_args()

    make_splits(args.labels, args.out_dir, args.seed, args.n_fold, args.val_frac)


if __name__ == '__main__':
    main()
