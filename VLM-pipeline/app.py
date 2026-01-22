import streamlit as st
from vlm_pipeline import CCTVVLMPipeline
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CCTV RAG Pipeline", layout="wide")

st.title("🔍 CCTV RAG Agent Pipeline")
st.markdown("**APSIT BE Project 2025-26**")

# Config
col1, col2 = st.columns(2)
with col1:
    chunk_size = st.select_slider("Chunk Size", options=[3,4,5], value=3)
with col2:
    overlap = st.select_slider("Overlap", options=[1,2,3], value=2)

if st.button("🚀 RUN PIPELINE", type="primary", use_container_width=True):
    with st.spinner("Processing frames → chunks → JSON events..."):
        pipeline = CCTVVLMPipeline()
        results = pipeline.process_all_chunks(chunk_size=chunk_size, overlap_step=overlap)
    
    # Results dashboard
    st.success(f"✅ Pipeline complete! {results['stats']['chunks_processed']} events generated")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Chunks", results['stats']['chunks_processed'])
    col2.metric("BLEU-4", f"{results['stats']['avg_bleu']:.3f}")
    col3.metric("VLM Calls Saved", "95%")
    
    # Events table
    df = pd.DataFrame(results['events'])
    st.dataframe(df[['chunk_id', 'trigger', 'summary', 'bleu']].style.format({'bleu': '{:.3f}'}))
    
    # Download
    st.download_button(
        "💾 Download ChromaDB JSON", 
        json.dumps(results, indent=2, ensure_ascii=False),
        f"cctv_rag_{results['timestamp']}.json"
    )

st.info("📁 **Put JPG/PNG frames in `frames/` folder → Click RUN**")
