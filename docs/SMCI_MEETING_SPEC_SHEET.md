# SMCI Meeting - Personal Compute
**Dec 13, 2024 | 3-Chassis System | Sovereign Compute**

---

## Hardware

### Chassis 1: CPU Node
| Component | Spec |
|-----------|------|
| CPU | AMD EPYC 9965 Turin |
| RAM | 2TB DDR5 ECC |
| Storage | 2x 15TB NVMe |
| Power | 2x 2600W redundant |

### Chassis 2: GPU Node
| Component | Spec |
|-----------|------|
| GPU | 2x AMD MI325X (256GB HBM3e each, 512GB total) |
| RAM | 128GB DDR5 |
| Power | 2x 2600W redundant |

*Full chassis = 8x MI325X*

### Chassis 3: Storage Node
| Component | Spec |
|-----------|------|
| Storage | Tiered (NVMe + HDD + Petabyte tier) |
| Network | High-speed fabric |
| Purpose | Data lake, CDC events, video feeds, bulk storage |

---

## Use Cases

1. **LLM Inference + Fine-Tuning** — 7B→405B models, multi-model orchestration
2. **Model Orchestration** — Sparse trees of cheap 7B models for context narrowing before expensive inference (21 questions approach)
3. **Image/Video Gen** — SD, SDXL, Flux, batch production
4. **Speech** — Whisper large-v3, real-time streaming, voice cloning
5. **Computer Vision** — Real-time multi-stream analysis, custom training
6. **Research** — Novel architectures, multi-modal, RL experiments

---

## Questions for SMCI

1. MI325X availability/lead time?
2. Cooling requirements for MI325X?
3. Storage expansion options?
4. Network fabric recommendations?
5. Support/warranty terms?

