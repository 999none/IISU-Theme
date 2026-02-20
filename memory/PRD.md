# iiSU White UI — Nintendo 3DS Custom Theme

## Original Problem Statement
Generate static Nintendo 3DS custom theme assets for "iiSU White UI" — a minimal white interface theme inspired by the iiSU Network design language. Deliverables: top.png (412x240), bottom.png (320x240), preview.png, body_LZ.bin, info.smdh. Anemone3DS compatible. Author: "none". BGM excluded. Preview page with download button added in iteration 2.

## Architecture
- **Asset generation:** Python/Pillow script (`generate_theme.py`)
- **Backend:** FastAPI serving ZIP download (`/api/download`) and asset files
- **Frontend:** React single-page preview with download button
- **Database:** Not used (no MongoDB needed)

## What's Been Implemented
### Iteration 1 (Feb 20, 2026)
- Generated all 5 theme assets: top.png, bottom.png, preview.png, body_LZ.bin, info.smdh
- ZIP package at `/app/iiSU_White_UI.zip`
- README_BUILD.md with YATA+/Usagi/3DS Theme Editor instructions

### Iteration 2 (Feb 20, 2026)
- Preview page displaying top.png, bottom.png, combined preview
- "Download Theme (.zip)" button with #7C8CFF accent, rounded pill shape, soft shadow, hover glow
- Metadata card with theme info and color palette swatches
- FastAPI backend serving `/api/download` endpoint
- **Testing: 100% pass (5/5 backend, 15/15 frontend)**

## Prioritized Backlog
- P1: Generate real body_LZ.bin (requires YATA+/3DS Theme Editor)
- P1: Generate proper info.smdh with icon images (requires smdhtool)
- P2: Add BGM (bgm.bcstm) if desired
- P2: Theme Plaza upload preparation
