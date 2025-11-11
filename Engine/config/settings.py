# config/settings.py

# Set API_FRAMEWORK to either "fastapi" or "flask"
# Flask not yet implemented. Setting flask will result in NotImplementedError
API_FRAMEWORK = "fastapi"

HOST = "0.0.0.0"
PORT = 8000
RELOAD = True

LOG_LEVEL = "info"