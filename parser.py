import re 

def extract_prices_from_html(html : str) -> list:

    if not html:
        return []

    # Strategy: Extract candidates, then VALIDATE
    candidates = re.findall(r'\$?\s*[\d,.]+', html)
    
    print(f"[Parser] Found {len(candidates)} raw candidates")
    
    valid_prices = []
    
    for candidate in candidates:
        # VALIDATION 1: Count dots in ORIGINAL string
        # "12.365.23" → 2 dots → REJECT ENTIRE THING
        if candidate.count('.') > 1:
            continue
        
        # VALIDATION 2: No dot at end
        if candidate.endswith('.'):
            continue
        
        # Clean
        clean = candidate.replace('$', '').replace(',', '').strip()
        
        # TRUNCATION (not rounding)
        if '.' in clean:
            parts = clean.split('.')
            integer = parts[0]
            decimal = parts[1]
            
            if len(decimal) > 2:
                # Simple truncation: "365" → "36"
                clean = f"{integer}.{decimal[:2]}"
            elif len(decimal) == 0:
                # Shouldn't happen due to validation, but safe
                clean = integer
        
        # Convert and validate range
        try:
            price = float(clean)
            if 0.99 < price < 100000:  # Realistic range
                valid_prices.append(price)
            else:
                continue
        except ValueError:
            continue
    
    print(f"[Parser] Kept {len(valid_prices)} valid prices")
    return valid_prices


if __name__ == "__main__":

    html = """
    <div class = "s-item__price">299.99</div>
    <span>Price : USD 450.50 </span>
    <div>1,299.99</div>
    <div>Invalid: 12.345.36</div>
    """

    parsed_prices = extract_prices_from_html(html)

    print("Parsed prices from provided html is: ", parsed_prices)
