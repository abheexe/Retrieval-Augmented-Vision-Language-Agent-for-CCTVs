import json, time, os, re, numpy as np
from pathlib import Path
from PIL import Image
import nltk
nltk.download('punkt', quiet=True)
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

class CCTVVLMPipeline:
    def __init__(self, frames_dir="frames", gt_path="gt_captions.json"):
        self.frames_dir = Path(frames_dir)
        self.gt_path = gt_path
        self.activity_history = []
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self.gt_captions = self.load_gt()
    
    def compute_bleu(self, gt_texts, pred_text):
        try:
            return sentence_bleu([c.split() for c in gt_texts], pred_text.split(),
                               weights=(0.25,0.25,0.25,0.25),
                               smoothing_function=SmoothingFunction().method1)
        except:
            return 0.0
    
    def load_gt(self):
        if os.path.exists(self.gt_path):
            with open(self.gt_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_frame_files(self):
        jpg_files = list(self.frames_dir.glob("*.jpg"))
        png_files = list(self.frames_dir.glob("*.png"))
        return sorted(jpg_files + png_files)
    
    def create_cctv_chunk(self, start_idx, chunk_size=3, track_id="person_47"):
        frame_files = self.get_frame_files()
        if start_idx + chunk_size > len(frame_files):
            return None
        
        chunk_frames = frame_files[start_idx:start_idx+chunk_size]
        frames = [Image.open(f).resize((512,512)) for f in chunk_frames]
        timestamps = [f"10:30:{15+start_idx+i*3:02d}" for i in range(chunk_size)]
        
        base_x = 100 + start_idx * 25
        positions = [[base_x+i*70, 200, 80, 180] for i in range(chunk_size)]
        
        trigger = "new_track" if start_idx == 0 else "activity_change" if start_idx%4==0 else "periodic"
        chunk_id = f"chunk_{start_idx//2:02d}"
        
        return {
            "chunk_id": chunk_id, "track_id": track_id, "frames": frames,
            "timestamps": timestamps, "positions": positions,
            "history": ["Person47 entered server room", "Person47 near equipment"],
            "trigger": trigger, "frame_names": [f.name for f in chunk_frames]
        }
    
    def get_chunks(self, chunk_size=3, overlap_step=2):
        frame_files = self.get_frame_files()
        print(f"📁 Found {len(frame_files)} frames")
        
        chunks = []
        for i in range(0, len(frame_files)-chunk_size+1, overlap_step):
            chunk = self.create_cctv_chunk(i, chunk_size)
            if chunk: 
                chunks.append(chunk)
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def vlm_simulate(self, chunk):
        """🎭 SIMULATE VLM - Perfect JSON matching your spec"""
        # Your EXACT JSON output format
        pred_json = {
            "track_id": chunk['track_id'],
            "event_id": f"evt_{chunk['chunk_id'][-2:]}",
            "timestamp_start": chunk['timestamps'][0],
            "timestamp_end": chunk['timestamps'][-1],
            "duration_s": len(chunk['timestamps']) * 3,
            "activity": "walked from corner to door",
            "direction": "left_to_right",
            "speed_mps": 0.3,
            "confidence": 0.92,
            "objects": ["server rack", "door", "chair"],
            "scene": "server_room",
            "natural_summary": f"Person47 walked purposefully from NW corner toward exit door in {chunk['chunk_id']}",
            "search_tags": ["person_movement", "exit_intent", "server_room"],
            "embedding_text": f"Person47 walking from corner to door in server room {chunk['timestamps'][0]}"
        }
        
        pred_summary = pred_json['natural_summary']
        pred_text = re.sub(r'[{}",:\[\]]', ' ', json.dumps(pred_json)).lower()
        
        first_frame = chunk["frame_names"][0]
        gt_texts = self.gt_captions.get(first_frame, ["Person moving in server room"])
        bleu_score = self.compute_bleu(gt_texts, pred_text)
        
        # Update temporal memory
        self.activity_history.append(pred_summary)
        
        return {
            'chunk_id': chunk['chunk_id'],
            'summary': pred_summary,
            'json': pred_json,
            'bleu': float(bleu_score),
            'latency': 0.05,
            'gt': gt_texts[0],
            'trigger': chunk['trigger']
        }
    
    def process_all_chunks(self, model_id="DemoVLM", chunk_size=3):
        chunks = self.get_chunks(chunk_size)
        if not chunks:
            raise ValueError("❌ No frames found! Add JPG/PNG files to frames/ folder")
        
        print(f"🚀 Processing {len(chunks)} chunks with {model_id}...")
        all_results = []
        
        for i, chunk in enumerate(chunks):
            result = self.vlm_simulate(chunk)
            all_results.append(result)
            
            print(f"✅ [{i+1}/{len(chunks)}] {result['chunk_id']}: {result['summary'][:60]}...")
            print(f"   Trigger: {result['trigger']} | BLEU: {result['bleu']:.3f}")
        
        # Save YOUR exact JSON format
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"cctv_rag_results_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'model': model_id,
                'project': 'APSIT BE CCTV RAG 2025-26',
                'total_frames': len(self.get_frame_files()),
                'chunks': len(all_results),
                'pipeline': 'YOLOv8+DeepSORT → VLM → ChromaDB',
                'results': all_results
            }, f, indent=2)
        
        print(f"\n💾 SAVED: {output_file}")
        print(f"📊 Chunks processed: {len(all_results)} | Ready for ChromaDB+RAG!")
        return all_results
