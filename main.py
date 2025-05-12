import uvicorn
import os
from app.api.app import app

# For Vercel serverless functions, we need to expose the app object directly
# The app is already imported from app.api.app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.api.app:app", host="0.0.0.0", port=port, reload=True) 