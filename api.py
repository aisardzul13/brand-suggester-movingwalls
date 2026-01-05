from fastapi import FastAPI, Query
from rapidfuzz import fuzz
import pandas as pd
import os

app = FastAPI(title="Brand Suggester API")

# Reusable logic to load brands (Same as your Streamlit app)
# def load_brands():
#     CSV_FILE = 'brands.csv'
#     if os.path.exists(CSV_FILE):
#         df = pd.read_csv(CSV_FILE)
#         return df['brand_name'].tolist()
#     return ["Nike", "Adidas", "Apple", "Moving Walls"] # Fallback

def load_brands():
    CSV_FILE = 'brands.csv'
    if os.path.exists(CSV_FILE):
        try:
            # Added encoding='latin1' to handle special characters
            df = pd.read_csv(CSV_FILE, encoding='latin1') 
            return df['brand_name'].tolist()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return ["Nike", "Adidas", "Apple", "Moving Walls"]
    return ["Nike", "Adidas", "Apple", "Moving Walls"]

BRAND_DATABASE = load_brands()

@app.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    """
    Mobile app calls this: https://your-api.com/suggest?q=nkee
    """
    suggestions = []
    for brand in BRAND_DATABASE:
        score = fuzz.ratio(q.lower(), brand.lower())
        # Apply the same weight logic as your Streamlit app
        if q.lower() == brand.lower(): score = 100
        elif q.lower() in brand.lower(): score = max(score, 95)
        
        if score > 45:
            suggestions.append({"brand": brand, "score": round(score, 2)})

    # Return top 2 results as JSON
    final_results = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:2]
    return {"query": q, "results": final_results}