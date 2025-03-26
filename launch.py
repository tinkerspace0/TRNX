# launch.py

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.api:app",     # Import string path to your FastAPI app
        host="0.0.0.0",     # Accessible on all network interfaces
        port=8000,          # Or any other port you prefer
        reload=True,        # Enable auto-reload (great for development)
        log_level="info"
    )
