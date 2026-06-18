# test_pipeline.py
from src.data_loader import load_candidates
from src.trap_detector import detect_traps
from src.semantic_ranker import calculate_semantic_score
import json
import pandas as pd

if __name__ == "__main__":
    # 1. Load Data
    df = load_candidates('sample_candidates.json') 
    
    # Fallback for JSON array format
    if len(df) == 0:
        print("Detected JSON array format for sample, loading...")
        with open('sample_candidates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        def clean_data(obj):
            if isinstance(obj, dict): return {k.strip(): clean_data(v) for k, v in obj.items()}
            elif isinstance(obj, list): return [clean_data(i) for i in obj]
            elif isinstance(obj, str): return obj.strip()
            return obj
        df = pd.json_normalize([clean_data(d) for d in data], sep='_')

    # 2. Trap Detection
    df_clean = detect_traps(df)
    
    # 3. Semantic Ranking (The AI Brain)
    df_ranked = calculate_semantic_score(df_clean)
    
    # 4. Show the Top 5 Semantic Matches
    print("\n🏆 TOP 5 SEMANTIC MATCHES (The AI Brain's Picks):")
    top_5 = df_ranked.nlargest(5, 'semantic_score')
    for idx, row in top_5.iterrows():
        name = row.get('profile_anonymized_name', 'Unknown')
        title = row.get('profile_current_title', 'Unknown')
        company = row.get('profile_current_company', 'Unknown')
        score = row['semantic_score']
        print(f"   [{score:.3f}] {name} | {title} @ {company}")
        
    print("\nPipeline Test Successful!")