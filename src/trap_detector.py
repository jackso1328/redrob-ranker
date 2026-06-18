"""
src/trap_detector.py
The 'Bouncer'. Instantly eliminates honeypots, keyword stuffers, and IT-services lifers.
"""
import pandas as pd
import numpy as np
from src.config import IT_SERVICES_COMPANIES

def detect_traps(df):
  print("️ Running Trap Detector (The Bouncer)...")
  initial_count = len(df)
  keep_mask = pd.Series(True, index=df.index)

  # --- TRAP 1: IT Services Lifer ---
  def is_it_lifer(row):
    history = row.get('career_history', [])
    if not history or not isinstance(history, list) or len(history) == 0: return False
    companies = [str(job.get('company', '')).lower() for job in history if isinstance(job, dict)]
    # Drop if ALL companies are IT services
    if len(companies) > 0 and all(c in IT_SERVICES_COMPANIES for c in companies): return True
    # Also drop if current company is IT services AND no product company in history
    current_industry = str(row.get('profile_current_industry', '')).lower()
    if current_industry == 'it services':
      industries = [str(job.get('industry', '')).lower() for job in history if isinstance(job, dict)]
      has_product = any(ind not in ('it services', 'consulting', 'manufacturing', 'paper products') for ind in industries)
      if not has_product: return True
    return False
  it_mask = df.apply(is_it_lifer, axis=1)
  keep_mask &= ~it_mask
  print(f" Dropped {it_mask.sum()} IT Services Lifers")

  # --- TRAP 2: Extreme YoE Outliers ---
  yoe_col = 'profile_years_of_experience'
  if yoe_col in df.columns:
    yoe = pd.to_numeric(df[yoe_col], errors='coerce').fillna(0)
    extreme_yoe_mask = (yoe < 3.0) | (yoe > 15.0)
    keep_mask &= ~extreme_yoe_mask
    print(f" Dropped {extreme_yoe_mask.sum()} Extreme YoE Outliers")

  # --- TRAP 3: Obvious Non-Technical Titles ---
  def is_disqualified_title(title):
    if not isinstance(title, str): return False
    title = title.lower()
    disqualified = [
      'accountant', 'hr manager', 'marketing manager', 'sales executive',
      'graphic designer', 'civil engineer', 'mechanical engineer',
      'content writer', 'customer support', 'operations manager',
      'business analyst', 'project manager', 'qa engineer',
      'recruiter', 'sales manager', 'legal', 'finance manager',
      'supply chain', 'logistics', 'procurement', 'teacher',
      'pharmacist', 'nurse', 'doctor', 'chef', 'driver'
    ]
    return any(kw in title for kw in disqualified)
  if 'profile_current_title' in df.columns:
    disqualified_title_mask = df['profile_current_title'].apply(is_disqualified_title)
    keep_mask &= ~disqualified_title_mask
    print(f" Dropped {disqualified_title_mask.sum()} Obvious Non-Tech Titles")

  # --- TRAP 4: Honeypot Detection ---
  # NOTE: Skills are CONCURRENT not sequential. A person with 7 years can have
  # 10 skills each lasting 12 months simultaneously. The old 1.5x threshold
  # was dropping 63,000 legit candidates. The spec says ~80 honeypots exist.
  # Real honeypots have extreme patterns: 10+ expert skills with 0 months,
  # or total skill months > 3.5x career length.
  def is_honeypot(row):
    yoe_months = row.get('profile_years_of_experience', 0) * 12
    skills = row.get('skills', [])
    if not isinstance(skills, list): return False
    total_skill_months = sum(s.get('duration_months', 0) for s in skills if isinstance(s, dict))
    expert_count = sum(1 for s in skills if isinstance(s, dict) and str(s.get('proficiency', '')).lower() == 'expert')
    # Honeypot pattern 1: Impossibly high total skill duration
    if yoe_months > 0 and total_skill_months > (yoe_months * 3.5):
      return True
    # Honeypot pattern 2: Many 'expert' skills but 0 duration
    if expert_count >= 8 and total_skill_months == 0:
      return True
    # Honeypot pattern 3: Expert in everything with short career
    if expert_count >= 10 and yoe_months < 60:
      return True
    return False
  honeypot_mask = df.apply(is_honeypot, axis=1)
  keep_mask &= ~honeypot_mask
  print(f" Dropped {honeypot_mask.sum()} Mathematical Honeypots")

  # --- TRAP 5: Title-Skill Dissonance (Keyword Stuffer) ---
  def is_dissonant(row):
    title = str(row.get('profile_current_title', '')).lower()
    skills = row.get('skills', [])
    if not isinstance(skills, list): return False
    
    # If title is clearly non-tech, but they claim "expert" in core AI skills
    non_tech_in_title = any(kw in title for kw in ['marketing', 'hr', 'sales', 'accountant', 'designer'])
    if non_tech_in_title:
      for s in skills:
        if isinstance(s, dict) and s.get('proficiency') == 'expert' and str(s.get('name', '')).lower() in {'pinecone', 'faiss', 'xgboost', 'pytorch'}:
          return True
    return False
  dissonance_mask = df.apply(is_dissonant, axis=1)
  keep_mask &= ~dissonance_mask
  print(f" Dropped {dissonance_mask.sum()} Title-Skill Dissonant Keyword Stuffers")

  # --- TRAP 6: Architect/Tech Lead Non-Coder ---
  def is_non_coding_lead(history):
    if not history or not isinstance(history, list) or len(history) == 0: return False
    # Get the most recent job
    recent_job = history[0] if isinstance(history[0], dict) else {}
    title = str(recent_job.get('title', '')).lower()
    duration = recent_job.get('duration_months', 0)
    
    # Check if title implies non-coding leadership without engineering
    is_lead = any(kw in title for kw in ['architect', 'tech lead', 'engineering manager', 'vp of engineering', 'director'])
    is_engineer = any(kw in title for kw in ['engineer', 'developer', 'programmer', 'scientist', 'sde'])
    
    if is_lead and not is_engineer and duration >= 18:
      return True
    return False
  
  if 'career_history' in df.columns:
    non_coder_mask = df['career_history'].apply(is_non_coding_lead)
    keep_mask &= ~non_coder_mask
    print(f" Dropped {non_coder_mask.sum()} Non-Coding Leads/Architects")

  df_filtered = df[keep_mask].copy().reset_index(drop=True)
  print(f"Bouncer finished. Dropped {initial_count - len(df_filtered)} traps. Kept {len(df_filtered)} viable candidates.\n")
  return df_filtered