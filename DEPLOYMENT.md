# Truthify Deployment Guide

Truthify has two parts:

- Frontend dashboard: deploy this to Netlify from the `static` folder.
- Backend detector API: deploy this to Render, Railway, Fly.io, Hugging Face Spaces, or another Python host.

Netlify alone cannot run the full detector because the app uses FastAPI, PyTorch, and a Hugging Face model. Netlify should host the website, while the Python backend runs separately.

## Local Review

```powershell
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

Login:

```text
Username: admin
Password: password
```

## Deploy Backend

1. Push this project to GitHub.
2. Create a new Web Service on Render or Railway.
3. Use Python 3.11.
4. Install command:

```text
pip install -r requirements.txt
```

5. Start command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

6. After deployment, copy the backend URL. It will look like:

```text
https://truthify-api.onrender.com
```

## Deploy Frontend To Netlify

1. Create a new Netlify site from the same GitHub repo.
2. Netlify will use `netlify.toml`.
3. Publish directory should be:

```text
static
```

4. Open the Netlify site.
5. Go to Settings.
6. Paste your deployed backend URL into `Backend API URL`.
7. Click Save Changes.
8. Login with `admin` / `password`.

## Reviewer Flow

1. Open the Netlify website.
2. Login using `admin` / `password`.
3. Upload an image.
4. The selected image preview appears below the upload box.
5. Truthify checks model probability, C2PA-like markers, EXIF/XMP generator tags, and the local perceptual-hash database.
