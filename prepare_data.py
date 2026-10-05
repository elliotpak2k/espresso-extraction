"""
Build per-annotator Potato packages from the Google Sheet export.

Design:
  - Each shot yields TWO items: its puck photo (channeling task) and its
    crema photo (crema task). The two get unrelated opaque IDs and separate
    personal orders, so an annotator cannot link a puck to its crema.
  - OVERLAP shots: labeled by every annotator (agreement / QWK set)
  - REMAINDER shots: each labeled by REDUNDANCY annotators, rotated through
    every possible annotator group so every pair of annotators shares items
    and everyone gets the same workload
  Both tasks use the same shot assignment. Each annotator gets two Potato
  tasks, run in order: 1_channeling/ then 2_crema/.

Outputs (commit everything except PRIVATE_*):
  images/<id>.jpg                              resized photos renamed to opaque IDs
  annotators/annotator_N/1_channeling/{config.yaml,data.jsonl}
  annotators/annotator_N/2_crema/{config.yaml,data.jsonl}
  PRIVATE_key.csv          opaque IDs <-> shot_id, intent, who labels it
  PRIVATE_id_secret.txt    created on first run; keeps IDs stable across reruns.
                           Keep it (and back it up) -- a new secret means new IDs.

Photos are looked up in <image-dir>/<image column>/<file> (the Drive folder
layout), falling back to <image-dir>/<file>. Shots missing either photo are dropped.

Usage:
  python prepare_data.py shots.csv --image-dir ./raw_photos \
      --base-url https://raw.githubusercontent.com/<you>/<repo>/main/images \
      --n-annotators 6 --overlap 40 --redundancy 3
"""
import argparse
import hashlib
import hmac
import itertools
import json
import random
import secrets
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps

# ---- Edit these to match your sheet's column headers ----
SHOT_ID_COL = "shot_id"   # not in the form export yet; add it to the final CSV
TASK_IMAGE_COLS = {"1_channeling": "puck_image_file", "2_crema": "crema_image_file"}  # task -> sheet column
INTENT_COL = "sample_tracking"   # used ONLY to stratify the overlap set, never shown
MAX_EDGE = 1600

COMMON_HEADER = """\
# Potato task for {name}. Run from THIS folder:  potato start config.yaml -p 8000
annotation_task_name: "{title} ({name})"
task_dir: "."
port: 8000

data_files:
  - "data.jsonl"
item_properties:
  id_key: id
  text_key: image

instance_display:
  fields:
    - key: image
      type: image
      label: "{image_label}"
      display_options: {{max_width: "100%", max_height: 600, zoomable: true, resizable: false}}

annotation_codebook_url: "{codebook}"
"""

COMMON_FOOTER = """
assignment_strategy: fixed_order   # data.jsonl is already shuffled per person
num_annotators_per_item: 1         # local copy = one annotator

# log in as: {name}  (no password; only this username is accepted)
require_password: false
user_config:
  allow_all_users: false
  users: ["{name}"]

# labels are saved to annotation_output/{name}/user_state.json;
# a jsonl export is also written to annotation_output/exports/
output_annotation_dir: "annotation_output/"
export_annotation_format: jsonl
"""

CONFIDENCE_SCHEME = """\
  - annotation_type: confidence
    name: {prefix}_confidence
    description: "How confident are you in this rating?"
    target_schema: {target}
    scale_type: likert
    labels: ["1 - Guessing", "2", "3", "4", "5 - Certain"]
    label_requirement: {{required: true}}
"""

QUALITY_FLAG_SCHEME = """\
  - annotation_type: multiselect
    name: {prefix}_image_quality
    description: "Optional: tick if the photo is too blurry or dark to judge"
    labels:
      - "Image quality issue"
    label_requirement: {{required: false}}
"""

SCHEMES = {
    "1_channeling": dict(
        title="Espresso Puck Channeling", image_label="Puck photo",
        schemes="""\
annotation_schemes:
  - annotation_type: multiselect
    name: channeling_features
    description: "Step 1: tick EVERY feature you see (guidelines A1). Leave blank if none."
    labels:
      - "Pinholes"
      - "Cracks"
      - "Edge gap"
      - "Wet pooling"
      - "Uneven color"
      - "Craters / divots"
    label_requirement: {required: false}
  - annotation_type: radio
    name: channeling_severity
    description: "Step 2: how severe is the channeling? (guidelines A3-A4)"
    labels:
      - "0 - None"
      - "1 - Low"
      - "2 - Medium"
      - "3 - High"
    sequential_key_binding: true
    label_requirement: {required: true}
""" + CONFIDENCE_SCHEME.format(prefix="channeling", target="channeling_severity")
    + QUALITY_FLAG_SCHEME.format(prefix="puck")),
    "2_crema": dict(
        title="Espresso Crema Extraction", image_label="Crema photo",
        schemes="""\
annotation_schemes:
  - annotation_type: radio
    name: crema_extraction
    description: "How does the extraction look from the crema? (guidelines B2-B3)"
    labels:
      - "Under"
      - "Balanced"
      - "Over"
    sequential_key_binding: true
    label_requirement: {required: true}
""" + CONFIDENCE_SCHEME.format(prefix="crema", target="crema_extraction")
    + QUALITY_FLAG_SCHEME.format(prefix="crema")),
}


def render_config(task, name, codebook):
    s = SCHEMES[task]
    header = COMMON_HEADER.format(name=name, title=s["title"], image_label=s["image_label"], codebook=codebook)
    return header + "\n" + s["schemes"] + COMMON_FOOTER.format(name=name)


