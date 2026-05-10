import os
from uvicorn import run

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    host = os.getenv('HOST', '0.0.0.0')

    # Start the FastAPI app from server.py
    # It already mounts React build from frontend/dist if present
    run('server:app', host=host, port=port, reload=False)
