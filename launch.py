# launch.py

from config.settings import API_FRAMEWORK

if __name__ == "__main__":
    if API_FRAMEWORK.lower() == "fastapi":
        # Launch FastAPI adapter
        import uvicorn

        uvicorn.run(
            "api.fastapi_app:app",  # Import string path to your FastAPI app
            host="0.0.0.0",         # Accessible on all network interfaces
            port=8000,              # Or any other port you prefer
            reload=True,            # Enable auto-reload (great for development)
            log_level="info"
        )
    
    elif API_FRAMEWORK.lower() == "flask":
        # from api.flask.app import app
        # app.run(host="0.0.0.0", port=8000, debug=True)
        raise NotImplementedError("Flask API is not implemented as of now.")
    
    else:
        raise ValueError("Unsupported API framework configuration")