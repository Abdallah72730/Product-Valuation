# Product Valuation — AI-Powered Image Analysis & Pricing Pipeline

A modular Python backend that accepts product images, runs them through a Vision API for automated visual analysis, scrapes market data, parses and scores the results, and serves structured valuation output via a local REST server.

Built as a personal project to explore how image recognition and web data can be combined into a real automated pipeline — the kind of data-processing architecture used in industrial QA systems and e-commerce pricing tools.

---

## What It Does

1. **Image Input** — accepts a product image
2. **Vision Analysis** (`vision_api.py`) — sends the image to a Vision API and extracts visual attributes (condition, category, identifying features)
3. **Market Scraping** (`scraper.py`) — uses the extracted attributes to search for comparable listings online
4. **HTML Parsing** (`parser.py`) — pulls structured pricing and product data from the scraped pages
5. **Valuation Analysis** (`analyzer.py`) — processes the parsed data and calculates an estimated value range
6. **Orchestration** (`orchestrator.py`) — coordinates the full pipeline from image input to final result
7. **REST Server** (`server.py`) — exposes the pipeline as a local API endpoint so it can be called from other apps or a frontend

---

## Project Structure

```
Product-Valuation/
├── vision_api.py       # Vision API integration — image → extracted attributes
├── scraper.py          # Web scraper — attributes → raw market HTML
├── parser.py           # HTML parser — raw HTML → structured pricing data
├── analyzer.py         # Analysis engine — structured data → valuation estimate
├── orchestrator.py     # Pipeline coordinator — ties all modules together
├── server.py           # REST server — exposes the pipeline as an API
├── config.py           # Configuration and environment variable loading
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template (API keys go here)
└── .gitignore
```

---

## Tech Stack

- **Python** — core language throughout
- **Vision API** — automated image analysis and feature extraction
- **REST / HTTP** — server.py exposes endpoints for pipeline access
- **Web scraping** — requests + HTML parsing for real-world market data
- **Environment variables** — API keys managed securely via `.env`, never hardcoded

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- A Vision API key (configured in `.env`)

### Installation

```bash
# Clone the repo
git clone https://github.com/Abdallah72730/Product-Valuation.git
cd Product-Valuation

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API key
```

### Running the Server

```bash
python server.py
```

The server will start locally. Send a POST request with an image to receive a valuation response.

### Running the Pipeline Directly

```bash
python orchestrator.py
```

---

## Key Design Decisions

**Modular architecture** — each file has one job. `vision_api.py` only handles the API call. `parser.py` only handles HTML parsing. This makes the pipeline easy to debug, test, or swap out individual components (e.g. switching Vision APIs without touching the analysis logic).

**Secure API key handling** — all credentials are stored in `.env` and loaded through `config.py`. The `.env` file is gitignored so keys are never exposed in the repository.

**Separation of scraping and parsing** — `scraper.py` handles HTTP requests and raw HTML retrieval, while `parser.py` handles the extraction logic. This separation means scraping failures don't affect the parser and vice versa.

---

## What I Learned

- How to structure a multi-module Python project cleanly
- Integrating third-party Vision APIs and handling their response formats
- Web scraping and HTML parsing with real-world, unpredictable page structures
- Building a simple REST server to expose backend logic as an API
- Managing secrets securely with environment variables

---

## Author

**Abdallah Najmudin Syed** — Computer Programming Student, Red Deer Polytechnic  
