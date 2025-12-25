# price_parser.py - PRODUCTION VERSION
import re

def extract_prices_from_html(html: str) -> list:
    """Extract ONLY actual product prices from eBay HTML"""
    if not html:
        return []
    
    # TARGET SPECIFIC EBAY PRICE CLASSES
    price_patterns = [
        r'<span[^>]*class="[^"]*s-item__price[^"]*"[^>]*>\$?\s*([\d,]+\.?\d{0,2})',
        r'<div[^>]*class="[^"]*s-item__price[^"]*"[^>]*>\$?\s*([\d,]+\.?\d{0,2})',
        r'class="[^"]*price[^"]*"[^>]*>.*?\$\s*([\d,]+\.?\d{0,2})',  # Generic fallback
    ]
    
    candidates = []
    for pattern in price_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        candidates.extend(matches)
    
    print(f"[Parser] Found {len(candidates)} raw candidates")
    
    valid_prices = []
    
    for candidate in candidates:
        if candidate.count('.') > 1:
            continue
        if candidate.endswith('.'):
            continue
        
        clean = candidate.replace('$', '').replace(',', '').strip()
        
        if not clean:
            continue
        
        try:
            price = float(clean)
            # Realistic secondhand product range
            if 5.00 <= price <= 50000:
                valid_prices.append(price)
        except ValueError:
            continue
    
    print(f"[Parser] Kept {len(valid_prices)} valid prices")
    
    # Remove outliers if enough data
    if len(valid_prices) >= 4:
        valid_prices = remove_outliers_iqr(valid_prices)
    
    return valid_prices


def remove_outliers_iqr(prices: list) -> list:
    """Remove statistical outliers using Interquartile Range method"""
    if len(prices) < 4:
        return prices
    
    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    
    q1_index = n // 4
    q3_index = (3 * n) // 4
    
    q1 = sorted_prices[q1_index]
    q3 = sorted_prices[q3_index]
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
    
    removed = len(prices) - len(filtered_prices)
    if removed > 0:
        print(f"[Outlier Filter] Removed {removed} outliers")
        print(f"[Outlier Filter] Kept range: ${lower_bound:.2f} - ${upper_bound:.2f}")
    
    # Safety: if too many removed, keep original
    if len(filtered_prices) < len(prices) * 0.5:
        print("[Outlier Filter] Too many removed - keeping original dataset")
        return prices
    
    return filtered_prices




if __name__ == "__main__":
    # Test with realistic eBay HTML structure
    html = """
    <li class="s-item">
        <span class="s-item__price">$299.99</span>
        <span class="s-item__bids">5 bids</span>
        <span class="s-item__shipping">$12.50</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$310.25</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$5.00</span>
        <span class="s-item__subtitle">Starting bid</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$450.50</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$1,299.99</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$325.00</span>
    </li>
    <li class="s-item">
        <span class="s-item__price">$289.99</span>
    </li>
    <div class="pagination">Page 1 of 23</div>
    <span class="item-count">142 results</span>
    """
    
    print("=== TESTING PARSER ===\n")
    parsed_prices = extract_prices_from_html(html)
    print(f"\nFinal parsed prices: {parsed_prices}\n")
    
    # Test with your analyzer
    from analyzer import generate_report
    
    report = generate_report(parsed_prices)
    print("=== PRICE REPORT ===")
    for key, value in report.items():
        if key != "price_list":
            print(f"{key}: {value}")