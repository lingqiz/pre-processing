"""
Generate 5-fold cross-validation splits from labels.json.

Strategy: sort locdata by (imov, frm) so frames are in natural movie order,
then assign each frame to a fold by stride: fold i holds out indices
{j : j % n_fold == i} as validation, the rest as training.

This is standard k-fold CV (each frame appears in exactly one val set) with
movie-order stratification — since labels cluster by movie, the stride ensures
every fold sees a similar distribution of movies.

Writes cv/train_{0..4}.json and cv/val_{0..4}.json. Output format is
{'splitnames', 'locdata'} — what APT_interface.py (-json_trn_file) and
Cricket-Hunting's pose.load_apt() consume.

Also creates cv/im -> ../im so APT's path resolution (pack_dir +
img['im/...png']) finds the PNGs without copying them.

Usage:
    python make_splits.py
    python make_splits.py --n-fold 10
    python make_splits.py --labels other.json --out-dir cv2
"""

import argparse
import json
import os


def make_splits(labels_path, out_dir, n_fold=5):
    with open(labels_path) as f:
        labels = json.load(f)

    locdata = sorted(labels['locdata'], key=lambda e: (e['imov'], e['frm']))

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
        val = [e for j, e in enumerate(locdata) if j % n_fold == i]
        train = [e for j, e in enumerate(locdata) if j % n_fold != i]

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
    p.add_argument('--labels', default=os.path.join(here, 'labels.json'))
    p.add_argument('--out-dir', default=os.path.join(here, 'cv'))
    p.add_argument('--n-fold', type=int, default=5)
    args = p.parse_args()

    make_splits(args.labels, args.out_dir, args.n_fold)


if __name__ == '__main__':
    main()