def load_secret(out):
    """Random secret, created once. IDs are keyed on it, so they are stable across reruns
    but cannot be recomputed from the (public) script and seed."""
    p = out / "PRIVATE_id_secret.txt"
    if not p.exists():
        p.write_text(secrets.token_hex(16))
    return p.read_text().strip()


def opaque_id(secret, task, shot_id):
    return hmac.new(secret.encode(), f"{task}:{shot_id}".encode(), hashlib.sha256).hexdigest()[:8]


def stratified_sample(df, n, seed):
    """Overlap set proportional across intent groups -> covers full severity range."""
    if INTENT_COL not in df.columns:
        return df.sample(n=n, random_state=seed)
    parts = [g.sample(n=min(max(1, round(n * len(g) / len(df))), len(g)), random_state=seed)
             for _, g in df.groupby(INTENT_COL)]
    picked = pd.concat(parts)
    if len(picked) > n:
        picked = picked.sample(n=n, random_state=seed)
    elif len(picked) < n:
        picked = pd.concat([picked, df.drop(picked.index).sample(n=n - len(picked), random_state=seed)])
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--image-dir", required=True)
    ap.add_argument("--base-url", required=True, help="public URL prefix for images/")
    ap.add_argument("--n-annotators", type=int, default=6)
    ap.add_argument("--overlap", type=int, default=40)
    ap.add_argument("--redundancy", type=int, default=3, help="labels per remainder item")
    ap.add_argument("--codebook-url", default="")
    ap.add_argument("--seed", type=int, default=510)
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    out, src = Path(args.out), Path(args.image_dir)
    (out / "images").mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    names = [f"annotator_{i + 1}" for i in range(args.n_annotators)]
    secret = load_secret(out)

    df = pd.read_csv(args.csv)
    missing = [c for c in [SHOT_ID_COL, *TASK_IMAGE_COLS.values()] if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns in CSV: {missing}")
    if df[SHOT_ID_COL].duplicated().any():
        raise SystemExit(f"Duplicate values in {SHOT_ID_COL}")
    no_image = df[list(TASK_IMAGE_COLS.values())].isna().any(axis=1)
    if no_image.any():
        print(f"dropping {no_image.sum()} shots with a missing photo: {', '.join(df.loc[no_image, SHOT_ID_COL])}")
        df = df[~no_image].reset_index(drop=True)
    for task in TASK_IMAGE_COLS:
        df[f"{task}_id"] = [opaque_id(secret, task, s) for s in df[SHOT_ID_COL]]
    all_ids = pd.concat([df[f"{t}_id"] for t in TASK_IMAGE_COLS])
    if all_ids.duplicated().any():
        raise SystemExit("Opaque ID collision; delete PRIVATE_id_secret.txt and rerun")

    # --- images: resize + rename to opaque IDs, build item records ---
    items = {task: {} for task in TASK_IMAGE_COLS}
    for idx, row in df.iterrows():
        for task, col in TASK_IMAGE_COLS.items():
            path = src / col / str(row[col])   # raw_photos/<column>/<file>, as downloaded from Drive
            if not path.exists():
                path = src / str(row[col])
            if not path.exists():
                raise SystemExit(f"Image not found: {path}")
            item_id = row[f"{task}_id"]
            fname = f"{item_id}.jpg"
            img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
            img.thumbnail((MAX_EDGE, MAX_EDGE))
            img.save(out / "images" / fname, quality=88)
            items[task][idx] = {"id": item_id, "image": f"{args.base_url.rstrip('/')}/{fname}"}

    # --- assignment (shared by both tasks) ---
    overlap = list(stratified_sample(df, args.overlap, args.seed).index)
    remainder = [i for i in df.index if i not in set(overlap)]
    rng.shuffle(remainder)
    # cycle through ALL k-subsets of annotators: equal workload, every pair shares items
    groups = itertools.cycle(list(itertools.combinations(range(args.n_annotators), args.redundancy)))
    assigned = {n: list(overlap) for n in names}
    who = {i: "ALL" for i in overlap}
    for i in remainder:
        g = next(groups)
        for a in g:
            assigned[names[a]].append(i)
        who[i] = ";".join(names[a] for a in g)

    # --- write one package per annotator, one folder per task ---
    for n in names:
        for task in TASK_IMAGE_COLS:
            d = out / "annotators" / n / task
            d.mkdir(parents=True, exist_ok=True)
            order = assigned[n][:]
            random.Random(f"{args.seed}-{n}-{task}").shuffle(order)  # personal order, differs per task
            with open(d / "data.jsonl", "w") as f:
                for i in order:
                    f.write(json.dumps(items[task][i]) + "\n")
            (d / "config.yaml").write_text(render_config(task, n, args.codebook_url))

    key_cols = [c for c in [SHOT_ID_COL, INTENT_COL, *(f"{t}_id" for t in TASK_IMAGE_COLS)] if c in df.columns]
    key = df[key_cols].copy()
    key["labeled_by"] = [who[i] for i in df.index]
    key.to_csv(out / "PRIVATE_key.csv", index=False)

    print(f"overlap: {len(overlap)} shots x {args.n_annotators} annotators")
    print(f"remainder: {len(remainder)} shots x {args.redundancy} annotators")
    for n in names:
        print(f"  {n}: {len(assigned[n])} shots x {len(TASK_IMAGE_COLS)} tasks")
    print(f"total labels per task: {sum(len(v) for v in assigned.values())}")


if __name__ == "__main__":
    main()
