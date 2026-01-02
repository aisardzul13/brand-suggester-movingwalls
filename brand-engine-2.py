# import csv
# import os
# from flask import Flask, request, jsonify, render_template_string
# from rapidfuzz import process, fuzz

# app = Flask(__name__)
# CSV_FILE = 'brands.csv'

# def load_brands():
#     brands = []
#     if not os.path.exists(CSV_FILE):
#         with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(['brand_name'])
#         return ["Nike", "Adidas", "Apple", "Amazon", "Tesla", "Microsoft", "Google", "Samsung", "Moving Walls"]
    
#     with open(CSV_FILE, mode='r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             brands.append(row['brand_name'])
#     return brands

# BRAND_DATABASE = load_brands()

# HTML_PAGE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Brand Suggester | Moving Walls</title>
#     <style>
#         :root {
#             --primary: #1a73e8;
#             --accent-high: #34a853;
#             --accent-mid: #fbbc05;
#             --bg: #f4f7fa;
#             --text: #202124;
#             --card-shadow: 0 10px 30px rgba(0,0,0,0.08);
#         }

#         body { 
#             font-family: 'Inter', -apple-system, sans-serif; 
#             background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
#             display: flex; flex-direction: column; align-items: center;
#             min-height: 100vh; margin: 0; padding-top: 60px;
#         }

#         .logo-container {
#             position: absolute; top: 30px; right: 40px;
#             background: rgba(255, 255, 255, 0.8); padding: 10px 20px;
#             border-radius: 12px; box-shadow: var(--card-shadow);
#             transition: transform 0.3s ease;
#         }
#         .logo-container img { width: 150px; height: auto; display: block; }

#         .stats-grid {
#             display: flex; gap: 15px; margin-bottom: 25px; width: 100%; max-width: 450px;
#         }
#         .stat-card {
#             flex: 1; background: rgba(255,255,255,0.7); padding: 15px; 
#             border-radius: 16px; backdrop-filter: blur(5px);
#             text-align: center; border: 1px solid rgba(255,255,255,0.3);
#         }
#         .stat-val { display: block; font-size: 18px; font-weight: 800; color: var(--primary); }
#         .stat-label { font-size: 10px; text-transform: uppercase; color: #777; letter-spacing: 0.5px; }

#         .container { 
#             background: rgba(255, 255, 255, 0.95); padding: 40px; 
#             border-radius: 24px; box-shadow: var(--card-shadow); 
#             width: 100%; max-width: 450px; text-align: center;
#             backdrop-filter: blur(10px); z-index: 2;
#         }

#         h1 { color: var(--text); font-size: 22px; font-weight: 700; margin-bottom: 8px; }
#         .subtitle { color: #5f6368; font-size: 14px; margin-bottom: 25px; }

#         input { 
#             width: 100%; padding: 16px 20px; border: 2px solid #e0e0e0; 
#             border-radius: 14px; box-sizing: border-box; font-size: 16px; 
#             transition: 0.3s; box-shadow: 0 2px 6px rgba(0,0,0,0.02);
#         }
#         input:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 4px rgba(26, 115, 232, 0.1); }

#         .result-box { margin-top: 20px; text-align: left; }
#         .suggestion-item { 
#             padding: 12px 16px; margin-bottom: 10px; background: white;
#             border: 1px solid #f0f0f0; border-radius: 12px; 
#             display: flex; justify-content: space-between; align-items: center;
#             transition: 0.2s; cursor: pointer; animation: slideUp 0.3s ease forwards;
#         }
#         .suggestion-item:hover { transform: translateY(-2px); border-color: var(--primary); }
#         .brand-name { color: var(--text); font-weight: 600; font-size: 15px; }
#         .score-badge { padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 11px; }
#         .high-match { background: #e6f4ea; color: var(--accent-high); }
#         .mid-match { background: #fff4e5; color: var(--accent-mid); }

#         .history-section { margin-top: 25px; border-top: 1px solid #eee; padding-top: 20px; text-align: left; }
#         .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
#         .clear-btn { font-size: 10px; color: #f44336; cursor: pointer; text-transform: uppercase; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
#         .clear-btn:hover { background: #ffebee; }
        
#         .history-chips { display: flex; gap: 8px; flex-wrap: wrap; }
#         .chip { background: #eee; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #555; cursor: pointer; transition: 0.2s; }
#         .chip:hover { background: var(--primary); color: white; }

