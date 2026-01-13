from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, Form
from typing import Optional 
import sys
import os 
import time 

#adding current directory to python path so we can import Phase 1 modules
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

#importing phase 1, 2 & 3 modules
try:
    from scraper import fetch_html_scraperapi   
    from parser import extract_prices_from_html
    from analyzer import generate_report
    print("successfully imported modules ")

    try:
        from vision_api import analyze_image
        import inspect
        if inspect.iscoroutinefunction(analyze_image):
            analyze_image_func = analyze_image
        else:
            async def analyze_image_func(image_bytes):
                return analyze_image(image_bytes)

        try: 
            from vision_api import Google_api_key as key
            Google_api_key = key
        except:
            Google_api_key = None

        print(f"vision_api imported: API key: {'Set' if Google_api_key else 'Not set' }")
    except ImportError as e:
        print(f"vision_api import failed: {e}")

        #create fallback
        async def analyze_image_func(image_bytes):
            return {
                "labels":["product"],
                "text":[],
                "best_guess": "product",
                "error":"Google Vision ot available"
            }
except:
    print(f"Error importing modules: {e}")
    sys.exit(1)


#initialize fastAPI app
app = FastAPI(title="Valuation API", version="1.0")

#configuring CORS (allows the website to call this API)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Home endpoint - API status."""
    return{
        "status":"online",
        "service":"Product Valuation API",
        "phase":2,
        "endpoints":{
            "/health":"Check API health",
            "/value/{item_name}": "Get valuation for an item",
            "/analyze_image":"Upload image for recognition and valuation",
            "/analyze-html":"Direct HTML analysis endpoint"
        }
    }

@app.get("/health")
def health_check():
    """Check if api dependencies are working"""

    # google_status = "configured" if Google_api_key else "Not configured"
    return {"status":"healthy", "timestamp":time.time()}

@app.get("/value/{item_name}")
def get_valuation(
    item_name: str,
    condition: Optional[str] = Query("Good", description="Item condition: New, Good, Fair, Poor"),
    force_refresh: Optional[bool] = Query("False", description="Force fresh scrape instead of cache")):

    """
    Main valuation endpoint.
    Example: GET /value/iPhone%2013?condition=Good&force_refresh=true
    """
    try:
        print(f"Valuation request: {item_name}, condition: {condition}")
        #fetch html from eBay (phase 1 scraper)
        html_content = fetch_html_scraperapi(item_name)
        if not html_content or len(html_content)<100:
            raise HTTPException(status_code=404, detail=f"No data found for: {item_name}")

        #Extract prices 
        prices = extract_prices_from_html(html_content)
        if not prices:
            raise HTTPException(status_code = 404, detail=f"No valid prices found for '{item_name}' ")

        #generate report
        report = generate_report(prices)


        #condition adjustment
        adjusted_value = apply_condition_adjustment(report["median"], condition)
        #prepare response

        response = {
            "item":item_name,
            "condition":condition,
            "data_summary":{
                "sold_listiings_analyzed":report["data_points"],
                "price_range":f"${report["minimum"]:.2f} - ${report["maximum"]:.2f}",
                "median_price":report["median"],
                "price_spread":report["range"] 
            },
            "valuation" : {
                "estimated_value": adjusted_value,
                "confidence":calculate_confidence(report["data_points"], report['range']),
                "note": "Based on eBay sold listings"
            },
            "metadata":{
                "source":"eBay sold listings",
                "cache_used": not force_refresh,
                "processing_time_ms":0
            }
        }

        return response

    except HTTPException:
        raise 
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail = f"Internal Server error: {str(e)}")


def apply_condition_adjustment(median_price: float, condition: str) -> float:
    """Adjusting prices based on conditions"""

    condition_multipliers = {
        "New": 1.4,
        "Like New": 1.2,
        "Good": 1.0,
        "Fair": 0.8,
        "Poor":0.6
    }

    multiplier = condition_multipliers.get(condition, 1.0)
    return round(median_price*multiplier, 2)

def calculate_confidence(data_points: int, price_range:float) -> str:

    if data_points < 5:
        return "Low (insufficient data)"
    elif price_range > (data_points * 100):
        return "Medium (high price variability)"
    else:
        return "High (reliable data)"


"""
implements image recognition 
"""
@app.post("/analyze_image")
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    condition: Optional[str] = Form("Good")
):
    #checks if it is an image 
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code = 400, detail="Please upload an image file" )
    
    
    try:
        #read image 
        image_data = await file.read()

        #analyze with google
        analysis =  await analyze_image_func(image_data)

        search_query = analysis.get("best_guess", "unknown")
        print(f"Searching for: {search_query}")

        html_content = fetch_html_scraperapi(search_query)
        
        if not html_content or len(html_content) < 100:
            raise HTTPException(status_code=404, detail=f"No data found for: {search_query}")
        
        prices = extract_prices_from_html(html_content)
        if not prices:
            raise HTTPException(status_code=404, detail=f"No valid prices found for:{search_query}")
        
        report = generate_report(prices)
        adjusted_value = apply_condition_adjustment(report["median"], condition)

        return {
             "success": True,
            "detected_product": search_query,
            "condition": condition,
            "estimated_value": adjusted_value,
            "data_points": report["data_points"],
            "price_range": f"${report['minimum']:.2f} - ${report['maximum']:.2f}",
            "labels_found": analysis.get("labels", [])[:3]
        }    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"image analysis failed: {str(e)}"  )    


@app.post("/analyze-html")
async def analyze_raw_html(html_content: str = ""):
    """
    Debug endpoint: Analyze raw HTML content directly
    Useful for testing parser without scraping  
    """
    if not html_content:
        raise HTTPException(status_code=400, detail="No HTML content provided")
    
    prices = extract_prices_from_html(html_content)
    report = generate_report(prices)

    return {
        "analysis":report,
        "note":"direct HTML analysis",
        "prices_found": len(prices)
    }





if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port= 8000, reload= True)