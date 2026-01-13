import requests
import base64
try:
    from config import Google_api_key
except:
    load_dotenv()
    Google_api_key = os.getenv("GOOGLE_API_KEY")


response = ""
"""
this function:
1. sends image to Google vision api
2. returns what google thinks is in the image 
"""
def analyze_image(image_bytes):
    #encode image to base64 (google's required format)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    #prepare the request
    request_body = {
        "requests":[{
            "image":{"content":encoded_image},
            "features":[
                
                    {"type":"LABEL_DETECTION", "maxResults":10},
                    {"type":"TEXT_DETECTION", "maxResults":5}
                
            ]
        }]
    }

    #send to google
    response = requests.post(
        f"https://vision.googleapis.com/v1/images:annotate?key={Google_api_key}",
        json=request_body
    )

    if response.status_code == 200:
        data = response.json()
        return parse_google_response(data)
    else:
        return {"error":f"API Error: {response.status_code}","details": response.text}

"""
extracts useful information from google's response
"""
def parse_google_response(data):
    
    result= {
        "labels":[],
        "text":[],
        "best_guess" :""
    }

    try:
        #get labels (what google sees)
        labels = data.get("responses", [{}])[0].get("labelAnnotations", [])
        result["labels"] = [label["description"] for label in labels] 

        #get text (any readable text)
        text_blocks = data.get("responses", [{}])[0].get("textAnnotations", [])
        if text_blocks:
            #first item is all text, rest are individual words
            full_text = text_blocks[0].get("description","")
            result["text"] = full_text.split("\n")
        
        #best guess is the first label
        if result["labels"]:
            result["best_guess"] = result["labels"][0]
        elif result['text']:
            result["best_guess"] = result["text"][0]
        else:
            result["best_guess"] = "unknown"
    except:
        result["error"] = f"Failed to parse: {str(e)}"


    return result

