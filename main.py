"""
FastAPI server for LLM Analysis Quiz Solver
Handles POST requests with quiz URLs and triggers the autonomous agent
"""
import os
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent after environment is loaded
from agent import run_agent

# Global variables
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    print("🚀 Starting LLM Analysis Quiz Solver...")
    print(f"📧 Email: {os.getenv('EMAIL')}")
    print(f"🔑 Secret configured: {'✓' if os.getenv('SECRET') else '✗'}")
    print(f"🤖 Gemini API configured: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
    
    # Create necessary directories
    os.makedirs("LLMFiles", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    yield
    
    print("👋 Shutting down server...")

app = FastAPI(
    title="LLM Analysis Quiz Solver",
    description="Autonomous agent for solving data-related quiz tasks",
    version="1.0.0",
    lifespan=lifespan
)

class QuizRequest(BaseModel):
    """Request model for quiz endpoint"""
    email: str = Field(..., description="Student email ID")
    secret: str = Field(..., description="Student secret string")
    url: str = Field(..., description="Quiz URL to solve")

class QuizResponse(BaseModel):
    """Response model for quiz endpoint"""
    status: str = Field(..., description="Status of the request")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Health status")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "LLM Analysis Quiz Solver",
        "version": "1.0.0",
        "endpoints": {
            "POST /solve": "Submit quiz to solve",
            "GET /healthz": "Health check"
        }
    }

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return HealthResponse(
        status="ok",
        uptime_seconds=uptime
    )

@app.post("/solve", response_model=QuizResponse)
async def solve_quiz(request: Request):
    """
    Main endpoint to receive quiz tasks
    
    Validates secret and triggers autonomous agent in background
    """
    try:
        # Parse JSON body
        try:
            body = await request.json()
        except Exception as e:
            print(f"❌ Invalid JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Validate request model
        try:
            quiz_request = QuizRequest(**body)
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid request format")
        
        # Verify secret
        expected_secret = os.getenv("SECRET")
        if not expected_secret:
            print("❌ SECRET not configured in environment")
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        if quiz_request.secret != expected_secret:
            print(f"❌ Invalid secret received")
            raise HTTPException(status_code=403, detail="Invalid secret")
        
        # Verify email (optional additional validation)
        expected_email = os.getenv("EMAIL")
        if expected_email and quiz_request.email != expected_email:
            print(f"⚠️  Warning: Email mismatch (expected: {expected_email}, got: {quiz_request.email})")
        
        print(f"\n{'='*60}")
        print(f"📨 New quiz request received")
        print(f"📧 Email: {quiz_request.email}")
        print(f"🔗 URL: {quiz_request.url}")
        print(f"{'='*60}\n")
        
        # Start agent in background
        asyncio.create_task(run_agent_background(
            email=quiz_request.email,
            secret=quiz_request.secret,
            url=quiz_request.url
        ))
        
        return QuizResponse(status="ok")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

async def run_agent_background(email: str, secret: str, url: str):
    """Run agent in background to solve quiz chain"""
    try:
        print(f"🤖 Starting autonomous agent...")
        result = await run_agent(email=email, secret=secret, initial_url=url)
        print(f"\n{'='*60}")
        print(f"✅ Agent completed successfully")
        print(f"📊 Final result: {result}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ Agent failed with error:")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors"""
    print(f"❌ Unhandled exception: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Get port from environment or default to 7860
    port = int(os.getenv("PORT", 7860))
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )