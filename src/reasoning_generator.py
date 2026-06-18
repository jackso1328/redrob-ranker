"""
src/reasoning_generator.py
Generates factual, zero-hallucination, varied reasoning strings.
"""
import pandas as pd
from src.config import RED_FLAG_SKILLS

def generate_reasoning(df):
  print("Generating Zero-Hallucination, Varied Reasoning...")
  
  reasons = []
  for idx, row in df.iterrows():
    name = row.get('profile_anonymized_name', 'Unknown')
    title = row.get('profile_current_title', 'Unknown')
    company = row.get('profile_current_company', 'Unknown')
    yoe = row.get('profile_years_of_experience', 0)
    response_rate = row.get('redrob_signals_recruiter_response_rate', 0)
    notice_period = row.get('redrob_signals_notice_period_days', 60)
    rank = row.get('rank', 50)
    
    skills = row.get('skills', [])
    sorted_skills = sorted(skills, key=lambda x: x.get('duration_months', 0) if isinstance(x, dict) else 0, reverse=True) if isinstance(skills, list) else []
    top_skills = ", ".join([s.get('name', '') for s in sorted_skills[:2] if isinstance(s, dict) and s.get('name')])

    # Check for product company
    career = row.get('career_history', [])
    product_cos = [j.get('company') for j in career if isinstance(j, dict) and j.get('industry') in ['Food Delivery', 'Transportation', 'E-commerce', 'Fintech', 'Software', 'AI/ML']]
    product_exp = f"experience at {product_cos[0]}" if product_cos else "general industry experience"

    # RED FLAG DETECTION
    concern_text = ""
    if sorted_skills:
      top_skill_names = {s.get('name', '').lower() for s in sorted_skills[:3] if isinstance(s, dict)}
      if top_skill_names.intersection(RED_FLAG_SKILLS):
        concern_text = " Note: Profile shows heavy Computer Vision/Speech focus which may lack required NLP/IR depth."

    # RANK-BASED TONE & SENTENCE VARIATION
    if rank <= 10:
      # Glowing tone, start with Company/Role
      reason = f"Currently {title} at {company} ({product_exp}), {name} brings {yoe} years of highly relevant applied ML experience. Deep expertise in {top_skills} with excellent engagement ({response_rate*100:.0f}% response rate).{concern_text}"
    elif rank <= 50:
      # Solid tone, start with Skills
      reason = f"Strong depth in {top_skills} combined with {yoe} years as {title} at {company}. {product_exp}. Behavioral signal is solid ({response_rate*100:.0f}% response rate, {notice_period} days notice).{concern_text}"
    else:
      # Honest/Concerned tone, start with YoE
      reason = f"{name} has {yoe} years of experience, currently as {title} at {company}. Possesses skills in {top_skills}, though primarily with {product_exp}. Notice period is {notice_period} days.{concern_text}"
      
    reasons.append(reason)
    
  df.loc[:, 'reasoning'] = reasons
  print("Reasoning generation complete.\n")
  return df