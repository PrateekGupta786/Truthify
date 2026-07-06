"""
Hugging Face Spaces compatible app wrapper.
Use this file name for Spaces to recognize it as the main app.
"""
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
