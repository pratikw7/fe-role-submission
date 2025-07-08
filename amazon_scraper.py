#!/usr/bin/env python3
"""
Amazon Product Scraper

This script scrapes product data from Amazon homepage and generates a responsive HTML page.
Implements human-like behaviors to avoid bot detection including random delays and realistic headers.

WARNING: This script is for educational purposes only. Always respect robots.txt and
website terms of service when scraping.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        """Initialize the Amazon scraper with configuration."""
        self.base_url = "https://www.amazon.in"
        self.session = requests.Session()
        
        # Search terms to try if one fails
        self.search_terms = [
            "electronics",
            "books", 
            "home+kitchen",
            "clothing",
            "sports",
            "toys"
        ]
        
        # List of realistic user agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Configure session with realistic settings
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def get_random_headers(self) -> Dict[str, str]:
        """Generate random realistic headers to mimic human browsing."""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.amazon.in/'
            ]),
            'Origin': 'https://www.amazon.in',
            'DNT': '1',
            'Sec-GPC': '1'
        }
        return headers

    def human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Introduce random delays to simulate human browsing patterns."""
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)

    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with error handling and retry logic."""
        for attempt in range(retries):
            try:
                # Update headers for each request
                self.session.headers.update(self.get_random_headers())
                
                # Add initial delay before request
                if attempt == 0:
                    self.human_delay(2.0, 5.0)
                else:
                    self.human_delay(5.0, 10.0)  # Longer delay for retries
                
                logger.info(f"Making request to {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    logger.warning("Rate limited, waiting longer...")
                    self.human_delay(10.0, 20.0)
                else:
                    logger.warning(f"Request failed with status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    self.human_delay(5.0, 10.0)
        
        return None

    def parse_product_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Parse product data from Amazon search results.
        
        Note: Amazon's HTML structure changes frequently. These selectors may need updates.
        The script looks for common product container patterns used on Amazon's search results.
        """
        products = []
        
        # Updated selectors for Amazon search results (more likely to work)
        product_selectors = [
            '[data-component-type="s-search-result"]',  # Primary search results
            '[data-asin][data-component-type="s-search-result"]',  # More specific search results
            '.s-result-item[data-component-type="s-search-result"]',  # Alternative format
            '[data-cel-widget*="search_result"]',  # Widget-based results
            '.s-result-item:not([data-component-type="s-search-result"])',  # Fallback result items
        ]
        
        for selector in product_selectors:
            containers = soup.select(selector)
            logger.info(f"Found {len(containers)} products with selector: {selector}")
            
            for container in containers[:20]:  # Limit to first 20 products
                try:
                    product = self.extract_product_info(container)
                    if product and product.get('productName'):  # Only require name to be present
                        products.append(product)
                        # Small delay between processing products
                        self.human_delay(0.1, 0.5)
                        
                except Exception as e:
                    logger.warning(f"Error parsing product: {e}")
                    continue
            
            if products:  # If we found products with this selector, break
                break
        
        logger.info(f"Successfully parsed {len(products)} products")
        return products

    def extract_product_info(self, container) -> Optional[Dict[str, str]]:
        """Extract individual product information from a container element."""
        product = {}
        
        # Extract product name - updated selectors for current Amazon structure
        name_selectors = [
            'h2.a-size-mini span',
            'h2 a span',
            '.a-size-base-plus',
            '.a-size-medium',
            'h2.s-size-mini span',
            '[data-cy="title-recipe-title"]',
            '.a-size-mini span',
            'h3 a span',
            '.s-size-mini span'
        ]
        
        product['productName'] = self.find_text_by_selectors(container, name_selectors)
        
        # Extract price - updated selectors for current Amazon structure
        price_selectors = [
            '.a-price.a-text-price.a-size-medium.a-color-base .a-offscreen',
            '.a-price-whole',
            '.a-price .a-offscreen',
            '.a-price-symbol',
            '.a-price-range .a-offscreen',
            '.a-price-range',
            '[data-a-size="xl"] .a-offscreen',
            '.a-price.a-text-price .a-offscreen'
        ]
        
        price_text = self.find_text_by_selectors(container, price_selectors)
        product['price'] = self.clean_price(price_text) if price_text else "Price not available"
        
        # Extract product link - updated selectors for current Amazon structure
        link_selectors = [
            'h2.a-size-mini a',
            'h2 a',
            '[data-cy="title-recipe-title"] a',
            '.a-link-normal[href*="/dp/"]',
            'a[href*="/dp/"]',
            '.a-link-normal'
        ]
        
        link_element = self.find_element_by_selectors(container, link_selectors)
        if link_element and link_element.get('href'):
            href = link_element['href']
            product['link'] = href if href.startswith('http') else f"https://www.amazon.in{href}"
        else:
            product['link'] = ""
        
        # Extract image URL - updated selectors for current Amazon structure
        img_selectors = [
            '.s-image',
            '.a-dynamic-image',
            'img[data-src*="amazon"]',
            'img[src*="amazon"]',
            'img[data-src]',
            '.rush-component img'
        ]
        
        img_element = self.find_element_by_selectors(container, img_selectors)
        if img_element:
            product['image_url'] = img_element.get('src') or img_element.get('data-src', '')
        else:
            product['image_url'] = ""
        
        # Only return if we have at least a name (relaxed requirement)
        name = product.get('productName')
        if name is not None and len(name.strip()) > 0:
            return product
        
        return None

    def find_text_by_selectors(self, container, selectors: List[str]) -> Optional[str]:
        """Find text content using multiple selectors."""
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None

    def find_element_by_selectors(self, container, selectors: List[str]):
        """Find element using multiple selectors."""
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element
        return None

    def clean_price(self, price_text: str) -> str:
        """Clean and format price text."""
        if not price_text:
            return "Price not available"
        
        # Remove extra whitespace and common price prefixes
        price_text = price_text.strip()
        price_text = price_text.replace('$', '$').replace('Price:', '').strip()
        
        # If price doesn't start with $, add it
        if price_text and not price_text.startswith('$'):
            price_text = f"${price_text}"
        
        return price_text if price_text else "Price not available"

    def scrape_amazon_search(self, search_term: str = "electronics") -> List[Dict[str, str]]:
        """Main method to scrape Amazon search results for product data."""
        logger.info(f"Starting Amazon search scraping for: {search_term}")
        
        # Construct search URL
        search_url = f"{self.base_url}/s?k={search_term}&ref=sr_pg_1"
        
        # Make request to Amazon search page
        response = self.make_request(search_url)
        if not response:
            logger.error(f"Failed to fetch Amazon search results for: {search_term}")
            return []
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product data
        products = self.parse_product_data(soup)
        
        logger.info(f"Scraping completed for '{search_term}'. Found {len(products)} products.")
        return products

    def scrape_with_fallback(self) -> List[Dict[str, str]]:
        """Try multiple search terms until we find products."""
        all_products = []
        
        for search_term in self.search_terms:
            logger.info(f"Trying search term: {search_term}")
            products = self.scrape_amazon_search(search_term)
            
            if products:
                all_products.extend(products)
                logger.info(f"Success with '{search_term}': {len(products)} products found")
                break
            else:
                logger.warning(f"No products found for '{search_term}', trying next term...")
                self.human_delay(3.0, 7.0)  # Wait before trying next term
        
        return all_products

