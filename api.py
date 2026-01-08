from fastapi import FastAPI, Query
from rapidfuzz import fuzz
import pandas as pd
import os

app = FastAPI(title="Brand Suggester API")

def load_brands():
    CSV_FILE = 'brands.csv'
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding='latin1') 
            return df['brand_name'].tolist()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return ["Nike", "Adidas", "Apple", "Moving Walls"]
    return ["Nike", "Adidas", "Apple", "Moving Walls"]

BRAND_DATABASE = load_brands()

@app.get("/")
def home():
    return {"status": "Brand Suggester API is running", "version": "1.1.0"}

@app.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    suggestions = []
    query_clean = q.lower().strip()

    for brand in BRAND_DATABASE:
        brand_clean = brand.lower().strip()
        
        # 1. Direct or Partial Match (High Priority)
        # Ratio: Basic similarity
        # Partial_ratio: Good for "Apple" in "Apple Inc"
        ratio_score = fuzz.ratio(query_clean, brand_clean)
        partial_score = fuzz.partial_ratio(query_clean, brand_clean)
        
        # 2. Pick the best score for this brand
        # This allows "abibas" to hit "adidas" with a high enough score
        score = max(ratio_score, partial_score)

        # 3. Boost logic (Same as your Streamlit app)
        if query_clean == brand_clean: 
            score = 100
        elif query_clean in brand_clean: 
            score = max(score, 95)
        
        # 4. Threshold: 35 is usually safe for typos like "abibas"
        if score > 35:
            suggestions.append({"brand": brand, "score": round(score, 2)})

    # Return top 2 results sorted by highest score
    final_results = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    return {"query": q, "results": final_results}