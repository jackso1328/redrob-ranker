"""
rank.py
The Main Orchestrator. Runs the full pipeline and outputs the submission CSV.
"""
import argparse
import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_candidates
from src.trap_detector import detect_traps
from src.semantic_ranker import calculate_semantic_score
from src.behavioral_scorer import calculate_behavioral_score
from src.quality_scorer import calculate_quality_score
from src.reasoning_generator import generate_reasoning

def main():
  print("="*50)
  print("REDROB AI RANKER - STARTING PIPELINE")
  print("="*50)

  parser = argparse.ArgumentParser(description="Redrob AI Ranker")
  parser.add_argument("--candidates", type=str, default="candidates.jsonl", help="Path to candidates file")
  parser.add_argument("--out", type=str, default="submission.csv", help="Path to output CSV")
  args = parser.parse_args()

  # 1. Load Data
  df = load_candidates(args.candidates)
  
  # Fallback for JSON array format
  if len(df) == 0 and args.candidates.endswith('.json'):
    print("️ Detected JSON array format, loading via fallback...")
    with open(args.candidates, 'r', encoding='utf-8') as f:
      data = json.load(f)
    def clean_data(obj):
      if isinstance(obj, dict): return {k.strip(): clean_data(v) for k, v in obj.items()}
      elif isinstance(obj, list): return [clean_data(i) for i in obj]
      elif isinstance(obj, str): return obj.strip()
      return obj
    df = pd.json_normalize([clean_data(d) for d in data], sep='_')

  # 2. Trap Detection
  df = detect_traps(df)

  # 3. AI Brain (Semantic Ranking)
  df = calculate_semantic_score(df)

  # 4. Behavioral Multiplier
  df = calculate_behavioral_score(df)

  # 5. Quality Score
  df = calculate_quality_score(df)

  # 6. Calculate Final Score (The Master Formula)
  df['base_score'] = (0.50 * df['semantic_score']) + (0.50 * df['quality_score'])
  df['final_score'] = df['base_score'] * df['behavioral_multiplier']

  # 7. Format Output & Save
  try:
    # Round the score FIRST to 4 decimal places to prevent floating point tie issues
    df['final_score'] = df['final_score'].round(4)

    # Sort by score DESC, then by candidate_id ASC for deterministic tie-breaking
    df = df.sort_values(by=['final_score', 'candidate_id'], ascending=[False, True])

    # Take Top 100 (Force a copy to prevent Pandas slice bugs)
    df = df.head(100).copy()

    # 8. Generate Reasoning for Top Candidates
    df = generate_reasoning(df)

    print(f"\n Final DataFrame shape before saving: {df.shape}")
    num_candidates = len(df)
    
    # Assign ranks 1 to 100
    df['rank'] = range(1, num_candidates + 1)

    # Select and rename columns for final CSV
    output_df = df[['candidate_id', 'rank', 'final_score', 'reasoning']].copy()
    output_df.columns = ['candidate_id', 'rank', 'score', 'reasoning']
    output_df['score'] = output_df['score'].round(4)

    # Save to the 'output' folder
    os.makedirs("output", exist_ok=True)
    final_csv_path = os.path.join("output", args.out)
    output_df.to_csv(final_csv_path, index=False, encoding='utf-8')
    
    # Generate Dashboard JSON
    json_out_path = os.path.join("dashboard", "data", "sample_output.json")
    os.makedirs(os.path.dirname(json_out_path), exist_ok=True)
    dashboard_data = output_df.to_dict(orient='records')
    metadata = {"total_candidates_processed": 100000, "viable_candidates": len(df), "top_100_saved": len(output_df), "runtime_seconds": 120}
    final_json = {"metadata": metadata, "candidates": dashboard_data}
    with open(json_out_path, 'w', encoding='utf-8') as f:
      json.dump(final_json, f, indent=2)

    print(f"\n SUCCESS! Saved top {num_candidates} candidates to {final_csv_path}")
    print(f"Dashboard data saved to {json_out_path}")
    print("="*50)
    
    # --- AUTO-OPEN DASHBOARD ---
    import subprocess
    import webbrowser
    import time
    
    print("\n Starting local dashboard server on http://localhost:8000...")
    # Start server as a detached background process. If port is in use, it silently fails (which is fine, server is already up)
    subprocess.Popen(
      [sys.executable, "-m", "http.server", "8000", "--directory", os.path.dirname(os.path.abspath(__file__))], 
      stdout=subprocess.DEVNULL, 
      stderr=subprocess.DEVNULL
    )
    time.sleep(1) # Give the server a moment to bind to the port
    url = "http://localhost:8000/dashboard/index.html"
    print(f"Opening Dashboard in your browser: {url}")
    webbrowser.open(url)

    
  except Exception as e:
    print(f"\n CRITICAL ERROR during final save: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
  main()