def generate_html_page(products: List[Dict[str, str]], output_file: str = "amazon_products.html"):
    """Generate a responsive HTML page with scraped product data using Tailwind CSS."""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Products - Scraped Data</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .product-card {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        .product-image {{
            aspect-ratio: 1;
            object-fit: cover;
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-12">
            <h1 class="text-4xl font-bold text-gray-800 mb-4">Amazon Products</h1>
            <p class="text-gray-600 text-lg">Scraped on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p class="text-gray-500 text-sm mt-2">Found {len(products)} products</p>
        </header>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {generate_product_cards(products)}
        </div>
        
        <footer class="mt-16 text-center text-gray-500 text-sm">
            <p>Data scraped from Amazon for educational purposes only.</p>
            <p class="mt-2">Always respect website terms of service and robots.txt.</p>
        </footer>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    logger.info(f"HTML page generated: {output_file}")

def generate_product_cards(products: List[Dict[str, str]]) -> str:
    """Generate HTML cards for each product."""
    cards = []
    
    for i, product in enumerate(products):
        # Fallback image if none provided
        image_url = product.get('image_url', '') or 'https://via.placeholder.com/300x300/f0f0f0/999999?text=No+Image'
        
        card_html = f"""
        <div class="product-card bg-white rounded-lg shadow-md overflow-hidden">
            <div class="aspect-square bg-gray-100 flex items-center justify-center">
                <img src="{image_url}" 
                     alt="{product.get('productName', 'Product')}" 
                     class="product-image w-full h-full object-contain"
                     onerror="this.src='https://via.placeholder.com/300x300/f0f0f0/999999?text=No+Image'">
            </div>
            <div class="p-4">
                <h3 class="font-semibold text-sm text-gray-800 mb-2 line-clamp-2 h-10 overflow-hidden">
                    {product.get('productName', 'Product Name Not Available')[:100]}{'...' if len(product.get('productName', '')) > 100 else ''}
                </h3>
                <p class="text-lg font-bold text-green-600 mb-3">
                    {product.get('price', 'Price not available')}
                </p>
                <a href="{product.get('link', '#')}" 
                   target="_blank" 
                   class="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200"
                   {'style="pointer-events: none; opacity: 0.5;"' if not product.get('link') else ''}>
                    View Product
                </a>
            </div>
        </div>"""
        
        cards.append(card_html)
    
    return '\n'.join(cards)

def main():
    """Main function to demonstrate the scraper usage."""
    print("Amazon Product Scraper")
    print("=" * 50)
    print("WARNING: This script is for educational purposes only.")
    print("Always respect website terms of service and robots.txt.")
    print("=" * 50)
    
    # Initialize scraper
    scraper = AmazonScraper()
    
    # Scrape products using fallback search terms
    products = scraper.scrape_with_fallback()
    
    if products:
        print(f"\nSuccessfully scraped {len(products)} products!")
        
        # Generate HTML page
        generate_html_page(products)
        
        # Save data as JSON for debugging
        with open('scraped_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print("Files generated:")
        print("- amazon_products.html (responsive webpage)")
        print("- scraped_products.json (raw data)")
        
        # Display sample products
        print("\nSample products:")
        for i, product in enumerate(products[:3]):
            print(f"\n{i+1}. {product['productName']}")
            print(f"   Price: {product['price']}")
            print(f"   Link: {product['link'][:50]}...")
    else:
        print("No products were scraped. This could be due to:")
        print("- Amazon's anti-bot measures")
        print("- Changes in Amazon's HTML structure")
        print("- Network issues")
        print("- IP blocking")

if __name__ == "__main__":
    main()