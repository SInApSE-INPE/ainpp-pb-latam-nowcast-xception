# Xception validation record

Recorded October 21, 2026.

## Checkpoint and technical checks

The supplied checkpoint loaded strictly into the reference architecture.
The versioned inference bundle contains only tensor weights and matching
mean/std files, with SHA-256 values in its manifest. Normalization files
match the originals referenced by the source script.

Six initial tests passed, covering exact reference equivalence on a
64 × 64 deterministic input, 4D/5D input support, model output leads,
rejection of incompatible weights or horizons, georeferenced GeoTIFFs,
atomic publication, and idempotent scheduling. Ruff passed. The service
and timer were rendered and passed `systemd-analyze verify`; neither was
installed or activated. The model matched the reference exactly with the same weights (`rtol=atol=0`). The six leads are predicted in one pass. The inference bundle loads with `weights_only=True` and `strict=True`; the original checkpoint is preserved.

A full-grid run with **12 synthetic GSMaP binaries** and the real checkpoint
produced six 880 × 970, EPSG:4326, float32 GeoTIFFs in mm/h. Reopened files
had the expected UTC leads and finite nonnegative values. The run included
a −99 input value, clamped to zero before normalization. Temporary synthetic
inputs were removed. These results demonstrate software behavior, **not
meteorological forecast quality**.

Synthetic results: `outputs/validation-synthetic/xception/gsmap_now/2000/01/01/1100Z/`. All outputs also passed bounds and manifest SHA-256 checks, with no masked pixels.

## Environment and open validation

The earlier full-grid run used CPU with PyTorch 2.10.0+cu128, torchvision 0.25.0+cu128, and timm 1.0.25 from an existing environment, plus rasterio from the ARAFNO environment. Those environments were not modified. ARAFNO's 29 tests passed in its own environment, with PyTorch 2.14.1+cpu.

A clean installation from the lock was not completed in the initial offline
session because the required CPU PyTorch wheel was unavailable or online
dependency retrieval failed through DNS. Run `uv sync --locked` with access
to the configured package indexes before operational use. The lock itself
passed `uv lock --offline --check`.

Real JAXA FTP, GPU inference, and the active systemd service were not tested
at this stage. Training latitude order remains unverified, and the NRT-to-NOW
input change requires meteorological evaluation. The normalized-space ReLU and its approximate 0.0453 mm/h inverse-transform floor also need scientific review.

## Independent distribution

Acquisition, processing, publication, and scheduling are embedded in
`src/xception_nowcast/_runtime/` and packaged in this model's wheel.
`uv lock --offline` and `uv build --offline` passed before the retention
change. The inspected wheel contains all 11 private runtime modules and
has no dependency on `nowcasting-runtime` or `../shared`. Importing the
runtime from an extracted wheel outside the checkout passed. The six
initial tests passed again. Changes needed by multiple independent models
must be applied to each one.

## Temporary download retention

FTP inputs now default to the system temporary directory, isolated by user
and model. The default 24-hour retention is configurable with
`--cache-ttl-hours`. Cleanup removes expired managed downloads on each FTP
run or scheduled poll, including polls with no new forecast, and preserves
local inputs.

**Eight tests passed** after this change; Ruff and
`uv lock --offline --check` passed. The Xception project environment was used for these tests. The current offline
wheel rebuild could not run because `hatchling` was missing from the build
cache; the previous build had passed.

## Docker deployment — October 22, 2026

The independent CPU image, Compose service, startup checkpoint verification, retry loop, polling interval, and bind mounts were added. Twenty tests passed, including container retry and configuration tests. Ruff checks, formatting, lock consistency, and static Compose/context validation passed. The image could not be built here: the Docker command is backed by Podman, which cannot initialize its state on the read-only `/run/user` filesystem. A live Docker build, checkpoint HTTP fetch, and JAXA FTP poll remain to be verified on the deployment host.
