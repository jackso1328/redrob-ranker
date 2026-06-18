"""
src/behavioral_scorer.py
Calculates the behavioral multiplier based on Redrob signals.
Updated to use flattened Pandas columns correctly.
"""
import pandas as pd
import numpy as np
from datetime import datetime

def calculate_behavioral_score(df):
  print("Calculating Behavioral Multipliers...")
  
  # 1. Demand vs Desperation Ratio
  views = df['redrob_signals_profile_views_received_30d'].fillna(0)
  apps = df['redrob_signals_applications_submitted_30d'].fillna(0)
  demand_index = views / (apps + 1)
  
  # 2. Engagement Velocity
  response_rate = df['redrob_signals_recruiter_response_rate'].fillna(0)
  response_time = df['redrob_signals_avg_response_time_hours'].fillna(200)
  time_score = 1.0 / (1.0 + (response_time / 100.0))
  engagement = response_rate * time_score
  
  # 3. GitHub Activity
  github = df['redrob_signals_github_activity_score'].fillna(-1)
  github_score = github.apply(lambda x: max(0, x) / 100.0)
  
  # Base Multiplier Calculation
  raw_score = (0.4 * engagement) + (0.3 * (demand_index / (demand_index.max() + 1))) + (0.3 * github_score)
  normalized_score = raw_score / raw_score.max() if raw_score.max() > 0 else raw_score
  df['behavioral_multiplier'] = 0.5 + (0.5 * normalized_score)

  # THE UPGRADE: Ghost Hard Reset
  reference_date = datetime(2025, 6, 1)
  
  def is_ghost(row):
    rate = row.get('redrob_signals_recruiter_response_rate', 0)
    last_active_str = row.get('redrob_signals_last_active_date', '2020-01-01')
    try:
      last_active = datetime.strptime(last_active_str, '%Y-%m-%d')
      days_inactive = (reference_date - last_active).days
    except:
      days_inactive = 999
    return (rate < 0.20) or (days_inactive > 90)
    
  ghost_mask = df.apply(is_ghost, axis=1)
  df.loc[ghost_mask, 'behavioral_multiplier'] = 0.01
  print(f" Hard-reset {ghost_mask.sum()} Ghost candidates to 0.01 multiplier")

  # THE UPGRADE: Notice Period Penalty
  notice_period = df['redrob_signals_notice_period_days'].fillna(60)
  penalty_mask = notice_period > 30
  df.loc[penalty_mask, 'behavioral_multiplier'] *= 0.95
  print(f" ️ Applied 0.95x penalty to {penalty_mask.sum()} candidates with >30 day notice")

  print(f"Behavioral scoring complete. Mean multiplier: {df['behavioral_multiplier'].mean():.3f}\n")
  return df