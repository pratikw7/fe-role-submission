# Amazon Product Scraper API

A FastAPI-based API that scrapes product information from Amazon based on search queries. Supports multiple Amazon country domains.

## Live API
Deployed URL: https://fe-role-submission.vercel.app/

## Working Proof
### Test Case 1: iPhone 16 Search
![API Working Proof 1](working%20proof%20image.PNG)

### Test Case 2: iPhone 15 Search
![API Working Proof 2](working%20proof%20%232.png)

## Testing the API

You can test the deployed API using PowerShell:

```powershell
$body = @{
    country = "US"
    query = "iPhone 16 Pro, 128GB"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://fe-role-submission.vercel.app/api/search" -Method Post -ContentType "application/json" -Body $body
```

This will return product details including name, price, and links from Amazon.

## Features

- Search products across different Amazon domains (US, UK, CA, IN)
- Returns product details including name, price, link, and image URL
- Built with anti-bot detection measures
- Ready for Vercel deployment

## API Usage

### Search Products Endpoint

```bash
curl -X POST https://fe-role-submission.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

#### Request Format
```json
{
    "country": "US",  // Supported: US, UK, CA, IN
    "query": "search term"
}
```

#### Response Format
```json
[
    {
        "productName": "Product Name",
        "price": "$999.99",
        "link": "Product URL",
        "image_url": "Image URL"
    }
]
```

## Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/amazon-scraper-api.git
cd amazon-scraper-api
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the development server
```bash
uvicorn api:app --reload
```

4. Test the API locally
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

## Deployment

This project is configured for Vercel deployment. Simply:

1. Push to GitHub
2. Import the repository in Vercel
3. Deploy

## Warning

This scraper is for educational purposes only. Always respect websites' terms of service and robots.txt when scraping. 
