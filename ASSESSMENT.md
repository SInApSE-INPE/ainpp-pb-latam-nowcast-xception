# Xception artifact assessment

Date: October 21, 2026.

This records the assessment made **before** implementation. The operational
pipeline now exists; see [README.md](README.md) and
[VALIDATION.md](VALIDATION.md).

**Conclusion:** the essential artifacts were present and compatible with an
ARAFNO-style operational pipeline. This stage evaluated the supplied
references; it did not yet create the Xception package.

## Available material

| File | Purpose | Check |
|---|---|---|
| `xception.py` | timm Xception encoder and U-Net decoder | Architecture instantiated and matched the weights |
| `best_model.pth` | Training checkpoint | `model_state_dict` loaded with `strict=True`, no missing or unexpected keys |
| `gsmap_nrt+mvk_log_mean_ainpp-latin-america.npy` | Log-space mean | Finite scalar: 0.04431336373090744 |
| `gsmap_nrt+mvk_log_std_ainpp-latin-america.npy` | Log-space standard deviation | Positive scalar: 0.21803349256515503 |
| `Optimized_Inference.py` | Sequence, domain, inverse-transform contract | Valid syntax; inference reference available |

## Confirmed contract

- Input: **12 hourly observations**, one channel each.
- Output: **six future hours in one pass**, shaped
  `[batch, 6, 1, height, width]`. ARAFNO's autoregressive rollout does
  not apply.
- `encoder.body.conv1.weight` and `outc.weight` matched the
  checkpoint's training arguments for input and output channels.
- The reference covers LATAM at 880 × 970 pixels with west −120°,
  south −55°, east −23°, and north 33°.
- The inverse transform is `max(expm1(x * std + mean), 0)`; operational
  input must use `log1p` and z-score with the same statistics.
- The checkpoint records 320 × 320 training patches at spatial stride 160.
  Reference inference uses the full grid. Both shapes passed technical
  tests, but this does not establish scientific equivalence between
  patch-based and full-grid inference.

## Checks performed

Existing environment: PyTorch **2.10.0+cu128** and timm **1.0.25**, run on CPU.

1. Both Python scripts passed syntax checking.
2. The architecture was created with `pretrained=False`, avoiding an
   ImageNet download for weights that would be replaced by the checkpoint.
3. All weights loaded strictly into the original architecture. The tested
   timm version redirects `xception` to `legacy_xception`.
4. A synthetic 64 × 64 input produced finite output of the expected shape.
5. Inputs representing normalized zero rainfall ran at 320 × 320 and
   880 × 970, with finite outputs of the expected shapes.

These checks established compatibility and execution, not forecast skill.
NOW acquisition and Xception GeoTIFF export had not yet been implemented
at this assessment stage.

## Distribution considerations

- The approximately **664 MiB** checkpoint includes model and optimizer
  weights, scheduler, scaler, metrics, and training arguments. Model
  tensors occupy about **221 MiB**. The inference bundle can hold only
  `state_dict` plus metadata and checksums, while preserving the original.
- NumPy scalars in the checkpoint's training metadata required an explicit
  allowlist (`scalar`, `dtype`, float32/float64 types) with
  `weights_only=True`. `weights_only=False` was unnecessary. Extracting
  a pure state dict removes that dependency from operational loading.
- Pin compatible timm, PyTorch, and torchvision versions.
- Reuse the established NOW acquisition, negative-value clamping before
  normalization, GeoTIFF export, manifests, retry policy, locks, and
  scheduling. The checkpoint determines the 12-hour input window.
- Adapt the entrypoint to six direct outputs. The native horizon is six;
  do not extend it automatically with ARAFNO-style rollout.
- Keep one operational configuration and separate versioned artifacts
  from the supplied references. Shared transport, georeferencing, and
  scheduling code should not diverge between models.

## Scientific questions

1. **Latitude order:** the checkpoint does not record row order. The
   reference creates increasing coordinates, which does not prove the
   source training data's order. A georeferenced Zarr sample or its
   preparation code would resolve this.
2. **Input product:** the reference uses NRT. Operational NOW follows
   the project choice but needs skill evaluation for Xception.
3. **Normalized-space ReLU:** the architecture applies ReLU before
   returning predictions. With the supplied mean, inverse
   normalization has a floor of
   `expm1(mean) ≈ 0.0453099 mm/h` even when network output is zero.
   This differs from clamping negative physical rainfall. Preserve
   reference behavior until training intent has been checked.

No essential file was missing for implementation. These open questions
affect operational meteorological validation, not weight compatibility
with the supplied architecture.
