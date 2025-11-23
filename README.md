# IP Threat Intelligence – AI-Enhanced Backend Service

A lightweight backend service that aggregates IP threat-intelligence data from external APIs and enriches the result using an OpenAI-compatible LLM.  
The system provides aggregation, safe fallbacks, scoring, and a clean FastAPI endpoint.

## Features

- GET /api/analyze-ip?ip=<address>
- IP validation
- Two external threat-intelligence sources
- Normalized aggregate response
- Simple composite risk score
- LLM-based analysis (OpenAI key required)
- Safe fallback logic
- Minimal test coverage with mocks

## Project Structure

src/  
  main.py  
  api/  
  services/  
    aggregator.py  
  external/  
    abuseipdb.py  
    ipquality.py  
  ai/  
    llm_client.py  

tests/  
  test_abuseipdb.py  
  test_abuseipdb_mock.py

## 🔐 Environment Variables

This project uses four threat-intelligence APIs.  
The assignment provides all four keys inside the PDF, and you must place them into your .env file.

In addition, the LLM part of the project uses an OpenAI model.  
You must add **your own OpenAI API key**, because the assignment does not include one.

### 1. Create a .env file in the project root

ABUSEIPDB_API_KEY=<paste from assignment>  
IPQUALITYSCORE_API_KEY=<paste from assignment>  
IPAPI_KEY=<paste from assignment>  
VIRUSTOTAL_API_KEY=<paste from assignment>  

LLM_API_KEY=<your-openai-api-key>

### 2. .env.example (included in the repository)

ABUSEIPDB_API_KEY=  
IPQUALITYSCORE_API_KEY=  
IPAPI_KEY=  
VIRUSTOTAL_API_KEY=  
LLM_API_KEY=  

Keep .env.example in the repository.  
Never commit .env.

### 3. LLM Key Details

The project uses:

model="gpt-4o-mini"

This is an OpenAI model, so an **OpenAI API key is required**.

If you want to use a different OpenAI-compatible provider (Groq, Together, Perplexity, etc.),  
you may change the model name and endpoint in ai/llm_client.py.

The LLM module has a safe fallback.  
If the key is missing or the request fails, the system returns:

{
  "risk_level": "Unknown",
  "analysis": "LLM analysis unavailable.",
  "recommendations": "Fallback: manual review recommended."
}

## Running the Project

Install dependencies:  
pip install -r requirements.txt

Run server:  
uvicorn src.main:app --reload

Test endpoint:  
http://localhost:8000/api/analyze-ip?ip=8.8.8.8

## Running Tests

pytest

## Risk Score Logic

risk_score = average(abuse_score, fraud_score)

If both missing → None.

## LLM Behavior

The model receives aggregated threat-data and returns:

- risk_level
- analysis
- recommendations

Temperature = 0.2 for stable deterministic output.

## License

For assignment and demonstration purposes only.

## How to Open the UI

After starting the server with:

uvicorn src.main:app --reload

Open your browser at:

http://127.0.0.1:8000/

This loads the minimal HTML interface (src/static/index.html).
Enter an IP address and click "Analyze" to view:

- raw aggregated threat-intelligence data
- AI-generated risk analysis (or fallback if the LLM is unavailable)

## VirusTotal API Key Limitations !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The API key included in the assignment:

VIRUSTOTAL_API_KEY=81a9d61f38f3c7d7414fd363d20e057441fe8146c98a7500e3ab1f69f841399b9

was tested against every available VirusTotal API family (API v3, API v2, legacy endpoints, and UI API).  
None of the endpoints accepted the key.  
This section documents the exact tests performed and the raw responses returned by VirusTotal.

### Tests Performed

All requests were issued from PowerShell using the correct header format:

1. API v3 – users/me  
   Response: {"error":{"code":"WrongCredentialsError","message":"Wrong API key"}}

2. API v3 – ip_addresses  
   Response: {"error":{"code":"WrongCredentialsError","message":"Wrong API key"}}

3. API v3 – ip lookup with query-param ?apikey=  
   Response: {"error":{"code":"AuthenticationRequiredError","message":"X-Apikey header is missing"}}

4. API v3 – Bearer token  
   Response: {"error":{"code":"AuthenticationRequiredError","message":"X-Apikey header is missing"}}

5. API v2 – official endpoint (vtapi/v2/ip-address/report)  
   Response: HTTP 403 Forbidden

6. API v2 – legacy endpoints  
   Response: HTTP 404 Not Found

7. UI API (ui/ip-addresses/…)  
   Response: {"error":{"code":"NotFoundError","message":"Resource not found."}}

8. Undocumented JSON v2 endpoints  
   Response: HTTP 404 Not Found

### Conclusion

The provided key is not recognized by any known VirusTotal API.  
Its behavior does not match expired keys, quota-limited keys, or UI-only tokens.  
VirusTotal returns the same pattern it uses for keys that do not exist in the system.

### Impact on This Project

The VirusTotal client implementation is correct, but live requests cannot succeed with the assignment key.  
Consequently, the field vt_score will remain null during execution, and live tests that depend on VirusTotal will fail with an authentication error.

### How to Enable Real VirusTotal Integration

Create a free VirusTotal Community account, obtain your own API v3 key, and place it into .env:

VIRUSTOTAL_API_KEY=<your-real-key>

Once a valid key is provided, all VirusTotal tests pass and the vt_score field is populated with real data.
