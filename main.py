import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging to monitor activity in the Render dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="East Coast E-Bike Warranty Hub")

# CORS middleware allows your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
html_content = None

@app.on_event("startup")
async def load_html():
    """Load index.html into memory when the server starts for speed."""
    global html_content
    index_path = BASE_DIR / "index.html"
    try:
        html_content = index_path.read_text(encoding="utf-8")
        logger.info("Successfully loaded index.html")
    except FileNotFoundError:
        logger.error(f"index.html not found at {index_path}")
        html_content = "<h1>Warranty Hub</h1><p>Error: index.html not found.</p>"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serves the frontend page you just created."""
    if html_content is None:
        raise HTTPException(status_code=500, detail="HTML content not available")
    return html_content

@app.get("/health")
async def health_check():
    """Used by Render to confirm the app is live."""
    return {"status": "healthy"}

# This model validates the data coming from your web form
class ClaimRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    claim_details: str = Field(default="", max_length=1000)

@app.post("/submit-claim")
async def submit_claim(claim: ClaimRequest):
    """Processes the claim data sent from the website."""
    try:
        # This will show up in your Render logs
        logger.info(f"New warranty claim received for: {claim.customer_name}")
        
        # In the future, you can add code here to save to a database
        
        return {
            "status": "success",
            "message": f"Claim received for {claim.customer_name}",
            "reference_id": "CLM-1001"  # You can automate this ID later
        }
    except Exception as e:
        logger.error(f"Error processing claim: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
                       
