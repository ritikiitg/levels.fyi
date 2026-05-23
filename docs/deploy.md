# Deploying this1 (free tier, no card required)

Two services, two free hosts.

## 1. Backend → Render (free Web Service)

1. Push this repo to GitHub.
2. Go to https://dashboard.render.com → **New +** → **Blueprint**.
3. Point it at your repo. Render reads [render.yaml](../render.yaml).
4. Click **Apply**. Render runs the build (`pip install`, `python -m app.seed`, `python -m ml.train`) then `uvicorn`. ~3 minutes.
5. Note the URL (e.g. `https://this1-backend.onrender.com`).

> **Note**: Free instances spin down after ~15 minutes idle. First request after sleep takes ~30s. For the live demo, hit `/api/health` 60s before pitching to wake it.

## 2. Frontend(s) → Vercel (free)

The site and the dashboard deploy as two separate Vercel projects.

### Site
```bash
cd frontend/site
npx vercel deploy --prod
```
- Project name: `this1-site`
- Root directory: `frontend/site`
- Output directory: `dist`
- Edit `vercel.json` and replace `this1-backend.onrender.com` with your actual Render URL.

### Dashboard
```bash
cd frontend/dashboard
npx vercel deploy --prod
```
- Project name: `this1-dashboard`
- Root directory: `frontend/dashboard`
- Same backend URL substitution.

> **WebSocket note**: Vercel rewrites don't proxy WebSockets. The dashboard's live feed connects directly to the Render backend's `/_defender/ws`. Edit `frontend/dashboard/src/api.js` `openLiveFeed` to point to the absolute backend URL if you deploy.

## 3. Sharing the demo

You'll have three links:
- `https://this1-site.vercel.app` — the "Levels.fyi" you're protecting
- `https://this1-dashboard.vercel.app` — the defender control panel
- `https://this1-backend.onrender.com/docs` — Swagger API (judges can try endpoints)

Run the simulator locally pointed at the deployed backend:
```bash
python simulator/attack.py --scenario naive-scraper \
  --target https://this1-backend.onrender.com --duration 30
```

Judges watching the dashboard will see the attack arrive in real time.
