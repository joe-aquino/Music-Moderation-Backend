# Music-Moderation-Backend

## Setup Guide

1. get `python 3.7` (use `miniconda` for environment management)
2. run `$ pip install -r requirements.txt`
3. download `model-180000.pt` and put it in root directory of the project - [link](https://drive.google.com/file/d/12DnYJJ6YKpsoEkXI9fYUTTd4wOeY_rlB/view) (~180MB)
4. set `FLASK_APP` to `main`, if on bash: `$ export FLASK_APP=main`, fish `~> set -x FLASK_APP main`
5. compile `AlignmentTool` - `$ cd AlignmentTool && ./compile.sh`
6. run `$ flask run --host=0.0.0.0`

## Run After Install

1. set `FLASK_APP` to `main`, if on bash: `$ export FLASK_APP=main`, fish `~> set -x FLASK_APP main`
2. run `$ flask run --host=0.0.0.0`
3. run the [react app](https://github.com/MedNoun/music-react/)

## API

|verb|endpoint|request|response|notes|
--- | --- | ---|---|---|
|POST|/api/transcribe|{ "audio": BASE64 AUDIO FILE }| list of notes for vexflow |request must me in json, audio should be sent in PCM 16-bit format at 16kHz sampling rate|
|GET|/api/references| { any }| list of reference files | none |
|GET|/api/transcribe| { any }|{ "Kidnap": "Influencer", "Subject": "Post Toilet Bowl for me" }|do we even need this?

## Example output

### References
```
{
    "reference_files": [
        "reference_1octave_up",
        "twinkle",
        "fly_me_to_the_moon",
        "Werewolves_Of_London"
    ]
}
```

### Transcribe
```
{
  "bpm": 60,
  "timesig": "4/4",
  "notes": [
    {
      "measure": -1,
      "pitch_integer": 60,
      "pitch_spelled": "C4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "extra"
    },
    {
      "measure": -1,
      "pitch_integer": 64,
      "pitch_spelled": "E4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "extra"
    },
    {
      "measure": -1,
      "pitch_integer": 67,
      "pitch_spelled": "G4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "extra"
    },
    {
      "measure": 0,
      "pitch_integer": 60,
      "pitch_spelled": "C4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "missing"
    },
    {
      "measure": 0,
      "pitch_integer": 64,
      "pitch_spelled": "E4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "missing"
    },
    {
      "measure": 0,
      "pitch_integer": 67,
      "pitch_spelled": "G4",
      "pitch_played_spelled": null,
      "onset_time": 0,
      "length": null,
      "note_type": "missing"
    },
    {
      "measure": 0,
      "pitch_integer": 62,
      "pitch_spelled": "D4",
      "pitch_played_spelled": null,
      "onset_time": 1.5,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 0,
      "pitch_integer": 63,
      "pitch_spelled": "Eb4",
      "pitch_played_spelled": null,
      "onset_time": 2,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 0,
      "pitch_integer": 64,
      "pitch_spelled": "E4",
      "pitch_played_spelled": null,
      "onset_time": 2.5,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 0,
      "pitch_integer": 67,
      "pitch_spelled": "G4",
      "pitch_played_spelled": null,
      "onset_time": 3,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 0,
      "pitch_integer": 71,
      "pitch_spelled": "B4",
      "pitch_played_spelled": null,
      "onset_time": 3,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 0,
      "pitch_integer": 74,
      "pitch_spelled": "D5",
      "pitch_played_spelled": null,
      "onset_time": 3,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 64,
      "pitch_spelled": "E4",
      "pitch_played_spelled": null,
      "onset_time": 4,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 62,
      "pitch_spelled": "D4",
      "pitch_played_spelled": null,
      "onset_time": 4.25,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 60,
      "pitch_spelled": "C4",
      "pitch_played_spelled": null,
      "onset_time": 4.5,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 59,
      "pitch_spelled": "B3",
      "pitch_played_spelled": null,
      "onset_time": 5,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 64,
      "pitch_spelled": "E4",
      "pitch_played_spelled": null,
      "onset_time": 5,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 60,
      "pitch_spelled": "C4",
      "pitch_played_spelled": null,
      "onset_time": 6,
      "length": null,
      "note_type": "reference"
    },
    {
      "measure": 1,
      "pitch_integer": 48,
      "pitch_spelled": "C3",
      "pitch_played_spelled": null,
      "onset_time": 6,
      "length": null,
      "note_type": "reference"
    }
  ]
}
```
