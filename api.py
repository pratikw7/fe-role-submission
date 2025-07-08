from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from amazon_scraper import AmazonScraper
from typing import List, Dict, Optional

app = FastAPI()

class SearchRequest(BaseModel):
    country: str
    query: str

@app.post("/api/search")
async def search_products(request: SearchRequest) -> List[Dict[str, str]]:
    try:
        # Initialize scraper
        scraper = AmazonScraper()
        
        # Update base URL based on country
        country_domains = {
            "US": "https://www.amazon.com",
            "UK": "https://www.amazon.co.uk",
            "CA": "https://www.amazon.ca",
            "IN": "https://www.amazon.in",
            # Add more country domains as needed
        }
        
        if request.country not in country_domains:
            raise HTTPException(status_code=400, detail=f"Unsupported country code: {request.country}")
        
        scraper.base_url = country_domains[request.country]
        
        # Search for products
        products = scraper.scrape_amazon_search(request.query)
        
        if not products:
            return []
            
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 