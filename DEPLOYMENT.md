# 🚀 Deployment Guide - Vercel + Railway

Complete guide to deploy the Olive Marketing Intelligence platform to production.

---

## 📋 Prerequisites

- ✅ GitHub account with this repo
- ✅ Vercel account (signed up with GitHub)
- ✅ Railway account (signed up with GitHub)
- ✅ Database file: `instance/marketing.db` (1.4GB)

---

## 🎯 Architecture

```
Frontend (Vercel)          Backend (Railway)
┌─────────────────┐       ┌──────────────────┐
│  React App      │──────▶│  Flask API       │
│  Static Files   │       │  ML Models       │
│  your-app       │       │  SQLite DB       │
│  .vercel.app    │       │  your-api        │
└─────────────────┘       │  .railway.app    │
                          └──────────────────┘
```

---

## Part 1: Deploy Backend to Railway

### Step 1: Create New Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **"olive-marketing-intelligence"** repo
5. Railway will auto-detect Python/Flask

### Step 2: Configure Build Settings

Railway should auto-detect, but verify:

- **Build Command:** (auto-detected from `railway.json`)
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
- **Root Directory:** `backend`

### Step 3: Add Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=<generate-random-secret-key>
DATABASE_URL=sqlite:////app/data/marketing.db
CORS_ORIGINS=https://your-app.vercel.app
USE_ML_MODELS=1
```

**To generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Add Persistent Storage

1. In Railway dashboard, click **"+ New"** → **"Volume"**
2. **Mount Path:** `/app/data`
3. **Size:** 2GB (for 1.4GB database + room to grow)
4. Click **"Add"**

### Step 5: Upload Database

**Option A: Via Railway CLI (Recommended)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Upload database
railway run --service=<your-service-name> \
  cp instance/marketing.db /app/data/marketing.db
```

**Option B: Via SFTP/SCP**

Railway provides SFTP access - check docs for current method.

**Option C: Regenerate on Railway**

If upload is difficult, you can regenerate a smaller dataset:
```bash
# SSH into Railway
railway shell

# Run data generation (smaller dataset)
cd data-pipeline
python generate_sample_data.py --users 100000
```

### Step 6: Deploy

1. Click **"Deploy"**
2. Wait ~5-10 minutes for build
3. Railway will provide a URL: `https://your-backend.railway.app`
4. Test: `https://your-backend.railway.app/api/health`

### Step 7: Copy Backend URL

Save your Railway URL - you'll need it for Vercel!

Example: `https://olive-marketing-production.up.railway.app`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Environment Variable

Before deploying, create `.env.production` in `frontend/`:

```bash
cd frontend
echo "REACT_APP_API_URL=https://your-backend.railway.app/api" > .env.production
```

Replace `your-backend.railway.app` with your actual Railway URL!

### Step 2: Commit Environment File

```bash
git add .env.production
git commit -m "Add production environment config"
git push
```

### Step 3: Deploy to Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New"** → **"Project"**
3. Import **"olive-marketing-intelligence"** repo
4. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

### Step 4: Add Environment Variable (Alternative)

If you didn't commit `.env.production`, add in Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add:
   - **Name:** `REACT_APP_API_URL`
   - **Value:** `https://your-backend.railway.app/api`
   - **Environment:** Production

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait ~2-3 minutes
3. Vercel will provide URL: `https://your-app.vercel.app`

### Step 6: Update CORS on Railway

1. Go back to Railway dashboard
2. Update `CORS_ORIGINS` variable:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
3. Railway will auto-redeploy

---

## Part 3: Test Deployment

### Test Backend

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Executive summary
curl https://your-backend.railway.app/api/executive/summary?days=30
```

### Test Frontend

1. Visit `https://your-app.vercel.app`
2. Check all 6 dashboards load
3. Test ML predictions in Modeling tab
4. Verify charts display data

---

## 🔧 Troubleshooting

### Backend Issues

**"Database not found"**
- Check DATABASE_URL path: `/app/data/marketing.db`
- Verify volume is mounted at `/app/data`
- Confirm database was uploaded

**"CORS error"**
- Update CORS_ORIGINS with exact Vercel URL
- Include `https://` prefix
- No trailing slash

**"Module not found"**
- Check all dependencies in `requirements.txt`
- Verify `gunicorn` is included
- Check Railway build logs

### Frontend Issues

**"API calls failing"**
- Verify REACT_APP_API_URL is set correctly
- Check Railway backend is running
- Test backend URL directly in browser

**"Blank page"**
- Check browser console for errors
- Verify build completed successfully
- Check Vercel deployment logs

---

## 💰 Cost Estimate

**Railway Hobby Plan:** $5/month credit
- Database storage (1.5GB): ~$0.38/month
- Compute (light traffic): ~$2-3/month
- **Total: ~$3-4/month** (covered by credit!)

**Vercel Free Tier:** $0/month
- Unlimited bandwidth for personal projects
- Perfect for portfolio/demo

**TOTAL: ~$0-4/month**

---

## 🎉 Success!

Your app is now live at:
- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-backend.railway.app`

Share the frontend URL for demos and interviews!

---

## 📝 Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Vercel project settings
2. Click **"Domains"**
3. Add your domain
4. Update DNS records as instructed
5. Free SSL certificate included!

### Railway Custom Domain

1. Go to Railway project settings
2. Click **"Settings"** → **"Domains"**
3. Add custom domain
4. Update DNS CNAME record

---

## 🔄 Continuous Deployment

Both platforms auto-deploy on git push:

```bash
git add .
git commit -m "Update feature"
git push

# Vercel and Railway will auto-deploy!
```

---

## 📊 Monitoring

**Railway Dashboard:**
- View logs
- Monitor resource usage
- Check deployment status

**Vercel Dashboard:**
- View analytics
- Monitor performance
- Check build logs

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Create an issue in your repo

---

**Happy Deploying! 🚀**
