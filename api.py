from fastapi import FastAPI, Query
from rapidfuzz import fuzz, process # Added process
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
            return ["Nike", "Adidas", "Apple", "Moving Walls"]
    return ["Nike", "Adidas", "Apple", "Moving Walls"]

BRAND_DATABASE = load_brands()

@app.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    query_clean = q.lower().strip()
    
    # Use extract_iter to compare the query against the whole database
    # WRatio is much better at handling typos like 'abibas'
    matches = process.extract(
        query_clean, 
        BRAND_DATABASE, 
        scorer=fuzz.WRatio, 
        limit=5
    )

    suggestions = []
    for brand, score, index in matches:
        brand_clean = brand.lower()
        
        # Boost logic for exact/partial matches
        final_score = score
        if query_clean == brand_clean: 
            final_score = 100
        elif query_clean in brand_clean: 
            final_score = max(final_score, 95)
        
        if final_score > 35:
            suggestions.append({"brand": brand, "score": round(final_score, 2)})

    # Sort results to ensure the best matches stay on top
    final_results = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    return {"query": q, "results": final_results}