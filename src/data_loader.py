"""
src/data_loader.py
Handles ultra-fast JSONL parsing and bulletproof data cleaning.
"""
import pandas as pd
import json
import time
from tqdm import tqdm

def clean_data(obj):
  """
  Recursively strips whitespace from all dictionary keys and string values.
  This protects us against the 'Dirty Data' trap in the hackathon JSONL.
  """
  if isinstance(obj, dict):
    return {k.strip(): clean_data(v) for k, v in obj.items() if k is not None}
  elif isinstance(obj, list):
    return [clean_data(i) for i in obj]
  elif isinstance(obj, str):
    return obj.strip()
  return obj

def load_candidates(filepath):
  """
  Streams the JSONL file, cleans it, and flattens it into a Pandas DataFrame.
  """
  print(f"Loading candidates from {filepath}...")
  start_time = time.time()
  
  cleaned_data = []
  
  # We use standard JSON streaming for maximum memory efficiency
  with open(filepath, 'r', encoding='utf-8') as f:
    # tqdm gives us a nice progress bar in the terminal
    lines = f.readlines()
    for line in tqdm(lines, desc="Parsing & Cleaning JSONL", unit="candidates"):
      if not line.strip():
        continue
      try:
        raw_json = json.loads(line)
        cleaned_json = clean_data(raw_json)
        cleaned_data.append(cleaned_json)
      except json.JSONDecodeError:
        continue # Skip malformed lines safely

  # pd.json_normalize flattens nested dicts (e.g., profile.years_of_experience becomes profile_years_of_experience)
  # Lists of dicts (like skills and career_history) remain as lists in their respective columns.
  df = pd.json_normalize(cleaned_data, sep='_')
  
  elapsed = time.time() - start_time
  print(f"Successfully loaded and cleaned {len(df)} candidates in {elapsed:.2f} seconds.")
  print(f"DataFrame Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
  
  return df