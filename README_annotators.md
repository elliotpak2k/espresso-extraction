# Espresso Puck Channeling: Annotator Instructions

Thanks for helping! You'll label about 100 espresso shots in two parts:

1. **Channeling:** about 100 photos of used espresso pucks
2. **Crema:** about 100 photos of the crema on top of the shot

Do Part 1 first, then Part 2. Expect ~10 min setup, ~30 min for Part 1, and ~15 min for Part 2.

## 1. Read the guidelines first (~5 min)

Read [annotation_guidelines.md](https://github.com/elliotpak2k/espresso-extraction/blob/main/annotation_guidelines.md). It explains every label and has example photos.

## 2. Setup (~5-10 min, needs Python 3.10+)

```
git clone https://github.com/elliotpak2k/espresso-extraction.git     # or Code -> Download ZIP
cd espresso-extraction
pip install -U potato-annotation
```

**If `pip install` fails** (for example with an `externally-managed-environment`
error), or you'd rather not install Potato globally, use a virtual environment
instead. From the `espresso-extraction` folder:

```
python -m venv .venv
.venv\Scripts\activate          # Windows (Command Prompt or PowerShell)
source .venv/bin/activate       # macOS / Linux
pip install -U potato-annotation
```

Activate the venv again in every new terminal before running `potato start`
(including Part 2 and when you resume later). If PowerShell refuses to run the
activate script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
first, or use Command Prompt.

**Windows only:** in the same terminal, run this before `potato start`, or
Potato can crash while printing emoji to the console:

```
set PYTHONUTF8=1                # Command Prompt
$env:PYTHONUTF8 = "1"           # PowerShell
```

If the `potato` command is not found or is blocked, use
`python -m potato start config.yaml -p 8000` instead.

## 3. Part 1: Channeling

Find your name below to get your folder and login:

| Annotator | Folder | Login |
|---|---|---|
| Valentina Bustamante | `annotators/annotator_1_valentina_bustamante/` | `annotator_1` |
| Khurram Shafique | `annotators/annotator_2_khurram_shafique/` | `annotator_2` |
| Luke Stemmerich | `annotators/annotator_3_luke_stemmerich/` | `annotator_3` |
| Raafat Saeed | `annotators/annotator_4_raafat_saeed/` | `annotator_4` |
| Shaun Sarcona | `annotators/annotator_5_shaun_sarcona/` | `annotator_5` |
| Venkat Repaka | `annotators/annotator_6_venkat_repaka/` | `annotator_6` |

The examples below use annotator_3 (Luke Stemmerich); substitute your own
folder and login:

```
cd annotators/annotator_3_luke_stemmerich/1_channeling
potato start config.yaml -p 8000
```

Open [http://localhost:8000](http://localhost:8000) and log in as `annotator_3` (no password).
Images load from the internet, so stay online.

For each puck photo (click the photo to zoom):

1. Tick every feature you see in the checklist.
2. Press 1-4 for severity: `1` = None, `2` = Low, `3` = Medium, `4` = High.
3. Click your confidence (1 = guessing, 5 = certain).
4. Tick "Image quality issue" if the photo is too blurry or dark to judge.

When you finish them all, stop the server (Ctrl+C).

## 4. Part 2: Crema

```
cd ../2_crema
potato start config.yaml -p 8000
```

Log in as `annotator_3` again. For each crema photo:

1. Press 1-3: `1` = Under, `2` = Balanced, `3` = Over.
2. Click your confidence (1-5), and tick "Image quality issue" if needed.

You can close the browser and resume later in either part; progress is saved.

## 5. Send your results back

When both parts are done, stop the server (Ctrl+C), then zip your whole
`annotators/annotator_3_luke_stemmerich/` folder (it contains both `annotation_output/`
folders) and email it to etpak@umich.edu.

Questions or problems: etpak@umich.edu / @elliotpak on Discord