"""
src/quality_scorer.py
Calculates the Quality Score based on Experience, Company Tier, Hard Skills, and JD Nuances.
"""
import pandas as pd
import numpy as np
from src.config import PRODUCT_COMPANY_KEYWORDS, TARGET_HARD_SKILLS, WRAPPER_SKILLS, FOUNDATIONAL_SKILLS, RESEARCH_TITLES, SHIPPING_KEYWORDS, IDEAL_TITLES, RED_FLAG_SKILLS

def calculate_quality_score(df):
  print("️ Calculating Quality Score (Experience, Companies, Hard Skills, Nuances)...")
  
  # 1. YEARS OF EXPERIENCE SCORE (Peak at 5-9 years)
  yoe = pd.to_numeric(df.get('profile_years_of_experience', 0), errors='coerce').fillna(0)
  yoe_score = np.where(yoe < 3, 0.1, np.where(yoe <= 5, 0.1 + ((yoe - 3) / 2) * 0.9, np.where(yoe <= 9, 1.0, np.where(yoe <= 12, 1.0 - ((yoe - 9) / 3) * 0.7, 0.2))))

  # 2. PRODUCT COMPANY BONUS
  def check_product_co(history):
    if not isinstance(history, list): return 0.2
    for job in history:
      if isinstance(job, dict) and any(p in str(job.get('company', '')).lower() for p in PRODUCT_COMPANY_KEYWORDS):
        return 1.0
    return 0.2
  product_score = df['career_history'].apply(check_product_co)

  # 3. HARD SKILL MATCH
  def check_hard_skills(skills):
    if not isinstance(skills, list): return 0.0
    count = sum(1 for s in skills if isinstance(s, dict) and str(s.get('name', '')).lower() in TARGET_HARD_SKILLS)
    return min(count / 4.0, 1.0) 
  skill_score = df['skills'].apply(check_hard_skills)

  # THE UPGRADE: Pre-LLM Era Ratio (Penalize LangChain Wrappers)
  def check_pre_llm_ratio(skills):
    if not isinstance(skills, list): return 1.0 # No penalty if no skills listed
    wrapper_dur = sum(s.get('duration_months', 0) for s in skills if isinstance(s, dict) and str(s.get('name', '')).lower() in WRAPPER_SKILLS)
    found_dur = sum(s.get('duration_months', 0) for s in skills if isinstance(s, dict) and str(s.get('name', '')).lower() in FOUNDATIONAL_SKILLS)
    if wrapper_dur > found_dur and wrapper_dur > 6: return 0.0 # Strict drop for LangChain Wrappers
    return 1.0
  pre_llm_multiplier = df['skills'].apply(check_pre_llm_ratio)

  # THE UPGRADE: Shipper vs Researcher
  def check_shipper(row):
    title = str(row.get('profile_current_title', '')).lower()
    history = row.get('career_history', [])
    is_research = any(rt in title for rt in RESEARCH_TITLES)
    if not is_research: return 1.0
    
    # If research title, check for shipping keywords in descriptions
    text = " ".join([str(j.get('description', '')) for j in history if isinstance(j, dict)]).lower()
    if any(kw in text for kw in SHIPPING_KEYWORDS): return 0.8 # Slight penalty but acceptable
    return 0.0 # Strict drop for pure researcher with zero shipping
  shipper_multiplier = df.apply(check_shipper, axis=1)

  # THE UPGRADE: Job Hopper Penalty (Avg tenure < 18 months)
  def check_job_hopper(history):
    if not isinstance(history, list) or len(history) == 0: return 1.0
    durations = [j.get('duration_months', 0) for j in history if isinstance(j, dict)]
    avg_tenure = sum(durations) / len(durations)
    return 0.7 if avg_tenure < 18 else 1.0
  hopper_multiplier = df['career_history'].apply(check_job_hopper)

  # THE UPGRADE: Location / Relocation
  def check_location(row):
    country = str(row.get('profile_country', 'India')).lower()
    willing = row.get('redrob_signals_willing_to_relocate', True)
    if country != 'india' and not willing: return 0.5
    return 1.0
  location_multiplier = df.apply(check_location, axis=1)

  # RED FLAG: Computer Vision / Speech Penalty
  # JD says: "People whose primary expertise is computer vision, speech, or robotics
  # without significant NLP/IR exposure. We respect your work but you'd be re-learning fundamentals."
  def check_red_flag_skills(skills):
    if not isinstance(skills, list): return 1.0
    skill_names = [str(s.get('name', '')).lower() for s in skills if isinstance(s, dict)]
    red_count = sum(1 for s in skill_names if s in RED_FLAG_SKILLS)
    target_count = sum(1 for s in skill_names if s in TARGET_HARD_SKILLS)
    if red_count > 0 and target_count == 0:
      return 0.3 # Heavy penalty: CV/Speech with zero relevant skills
    elif red_count > target_count:
      return 0.6 # Moderate penalty: more red flags than target skills
    return 1.0
  red_flag_multiplier = df['skills'].apply(check_red_flag_skills)

  # IDEAL TITLE BONUS
  # Candidates with titles like 'AI Engineer', 'ML Engineer', 'Search Engineer' get a boost
  def check_ideal_title(title):
    if not isinstance(title, str): return 1.0
    title = title.lower()
    if any(ideal in title for ideal in IDEAL_TITLES):
      return 1.3 # 30% boost for ideal titles
    return 1.0
  title_bonus = df['profile_current_title'].apply(check_ideal_title)

  # Combine into final Quality Score
  base_quality = (0.50 * yoe_score) + (0.25 * product_score) + (0.25 * skill_score)
  
  # Apply all the nuanced multipliers
  df['quality_score'] = base_quality * pre_llm_multiplier * shipper_multiplier * hopper_multiplier * location_multiplier * red_flag_multiplier * title_bonus
  
  print(f"Quality scoring complete. Mean: {df['quality_score'].mean():.3f}\n")
  return df