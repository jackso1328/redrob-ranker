"""
src/config.py
Centralized configuration for the Redrob Ranker.
"""

# ==============================================================================
# 1. THE "BOUNCER" FILTERS (Trap Detection)
# ==============================================================================
IT_SERVICES_COMPANIES = {
  "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", 
  "mindtree", "hcl", "tech mahindra", "ltimindtree", "lt infotech",
  "mphasis", "persistent systems", "epam systems", "publicis sapient", "genpact"
}

MIN_YOE = 3.0
MAX_YOE = 12.0

# ==============================================================================
# 2. THE "AI BRAIN" & QUALITY TARGETS
# ==============================================================================
JD_MANDATES = [
  "shipped ranking or recommendation systems to production",
  "built embeddings-based retrieval systems",
  "managed vector databases like Pinecone, FAISS, Weaviate, or Milvus",
  "designed evaluation frameworks for ranking using NDCG, MRR, or MAP",
  "offline-to-online correlation analysis and A/B testing for ML models",
  "learning-to-rank models using XGBoost or neural networks"
]

PRODUCT_COMPANY_KEYWORDS = {
  "swiggy", "zomato", "uber", "ola", "razorpay", "cred", "flipkart", 
  "meesho", "phonepe", "paytm", "byju's", "rupeek", "zepto", "blinkit",
  "microsoft", "google", "amazon", "meta", "netflix", "adobe", "salesforce"
}

# Expanded to catch the exact tech stack requested in the JD
TARGET_HARD_SKILLS = {
  'pinecone', 'faiss', 'milvus', 'weaviate', 'qdrant', 'opensearch', 'elasticsearch',
  'embeddings', 'sentence transformers', 'information retrieval', 'vector search', 
  'semantic search', 'hybrid search', 'retrieval', 'rag',
  'xgboost', 'lightgbm', 'learning to rank', 'ltr', 'ndcg', 'mrr', 'map',
  'scikit-learn', 'tensorflow', 'pytorch', 'hugging face',
  'lora', 'qlora', 'peft'
}

# The "LangChain Wrapper" Trap
WRAPPER_SKILLS = {'langchain', 'openai api', 'llamaindex'}
FOUNDATIONAL_SKILLS = {'xgboost', 'lightgbm', 'scikit-learn', 'faiss', 'elasticsearch', 'tensorflow', 'pytorch', 'pyspark'}

# The "Shipper vs Researcher" Trap
RESEARCH_TITLES = {'research scientist', 'research engineer', 'postdoc', 'phd researcher'}
SHIPPING_KEYWORDS = {'shipped', 'deployed', 'production', 'a/b test', 'users', 'latency', 'throughput', 'live'}

# The "Red Flag" Skills (Computer Vision / Speech)
RED_FLAG_SKILLS = {'gans', 'yolo', 'object detection', 'speech recognition', 'tts', 'image classification', 'computer vision', 'cnn'}

# Ideal Titles for the role
IDEAL_TITLES = {'ai engineer', 'ml engineer', 'machine learning engineer', 'search engineer', 'nlp engineer', 'recommendation systems engineer', 'applied scientist', 'data scientist'}