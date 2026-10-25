"""Page 9: Model Registry - Checkpoint governance, metadata, and validation status."""

import os
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
import pandas as pd
from traffic_ai.dashboard.data_access import load_model_metadata


def render_page():
    st.markdown("## 🗄️ Model Registry & Checkpoint Governance")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>ARTIFACT REGISTRY · VERSIONED CHECKPOINTS</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    models_dir = Path("artifacts/models")
    models_dir.mkdir(parents=True, exist_ok=True)

    checkpoints = list(models_dir.glob("*.zip"))

    if checkpoints:
        data = []
        for p in checkpoints:
            stat = p.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            size_kb = round(stat.st_size / 1024.0, 1)
            is_best = "dqn_best" in p.name
            data.append({
                "Filename": p.name,
                "Algorithm": "Stable-Baselines3 DQN",
                "Size": f"{size_kb} KB",
                "Modified": mod_time,
                "Validation Status": "⭐ BEST VALIDATED" if is_best else "ARCHIVED",
                "Path": str(p),
            })

        st.markdown("### 📦 Available Checkpoint Artifacts")
        st.dataframe(pd.DataFrame(data), use_container_width=True)

        selected_ckpt = st.selectbox("Inspect Checkpoint", [d["Filename"] for d in data])

        col_arch, col_meta = st.columns(2)
        with col_arch:
            st.markdown("### 🧬 Architecture Specification")
            st.markdown(
                """
                <div class='kpi-card'>
                    <div class='kpi-label'>Network Topology</div>
                    <div style='color:#F9FAFB; font-size:0.85rem; line-height:1.6;'>
                        • <b>Framework:</b> Stable-Baselines3 (PyTorch backend)<br>
                        • <b>Policy:</b> Multi-Layer Perceptron (MlpPolicy)<br>
                        • <b>Hidden Layers:</b> [128, 128] with ReLU activations<br>
                        • <b>Observation Space:</b> 25 continuous features (Box[0, 1])<br>
                        • <b>Action Space:</b> 4 discrete actions (Discrete(4))<br>
                        • <b>Target Update:</b> Polyak averaging / Periodic (tau=1.0)<br>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_meta:
            meta = load_model_metadata()
            st.markdown("### 📋 Training Parameters")
            if meta:
                st.json(meta)
            else:
                st.info("No JSON metadata found for this checkpoint.")
    else:
        st.info("No model checkpoints found in 'artifacts/models/'. Train a model in the Training Center.")
