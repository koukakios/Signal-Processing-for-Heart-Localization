from pathlib import Path

CONFIG_PATH = Path.cwd() / "config.ini"

DEFAULT_CONFIG = {
    "LowpassFilter": {
        "FilterOrder": 2,
        "LowFrequency": 10,
        "HighFrequency": 800,
        "Size": 5000
    },
    "Downsampling":{
        "FsTarget": 4000
    },
    "Energy":{
        "FilterOrder": 2,
        "CutoffFrequency": 7,
        "Size": 1000
    },
    "Segmentation": {
        "MinHeight": 0.3,
        "MinDist": 0.23,
        "EnvelopeThreshold": 0.1,
        "SolveUncertainLength": 2,
        "OutputPath": "generated/segmentation",
        "ConcatPath": "without zeros",
        "SegmentedPath": "with zeros",
        "MaxUncertainCountPerMin": 20,
        "MaxCompHeight": 1,
        "MaxCompIter": 100,
    },
    "HeartSoundModel": {
        "Fs": 48000,
        "BPM": 66,
        "NBeats": 200,
    },
    "Generation": {
        "SoundsPath": "generated/hearbeat model"
    },
    "Multichannel": {
        "V_body": 60
    }
}

DEFAULT_COMMENTS = {
    "LowpassFilter": ["# Properties of the lowpass filter"],
    "Downsampling": ["# Parameters for downsampling"],
    "Energy": ["# Properties of the lowpass filter for building the Shannon energy envelope"],
    "Multichannel": ["# m/s, speed of sound through body"]
}