#         .info-box {
#             margin-top: 30px; width: 100%; max-width: 450px; 
#             background: rgba(255,255,255,0.4); padding: 20px; border-radius: 16px;
#             font-size: 12px; color: #666; text-align: left; line-height: 1.6;
#         }
        
#         footer { margin-top: auto; padding: 40px 0 20px; font-size: 12px; color: #777; }

#         label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; color: #aaa; display: block; }
#         @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
#     </style>
# </head>
# <body>
#     <div class="logo-container">
#         <img src="https://www.movingwalls.com/wp-content/uploads/2023/05/cropped-MW-logo-1.png" alt="Moving Walls">
#     </div>

#     <div class="stats-grid">
#         <div class="stat-card">
#             <span class="stat-val">{{ brand_count }}</span>
#             <span class="stat-label">Total Brands</span>
#         </div>
#         <div class="stat-card">
#             <span class="stat-val" style="color: var(--accent-high);">Active</span>
#             <span class="stat-label">System Status</span>
#         </div>
#     </div>

#     <div class="container">
#         <h1>Brand Suggester</h1>
#         <p class="subtitle">Intelligent brand discovery by Moving Walls</p>
        
#         <input type="text" id="searchBox" placeholder="Start typing (e.g., nkee)..." oninput="liveSearch()" autocomplete="off">

#         <div id="resultContainer" style="display:none; margin-top: 20px;">
#             <label>Top 2 Suggestions</label>
#             <div class="result-box" id="results"></div>
#         </div>

#         <div class="history-section" id="historySection" style="display:none;">
#             <div class="history-header">
#                 <label>Recent Searches</label>
#                 <span class="clear-btn" onclick="clearHistory()">Clear</span>
#             </div>
#             <div class="history-chips" id="historyChips"></div>
#         </div>
#     </div>

#     <div class="info-box">
#         <strong>💡 Pro Tip:</strong> Our engine uses <b>RapidFuzz</b> logic. This means it can find brands even if you misspell them or miss a few letters. Click a search result to save it to your history!
#     </div>

#     <footer>
#         &copy; 2026 Moving Walls Media Technology Group. All rights reserved.
#     </footer>

#     <script>
#         let history = JSON.parse(localStorage.getItem('brandHistory')) || [];

#         function updateHistoryUI() {
#             const section = document.getElementById('historySection');
#             const chipContainer = document.getElementById('historyChips');
#             if (history.length === 0) { section.style.display = 'none'; return; }
#             section.style.display = 'block';
#             chipContainer.innerHTML = '';
#             history.forEach(brand => {
#                 const span = document.createElement('span');
#                 span.className = 'chip';
#                 span.innerText = brand;
#                 span.onclick = () => { document.getElementById('searchBox').value = brand; liveSearch(); };
#                 chipContainer.appendChild(span);
#             });
#         }

#         function clearHistory() {
#             history = [];
#             localStorage.removeItem('brandHistory');
#             updateHistoryUI();
#         }

#         function addToHistory(brand) {
#             if (!history.includes(brand)) {
#                 history.unshift(brand);
#                 if (history.length > 5) history.pop();
#                 localStorage.setItem('brandHistory', JSON.stringify(history));
#                 updateHistoryUI();
#             }
#         }

#         function liveSearch() {
#             const query = document.getElementById('searchBox').value;
#             const container = document.getElementById('resultContainer');
#             const resultDiv = document.getElementById('results');

#             if (query.length < 2) { container.style.display = 'none'; return; }

#             fetch('/suggest?query=' + query)
#                 .then(res => res.json())
#                 .then(data => {
#                     container.style.display = 'block';
#                     resultDiv.innerHTML = '';
#                     if (data.suggestions.length === 0) {
#                         resultDiv.innerHTML = '<div style="color:#999; font-size:14px; text-align:center; padding: 10px;">No matching brands found</div>';
#                     } else {
#                         data.suggestions.forEach(item => {
#                             const badgeClass = item.score >= 80 ? 'high-match' : 'mid-match';
#                             const itemEl = document.createElement('div');
#                             itemEl.className = 'suggestion-item';
#                             itemEl.innerHTML = `<span class="brand-name">${item.brand}</span><span class="score-badge ${badgeClass}">${Math.round(item.score)}% Match</span>`;
#                             itemEl.onclick = () => {
#                                 document.getElementById('searchBox').value = item.brand;
#                                 addToHistory(item.brand);
#                             };
#                             resultDiv.appendChild(itemEl);
#                         });
#                     }
#                 });
#         }
#         updateHistoryUI();
#     </script>
# </body>
# </html>
# """

