# Signal Processing for Heart Sound Localization (EE2L1 IP-3)

This repository contains the implementation and experimental results of the **EE2L1 IP-3 project: Heart Sound Localization**, a Bachelor Electrical Engineering project at TU Delft.

The goal of the project is to **localize heart valve activity** using audio signals recorded by a **microphone array placed on the chest**, combining signal processing, modeling, and array processing techniques.

---

## Project overview

Heart sounds (phonocardiograms, PCG) are captured using multiple microphones.  
The system processes these signals to:
- segment individual heart sounds (S1, S2),
- model heart valve acoustics,
- estimate the **direction of arrival (DoA)** of heart sounds,
- localize valve activity using beamforming and subspace methods.

The system is structured into **four modules**, each addressing a specific stage of the pipeline.

---

## Module structure

### Module 1 — Segmentation
Pre-processing and segmentation of PCG signals:
- band-pass filtering and downsampling,
- Shannon energy envelope computation,
- peak detection and classification into S1 / S2 sounds,
- robustness against noise and missing peaks.

### Module 2 — Heart sound modeling
Synthetic modeling of heart sounds:
- valve impulse response modeling,
- multi-valve signal synthesis,
- spatial delay and attenuation per microphone,
- generation of realistic multi-channel test data.

### Module 3 — Direction finding
Classical array processing methods:
- Matched (delay-and-sum) beamforming,
- MVDR beamforming,
- frequency selection trade-offs (resolution vs aliasing),
- evaluation on single- and multi-source scenarios.

### Module 4 — Advanced localization
High-resolution localization using subspace methods:
- SVD-based signal/noise subspace separation,
- MUSIC algorithm for DoA estimation,
- comparison with beamforming approaches.

---

## Repository structure

```text
.
├── src/                # Source code per module / chapter
│   ├── module_1/
│   ├── module_2/
│   ├── module_3/
│   └── module_4/
├── lib/                # Shared utilities (signal processing, plotting, IO)
├── docs/               # Documentation, reports, manuals
│   └── _general/
├── samples/            # Audio samples and datasets
├── requirements.txt    # Python dependencies
└── README.md
