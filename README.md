# StandardsFinder 🇮🇳

**StandardsFinder** is an AI-powered recommendation engine that converts unstructured procurement specifications into the most applicable **Indian Standards (BIS / IS codes)** ranked by relevance.

Built for **Smart India Hackathon Problem SIH26108** (*Ministry of Consumer Affairs, Food & Public Distribution*), it assists public procurement officers, GeM portal buyers, and industry engineers in ensuring compliance with mandatory Bureau of Indian Standards (BIS) and Quality Control Orders (QCOs).

---

## ⚡ Tech Stack

- **Backend**: Python 3.11+ / FastAPI / scikit-learn (TF-IDF + Cosine Similarity + Keyword Boosting + Domain Synonym Expansion).
  - *Ultra-lightweight (< 100MB RAM footprint)*: Built without heavy deep-learning dependencies so it runs reliably on Render's 512MB free tier.
- **Frontend**: React 19 + Vite + Tailwind CSS + Lucide Icons.
- **Data**: Curated catalog of 87 realistic Indian Standards across 9 procurement categories (`backend/data/standards.json`).

---

## 📁 Project Structure

```
├── backend/
│   ├── data/
│   │   └── standards.json       # 87 Indian Standards across 9 categories
│   ├── main.py                  # FastAPI app & endpoints
│   ├── recommender.py           # Preprocessing, TF-IDF & keyword-boosting engine
│   ├── requirements.txt         # Lightweight Python dependencies
│   ├── render.yaml              # Render deployment configuration
│   ├── test_recommender.py      # Automated recommendation verification
│   └── .env.example             # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Responsive search UI, results cards & modal
│   │   ├── index.css            # Tailwind CSS base styles
│   │   └── main.jsx             # React entry point
│   ├── index.html               # Semantic HTML & Google fonts
│   ├── package.json             # React, Vite, Tailwind CSS dependencies
│   ├── vite.config.js           # Vite configuration & backend proxy
│   ├── vercel.json              # Vercel SPA routing configuration
│   └── .env.example             # Frontend environment template
├── README.md                    # Setup, architecture & deployment guide
└── .gitignore                   # Python & Node ignore rules
```

---

## 📊 Standards Coverage (87 Standards across 9 Domains)

1. **Cement (10)**: IS 8112 (43 Grade OPC), IS 12269 (53 Grade OPC), IS 269 (33/43/53 Grade OPC), IS 1489 Pt 1 & 2 (PPC Fly Ash & Calcined Clay), IS 455 (PSC Slag Cement), IS 8041, IS 12330, IS 3466, IS 6909.
2. **Steel (10)**: IS 1786 (TMT Deformed Rebars Fe 415/500/500D/550/600), IS 2062 (Structural Steel E250/E350), IS 432 Pt 1 (Mild Steel Bars), IS 2830, IS 1367 (Fasteners), IS 277 (GI Sheets), IS 1161, IS 1079, IS 1239 Pt 1, IS 1875.
3. **Electrical (11)**: IS 694 (PVC Cables up to 1100V), IS 1180 Pt 1 (Distribution Transformers 11kV/433V), IS/IEC 60898 Pt 1 (MCBs), IS 3854 (Switches), IS 1293 (Plugs/Sockets), IS 16102 Pt 1 (LED Lamps), IS 3043 (Earthing), IS 7098 Pt 1 & 2 (LT/HT XLPE Cables), IS 2026 Pt 1, IS 9857.
4. **Food & Rations (11)**: IS 1155 (Chakki Atta / Wheat Flour), IS 14543 (Packaged Drinking Water), IS 13428 (Natural Mineral Water), IS 1165 (Milk Powder), IS 515 (Refined Sugar), IS 1005 (Edible Salt), IS 548 Pt 1 (Oils & Fats), IS 4251, IS 15757 (Fortified Atta), IS 16076 (Fortified Oil), IS 1488.
5. **Textiles (10)**: IS 16289 (3-Ply Surgical Face Masks), IS 17349 (Healthcare Coveralls PPE), IS 15809 (High Visibility Jackets), IS 1969 Pt 1 (Fabric Tensile Strength), IS 2977 (Terry Towels), IS 15852 (Uniform Fabrics), IS 177, IS 1259 (Rexine), IS 16654 (Geotextiles), IS 1390.
6. **Pipes (9)**: IS 4985 (uPVC Pipes for Potable Water), IS 15778 (CPVC Hot/Cold Water Pipes), IS 8329 (Ductile Iron DI Pipes K7/K9), IS 14333 (HDPE Sewerage Pipes), IS 1239 Pt 2 (Steel Fittings), IS 458 (RCC Spun Pipes), IS 13592 (SWR Drainage Pipes), IS 14846, IS 1536.
7. **Paints (8)**: IS 154 (Synthetic Enamel Paint), IS 5410 (Cement Paint), IS 15489 (Plastic Emulsion Paint), IS 2074 (Red Oxide Zinc Chrome Primer), IS 101 Pt 1, IS 2932, IS 13183 (PU Coatings), IS 341.
8. **Packaging (9)**: IS 2771 Pt 1 (Corrugated Fibreboard Boxes), IS 10221 (Anti-Corrosion Packaging VCI), IS 15644 (Wooden Crates), IS 12795 (Milk Film Pouches), IS 14001 (Cement Sacks), IS 14005 (Food Grain Sacks), IS 10146 (Food Contact Plastics), IS 15886, IS 13947.
9. **Safety Equipment (9)**: IS 2925 (Industrial Safety Helmets), IS 15683 (Portable Fire Extinguishers ABC/CO2), IS 15298 Pt 2 (Steel Toe Safety Footwear), IS 3521 Pt 1 (Full Body Safety Harnesses), IS 8521 Pt 1 (Face Shields), IS 9473 (FFP2 / N95 Particulate Respirators), IS 2573, IS 6994 Pt 1, IS 8808.

