import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv()

# Add the 'api' directory to the path so internal imports work (Vercel style)
api_path = os.path.join(os.path.dirname(__file__), "api")
if api_path not in sys.path:
    sys.path.append(api_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Enterprise AI Inbox Simulator Backend on http://localhost:{port}")
    # Use the 'index' entry point after setting up path
    uvicorn.run("index:app", host="0.0.0.0", port=port, reload=True)
