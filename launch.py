# launch.py

# from config.settings import API_FRAMEWORK, RELOAD, LOG_LEVEL, HOST, PORT
from gui.app import main


if __name__ == "__main__":
    main()
# if __name__ == "__main__":
    # if API_FRAMEWORK.lower() == "fastapi":
    #     # Launch FastAPI adapter
    #     import uvicorn

    #     uvicorn.run(
    #         "api.fastapi.app:app",  # Import string path to your FastAPI app
    #         host=HOST,              # Accessible on all network interfaces
    #         port=PORT,              # port you prefer
    #         reload=RELOAD,          # Enable auto-reload (great for development)
    #         log_level=LOG_LEVEL
    #     )
    
    # elif API_FRAMEWORK.lower() == "flask":
    #     # from api.flask.app import app
    #     # app.run(host=HOST, port=PORT, debug=True)
    #     raise NotImplementedError("Flask API is not implemented as of now.")
    
    # else:
    #     raise ValueError("Unsupported API framework configuration")