---

## 🚀 Quickstart: Local Setup

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 1. Run the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API will be live at: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173` in your browser.
- Vite automatically proxies `/api` requests to `http://localhost:8000`.

---

## 🔌 API Endpoints

### 1. Recommend Standards
- **Endpoint**: `POST /api/recommend`
- **Request Body**:
```json
{
  "query": "Portland cement for residential construction, 43 grade",
  "top_k": 3
}
```
- **Response**:
```json
[
  {
    "is_code": "IS 8112:2013",
    "title": "43 Grade Ordinary Portland Cement - Specification",
    "category": "Cement",
    "score": 100.0,
    "matched_keywords": [
      "cement",
      "opc",
      "43 grade",
      "ordinary portland cement",
      "compressive strength",
      "residential construction"
    ],
    "reason": "High confidence match in Cement category on 'cement', 'opc', '43 grade'. Formulated specifically for requirements defined in IS 8112:2013."
  }
]
```

### 2. Browse Standards Catalog
- **Endpoint**: `GET /api/standards?page=1&page_size=10&category=Cement&search=opc`
- **Response**:
```json
{
  "total": 10,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "standards": [ ... ]
}
```

### 3. Health Check
- **Endpoint**: `GET /api/health`
- **Response**:
```json
{
  "status": "ok",
  "standards_count": 87,
  "version": "1.0.0"
}
```

---

## 🌐 Deployment Guide

### A. Deploy Backend to Render (Free Tier 512MB RAM)

1. Push your repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following fields:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Under **Environment Variables**, add:
   - `ALLOWED_ORIGINS`: `*` (or your frontend Vercel URL)
6. Click **Create Web Service**. Your backend URL will be e.g. `https://standardsfinder-backend.onrender.com`.

*(Alternatively, use `backend/render.yaml` with Render Blueprints).*

---

### B. Deploy Frontend to Vercel

1. In [Vercel Dashboard](https://vercel.com), click **Add New...** -> **Project**.
2. Select your repository.
3. Configure the project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
4. Under **Environment Variables**, add:
   - `VITE_API_URL`: Your Render backend URL (e.g. `https://standardsfinder-backend.onrender.com`)
5. Click **Deploy**. Vercel will build and serve your app globally.

---

## 🧪 Sample Verification Queries

| Query | Expected Standard | Category |
|---|---|---|
| `Portland cement for residential construction, 43 grade` | **IS 8112:2013** | Cement |
| `Supply of Fe 500D grade TMT deformed steel bars 12mm` | **IS 1786:2008** | Steel |
| `Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher` | **IS 15683:2018** | Safety Equipment |
| `Unplasticized PVC pipes for potable drinking water supply` | **IS 4985:2021** | Pipes |
| `Disposable 3-ply surgical face masks with meltblown filter layer` | **IS 16289:2014** | Textiles |

---

## ⚖️ License
Released under the MIT License for Smart India Hackathon (SIH26108).