# @app.route('/')
# def home():
#     return render_template_string(HTML_PAGE, brand_count=len(BRAND_DATABASE))

# @app.route('/suggest', methods=['GET'])
# def get_suggestions():
#     query = request.args.get('query', '').strip().lower()
#     if not query: return jsonify({"suggestions": []})
#     suggestions = []
#     for brand in BRAND_DATABASE:
#         score = fuzz.ratio(query, brand.lower())
#         if query == brand.lower(): score = 100
#         elif query in brand.lower(): score = max(score, 95)
#         suggestions.append({"brand": brand, "score": score})
#     final_results = sorted([s for s in suggestions if s['score'] > 45], key=lambda x: x['score'], reverse=True)[:2]
#     return jsonify({"suggestions": final_results})

# if __name__ == '__main__':
#     app.run(debug=True)

import streamlit as st
from rapidfuzz import fuzz
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Brand Suggester | Moving Walls", page_icon="🏢")

# --- CUSTOM CSS (Maintaining your High-End UI style) ---
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
    .stTextInput > div > div > input {
        border-radius: 14px;
        padding: 16px;
        border: 2px solid #e0e0e0;
    }
    .score-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        float: right;
    }
    .high-match { background-color: #e6f4ea; color: #34a853; }
    .mid-match { background-color: #fff4e5; color: #fbbc05; }
    .info-box {
        background: rgba(255,255,255,0.4);
        padding: 20px;
        border-radius: 16px;
        font-size: 13px;
        color: #666;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BRAND LOADING LOGIC ---
@st.cache_data
def load_brands():
    CSV_FILE = 'brands.csv'
    default_brands = ["Nike", "Adidas", "Apple", "Amazon", "Tesla", "Microsoft", "Google", "Samsung", "Moving Walls"]
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            return df['brand_name'].tolist()
        except:
            return default_brands
    return default_brands

BRAND_DATABASE = load_brands()

# --- HEADER & STATS ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Brand Suggester")
    st.caption("Intelligent brand discovery by Moving Walls")
with col2:
    st.image("https://www.movingwalls.com/wp-content/uploads/2023/05/cropped-MW-logo-1.png", width=150)

# Dashboard Cards
s1, s2 = st.columns(2)
s1.metric("Total Brands", len(BRAND_DATABASE))
s2.metric("System Status", "Active")

# --- SEARCH HISTORY LOGIC ---
if 'history' not in st.session_state:
    st.session_state.history = []

def add_to_history(brand):
    if brand not in st.session_state.history:
        st.session_state.history.insert(0, brand)
        st.session_state.history = st.session_state.history[:5]

# --- MAIN SEARCH ---
query = st.text_input("Start typing (e.g., nkee)...", key="search_input")

if len(query) >= 2:
    suggestions = []
    for brand in BRAND_DATABASE:
        score = fuzz.ratio(query.lower(), brand.lower())
        if query.lower() == brand.lower(): score = 100
        elif query.lower() in brand.lower(): score = max(score, 95)
        
        if score > 45:
            suggestions.append({"brand": brand, "score": score})

    # SORT & LIMIT TO TOP 2
    final_results = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:2]

    if not final_results:
        st.warning("No matching brands found")
    else:
        st.write("### Top 2 Suggestions")
        for item in final_results:
            badge_type = "high-match" if item['score'] >= 80 else "mid-match"
            
            # Row Layout
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{item['brand']}**")
                c2.markdown(f'<span class="score-badge {badge_type}">{round(item["score"])}% Match</span>', unsafe_allow_html=True)
                
                if st.button(f"Select {item['brand']}", key=item['brand']):
                    add_to_history(item['brand'])
                    st.success(f"Selected {item['brand']}")

# --- HISTORY SECTION ---
if st.session_state.history:
    st.divider()
    h_col1, h_col2 = st.columns([4, 1])
    h_col1.write("**Recent Searches**")
    if h_col2.button("Clear History"):
        st.session_state.history = []
        st.rerun()
    
    st.write(" / ".join([f"`{h}`" for h in st.session_state.history]))

# --- FOOTER ---
st.markdown("""
    <div class="info-box">
        <strong>💡 Pro Tip:</strong> Our engine uses RapidFuzz logic. It finds brands even with typos. 
        Top 2 results are shown based on the highest matching percentage.
    </div>
    <br><center><small>© 2026 Moving Walls Media Technology Group</small></center>
    """, unsafe_allow_html=True)