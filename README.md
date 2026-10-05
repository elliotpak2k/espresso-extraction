# Espresso Puck Channeling Annotation (ARI 510)

A new dataset of home espresso shots pulled with Michigan-roasted beans. Each
shot has a row of brew parameters, a photo of the used puck, and a photo of the
crema. Annotators label the two photos separately:

- **Puck photo:** channeling severity (None / Low / Medium / High), plus a feature checklist
- **Crema photo:** apparent extraction (Under / Balanced / Over)

Both labels also get a 1-5 confidence rating. The main target is **channeling
severity**, scored with quadratic weighted kappa (QWK). It is an ordinal label,
so predicting "Low" when the answer is "High" should cost more than predicting
"Medium".

**Annotators: start with [README_annotators.md](README_annotators.md).**
Labeling rules are in [annotation_guidelines.md](annotation_guidelines.md).

---

## 1. Summary

| | |
|---|---|
| **Instance** | One espresso shot: one tabular record, one puck photo, one crema photo |
| **Shots** | 154 (out of 158 logged; see [Sampling](#4-sampling-and-filtering)) |
| **Annotation items** | 308 images: 154 puck (channeling task) + 154 crema (crema task) |
| **Collection dates** | 2026-09-09 to 2026-10-05, on 23 days |
| **Beans** | 10 bags from 2 southeast Michigan roasters |
| **Annotators** | 6 |
| **Labels per task** | 582 (40 shots × 6 annotators + 114 shots × 3 annotators) |
| **Collector** | Elliot Pak (one person, one home setup) |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

---

## 2. Data source

The data was collected by hand for this project. No existing dataset, website,
or API was used, so no third-party license or terms of service apply. I am not
aware of any public dataset that pairs shot-level espresso parameters with puck
and crema photos and a quality label. The existing espresso datasets hold
numerical experiments only and have no per-shot quality label.

---

## 3. Collection procedure

Follow these steps to collect a comparable dataset.

### 3.1 Fixed equipment

These were held constant for every shot. That leaves the variables in
§3.2 as the only intended sources of variation.

| Item | Value |
|---|---|
| Espresso machine | Gemilai Owl 3006 |
| Grinder | Turin DF54 |
| Portafilter / basket | Standard 58mm spouted portafilter |
| Water source | Crystal Geyser Spring Water |
| Brew temperature target | 203 degrees F |
| Bean storage | Roaster's Packaging |
| Scale | Standard coffee scale (0.1 gram precision) |
| Camera | iPhone 16, default camera app, flash ON |
| Photo lighting / framing | Same spot, same ambient light and flash, same framing every time, kept as close as possible |

### 3.2 Beans

Ten bags of beans, all roasted in southeast Michigan by Chazzano Coffee
Roasters or RoosRoast Coffee. Each bag gets a numeric `bean_id`. A new bag of
the same coffee gets a new `bean_id` (beans 3 and 4 are two bags from the same
roast).

| `bean_id` | Roaster | Coffee | Roast date | Shots | Kept |
|---|---|---|---|---|---|
| 1 | Chazzano | Mexico Chiapas | 2026-08-24 | 18 | 17 |
| 2 | RoosRoast | Decaf Lovers | 2026-08-09 | 9 | 8 |
| 3 | Chazzano | Mexico Chiapas | 2026-09-14 | 18 | 18 |
| 4 | Chazzano | Mexico Chiapas | 2026-09-14 | 19 | 18 |
| 5 | Chazzano | Ethiopia Harrar | 2026-09-22 | 18 | 18 |
| 6 | RoosRoast | Decaf Lovers | 2026-09-13 | 19 | 19 |
| 7 | Chazzano | Sumatra Mandheling | 2026-09-22 | 19 | 19 |
| 8 | RoosRoast | Lobster Butter | 2026-09-17 | 18 | 17 |
| 9 | Chazzano | Ethiopia Harrar | 2026-09-29 | 18 | 18 |
| 10 | Chazzano | Mexico Chiapas | 2026-09-29 | 2 | 2 |

"Shots" counts form submissions. "Kept" is after dropping shots with no puck
photo (§4).

### 3.3 Per-shot procedure

1. Pull the shot as part of normal daily coffee: usually two morning shots,
   some extra afternoon or evening shots, and longer dedicated sessions of
   4-10 shots in one sitting.
2. Deliberately vary the shot instead of always aiming for the best one. Change
   grind setting and dose, use or skip WDT, use a spring tamp or an uneven
   regular tamp, and use or skip a puck screen. Tag each shot's intent in
   `sample_tracking`:
   - `Normal Pull`: a normal dial-in shot
   - `Adjusted Grind/Dose`: grind or dose changed on purpose
   - `Defect Shot`: variation in puck prep on purpose (e.g. skip WDT, uneven tamp)
3. Record a video of the extraction (not distributed; see §6).
4. **Crema photo:** right after the shot, shoot straight down into the cup.
5. **Puck photo:** take the portafilter out without knocking out the puck and
   shoot straight down into the basket.
6. Taste the shot and rate it (the sensory columns in §5.3).
7. Fill in the Google Form (`EspressoExtractionDaily`). Upload the video and
   both photos through the form's file-upload fields. The form timestamps the
   submission automatically and uses multiple choice where it can.

---

## 4. Sampling and filtering

- **Population:** every shot logged in the form between 2026-09-09 and
  2026-10-05. Nothing was sampled at collection time: every shot pulled and
  logged in that window is included.
- **Filtering:** 4 of the 158 submissions have no puck photo (`shot_003`
  2026-09-10 06:57, `shot_061` 09-27 10:40, `shot_071` 09-28 07:30, `shot_133`
  10-03 13:23). They were dropped, leaving **154 shots**. Their crema photos
  are dropped too.
- **Intent mix (154 shots):** 54 Normal Pull, 70 Adjusted Grind/Dose, 30 Defect
  Shot. Defect shots were pulled on purpose so that channeling severity covers
  its full range. Without them almost every puck would be None or Low.
- **Annotator assignment** (the same for both tasks):
  - **Overlap set:** 40 shots, labeled by all 6 annotators and used to measure
    agreement. These are a stratified sample by `sample_tracking` (14 Normal,
    18 Adjusted, 8 Defect), so they keep the overall intent mix.
  - **Remainder:** the other 114 shots get 3 annotators each. The script cycles
    through all 20 possible 3-person groups, so every pair of annotators shares
    some items.
  - **Workload:** 95-100 shots per annotator per task (annotator_1: 100,
    annotator_2: 98, annotator_3: 97, annotator_4-5: 96, annotator_6: 95).

Collection by day. "Logged" is form submissions; "Kept" is after dropping
shots with no puck photo.

| Date | Logged | Kept | Date | Logged | Kept | Date | Logged | Kept |
|---|---|---|---|---|---|---|---|---|
| 09-09 | 2 | 2 | 09-21 | 2 | 2 | 09-29 | 11 | 11 |
| 09-10 | 2 | 1 | 09-22 | 13 | 13 | 09-30 | 15 | 15 |
| 09-14 | 4 | 4 | 09-23 | 3 | 3 | 10-01 | 10 | 10 |
| 09-15 | 2 | 2 | 09-24 | 2 | 2 | 10-02 | 10 | 10 |
| 09-16 | 4 | 4 | 09-25 | 6 | 6 | 10-03 | 14 | 13 |
| 09-17 | 2 | 2 | 09-26 | 11 | 11 | 10-04 | 5 | 5 |
| 09-18 | 2 | 2 | 09-27 | 12 | 11 | 10-05 | 14 | 14 |
| 09-19 | 2 | 2 | 09-28 | 10 | 9 | | | |

---

## 5. Dataset format

### 5.1 Repository layout

| Path | Contents | Committed |
|---|---|---|
| `images/<id>.jpg` | 308 resized photos (1200×1600, 2 are 1600×1200), named by opaque ID, about 126 MB total | yes |
| `annotators/annotator_N/1_channeling/` | [Potato](https://potatoannotator.com) task for puck photos: `config.yaml` + `data.jsonl` | yes |
| `annotators/annotator_N/2_crema/` | Potato task for crema photos | yes |
| `annotators/annotator_N/*/annotation_output/` | That annotator's labels, made by Potato (§5.4) | no (emailed back, or submitted as a pull request) |
| `prepare_data.py` | Builds `images/` and `annotators/` from the shot sheet | yes |
| `annotation_guidelines.md` | Label definitions and decision rules | yes |
| `guideline_examples/` | Example photos embedded in the guidelines, two per label (`<task>_<label>_N.jpg`) | yes |
| `README_annotators.md` | Setup and run instructions for annotators | yes |
| Shot sheet CSV | One row per shot, brew parameters (§5.3) | no (kept back during annotation so annotators stay blind; released with the final labels) |
| `PRIVATE_key.csv`, `PRIVATE_id_secret.txt`, `raw_photos/` | Opaque ID ↔ shot mapping, ID secret, original photos and videos | never |

Nothing is hosted. Each annotator runs Potato locally and loads images from
this repo's raw GitHub URLs.

### 5.2 `data.jsonl` (one line per item)

| Field | Meaning |
|---|---|
| `id` | Opaque item ID (same as the image filename without `.jpg`) |
| `image` | URL of the image Potato shows |

### 5.3 Shot sheet columns

One row per shot. The tabular columns are the model inputs. The sensory
columns are an extra label set from one taster (the collector).

| Column | Type | Meaning |
|---|---|---|
| `shot_id` | str | `shot_001`-`shot_158`, in submission order |
| `Timestamp` | datetime | Form submission time (local, M/D/YYYY H:MM:SS) |
| `session_shot_number` | int | Shot number within one sitting (1-11) |
| `bean_id` | int | Bean bag (1-10), see §3.2 |
| `days_since_roast` | int | Shot date minus the bag's roast date (§3.2), in days (4-50) |
| `ambient_temperature_f` | int | Room temperature, °F |
| `dose_target_g` | float | Planned dose, grams |
| `dose_actual_g` | float | Weighed dose, grams |
| `water_spritz` | Yes/No | Beans spritzed with water before grinding |
| `grind_setting` | float | Grinder dial setting (lower = finer) |
| `tamping_method` | cat | `Spring Tamp` or `Regular Tamp` (slightly uneven) |
| `puck_screen_used` | Yes/No | Puck screen on top of the puck |
| `wdt_used` | Yes/No | Grounds stirred with a WDT tool before tamping |
| `preheat_s` | int | Machine preheat time, seconds (120-300) |
| `target_yield_g` | int | Planned shot weight, grams (24, 30, 36, or 38) |
| `tank_drained` | Yes/No | Machine's water tank ran dry during the shot |
| `actual_yield_g` | float | Weighed shot weight, grams |
| `first_drop_time_s` | int | Seconds until the first drop |
| `shot_end_time_s` | int | Total shot time, seconds |
| `peak_pressure` | float | Peak gauge pressure, bar |
| `sample_tracking` | cat | Shot intent: `Normal Pull` / `Adjusted Grind/Dose` / `Defect Shot` |
| `extraction_video_file` | str | Extraction video file name, `<shot_id>_video.mov` in `raw_photos/extraction_video_file/` (not distributed) |
| `crema_image_file` | str | Crema photo file name, `<shot_id>_crema.<ext>` in `raw_photos/crema_image_file/` |
| `puck_image_file` | str | Puck photo file name, `<shot_id>_puck.<ext>` in `raw_photos/puck_image_file/` |
| `sourness_1_7` … `harshness_1_7` | 1-7 | Taste ratings: sourness, bitterness, sweetness, astringency, body, clarity, harshness |
| `overall_preference_1_7` | 1-7 | How much the taster liked the shot |
| `sensory_diagnosis` | cat | `under_extracted`, `balanced`, `strong_but_balanced`, `over_extracted`, `weak_or_diluted`, `uneven_or_channeling`, `ambiguous` |

### 5.4 Annotation output

Potato saves each annotator's work to
`annotation_output/<annotator>/user_state.json` and also exports JSONL to
`annotation_output/exports/`. Each record is keyed by item `id` and has these
fields:

| Task | Field | Values |
|---|---|---|
| Channeling | `channeling_features` | Any of: Pinholes, Cracks, Edge gap, Wet pooling, Uneven color, Craters / divots (may be empty) |
| Channeling | `channeling_severity` | `0 - None`, `1 - Low`, `2 - Medium`, `3 - High` (required) |
| Channeling | `channeling_confidence` | 1 (guessing) to 5 (certain) (required) |
| Channeling | `puck_image_quality` | `Image quality issue` or empty |
| Crema | `crema_extraction` | `Under`, `Balanced`, `Over` (required) |
| Crema | `crema_confidence` | 1 to 5 (required) |
| Crema | `crema_image_quality` | `Image quality issue` or empty |

To join labels back to shots, use `PRIVATE_key.csv`
(`shot_id, sample_tracking, 1_channeling_id, 2_crema_id, labeled_by`).

---

## 6. Missing data and known issues

- **Shots with no puck photo:** 4, dropped (§4).
- **Missing values in the shot sheet** (all 158 rows): only
  `extraction_video_file` for `shot_157`. Videos are not used for annotation.
  All tabular columns are complete and numeric.
- **Unbalanced beans:** bean 10 has only 2 shots and bean 2 has 9. The other
  beans have 18-19.
- **Videos** are collected but not distributed or annotated, to keep the scope
  manageable for a solo project.
- **EXIF:** most photos lost their EXIF capture time on upload, so `Timestamp`
  is the only reliable time for each shot. The 20 photos that kept it (8 puck,
  12 crema) were all taken within 90 minutes of their row's `Timestamp`, which
  supports the photo-to-shot pairing.
- **Image URLs:** `data.jsonl` points to
  `https://raw.githubusercontent.com/elliotpak2k/espresso-extraction/main/images/`,
  so images only load once `images/` is on the `main` branch.

---

## 7. Estimated labeling time

| Task | Per item | Why |
|---|---|---|
| Puck (channeling) | **~15-25 s** | Scan the whole puck, tell real flaws from screen imprint and glare, tick up to 6 features, apply the worst-area and bump-up rules, then set confidence. Zooming in on borderline pucks adds time. |
| Crema (extraction) | **~8-12 s** | Mostly a color judgment against the guideline examples. Coverage and bubbles only matter for close calls. |
| One-time overhead | ~10 min | Read the guidelines (~5 min) and install Potato (~5-10 min) |

At these rates one annotator's share (about 97 shots × 2 tasks) takes about
**40-60 minutes** plus setup: 25-40 minutes for pucks and 13-20 minutes for
crema. All 1,164 labels take about 4-6 annotator-hours. These numbers come from
the task design.

---

## 8. License

The dataset (images, shot sheet, and annotations) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE).
