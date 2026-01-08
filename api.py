from fastapi import FastAPI, Query
from rapidfuzz import fuzz
import pandas as pd
import os

app = FastAPI(title="Brand Suggester API | Moving Walls")

# --- BRAND LOADING LOGIC ---
def load_brands():
    CSV_FILE = 'brands.csv'
    if os.path.exists(CSV_FILE):
        try:
            # Using latin1 to prevent the UnicodeDecodeError we saw earlier
            df = pd.read_csv(CSV_FILE, encoding='latin1') 
            return df['brand_name'].tolist()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return ["Nike", "Adidas", "Apple", "Baskin-Robbins", "Moving Walls"]
    return ["Nike", "Adidas", "Apple", "Baskin-Robbins", "Moving Walls"]

BRAND_DATABASE = load_brands()

# --- ROOT ROUTE (Fixes the 404 Error) ---
@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Welcome to the Moving Walls Brand API",
        "usage": "/suggest?q=brandname"
    }

# --- SEARCH LOGIC (Improved for Typos & Abbreviations) ---
@app.get("/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    query_clean = q.lower().strip()
    suggestions = []

    for brand in BRAND_DATABASE:
        brand_name = str(brand)
        brand_clean = brand_name.lower().strip()
        
        # 1. Calculate 'Token Set Ratio'
        # This is great for abbreviations and out-of-order words (e.g., 'mcd' for 'McDonalds')
        score = fuzz.token_set_ratio(query_clean, brand_clean)
        
        # 2. THE FIRST LETTER BOOST (+15 points)
        # People usually get the first letter right. This stops "Bakin" from matching "Cap Tamin"
        if brand_clean.startswith(query_clean[0]):
            score += 15

        # 3. LENGTH PENALTY
        # If the brand name is way longer than the query, we reduce the score
        len_diff = abs(len(query_clean) - len(brand_clean))
        if len_diff > 12:
            score -= 20

        # 4. FINAL PRIORITY BOOSTS
        if query_clean == brand_clean: 
            score = 150  # Exact match always wins
        elif query_clean in brand_clean: 
            score = max(score, 95) # Query is inside the brand name
        
        # 5. THRESHOLD
        # We only keep brands with a score above 50 now for better quality
        if score > 50:
            suggestions.append({
                "brand": brand_name, 
                "score": min(score, 100) # Cap display score at 100%
            })

    # Sort results by score (highest first) and return top 3
    final_results = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    
    return {
        "query": q, 
        "results": final_results
    }