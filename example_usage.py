#!/usr/bin/env python3
"""
Example usage of the Amazon Scraper

This file demonstrates how to use the scraper to search for products on Amazon.
Simply modify the variables below and run the script.
"""

from amazon_scraper import AmazonScraper, generate_html_page
import json

def main():
    # ========================================
    # MODIFY THESE VARIABLES
    # ========================================
    
    search_term = "MacBook Air M2"    # Change this to your desired product
    
    print(f"🔍 Searching for: {search_term}")
    print("⏳ Please wait while we search...")
    
    # Initialize the scraper
    scraper = AmazonScraper()
    
    # Search for products
    products = scraper.scrape_amazon_search(search_term)
    
    if not products:
        print("No products found. Trying fallback search...")
        products = scraper.scrape_with_fallback()
    
    # Display results
    print("\n" + "="*50)
    print("📊 SEARCH RESULTS")
    print("="*50)
    
    for product in products[:5]:  # Show first 5 products
        print(f"🎯 Product: {product['productName']}")
        print(f"💰 Price: {product['price']}")
        print("-"*50)
    
    # Save detailed results
    output_file = "search_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Detailed results saved to: {output_file}")
    
    # Generate HTML page with results
    html_file = "amazon_products.html"
    generate_html_page(products, html_file)
    print(f"🌐 HTML page generated: {html_file}")

if __name__ == "__main__":
    main()