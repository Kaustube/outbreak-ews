# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### Option 1: One-Click Deploy (Easiest)

1. Go to https://vercel.com/
2. Sign in with GitHub
3. Click "Add New Project"
4. Import `Kaustube/outbreak-ews` repository
5. Vercel auto-detects settings
6. Click "Deploy"
7. Done! Get your live URL

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd outbreak-ews
vercel

# Follow prompts - it will deploy automatically
```

## ⚙️ Configuration Files Added

### 1. `vercel.json`
- Configures Vercel build settings
- Routes traffic to dashboard.py
- Python runtime configuration

### 2. `runtime.txt`
- Specifies Python 3.9 (compatible with Vercel)

### 3. `requirements.txt` (Updated)
- Fixed versions for reproducibility
- Removed imdlib/xarray (not needed for dashboard)
- Lighter weight packages

### 4. `.streamlit/config.toml`
- Streamlit server configuration
- Headless mode for cloud deployment
- CORS disabled for Vercel

### 5. `.vercelignore`
- Excludes unnecessary files from deployment
- Keeps deployment size small

## 📦 What Gets Deployed

**Included:**
- ✅ dashboard.py (main app)
- ✅ data/*.csv, data/*.csv.gz (datasets)
- ✅ results/metrics.json (model performance)
- ✅ All Python code files
- ✅ Documentation files

**Excluded:**
- ❌ IMD raw data (too large)
- ❌ Git files
- ❌ Python cache files
- ❌ Test files

## 🎯 Post-Deployment

After deployment, you'll get a URL like:
```
https://outbreak-ews-kaustube.vercel.app
```

**Share this link:**
- In your submission form ✓
- In your presentation ✓
- With your team ✓

## 🔧 Troubleshooting

### If build fails:

**Error: "Module not found"**
- Solution: Check requirements.txt has all dependencies

**Error: "Out of memory"**
- Solution: Data files are small enough (21 MB total)
- If issue persists, remove data/panel.csv.gz temporarily

**Error: "Build timeout"**
- Solution: Vercel free tier has 45s build limit
- Should be fine - our app is lightweight

### If dashboard loads but no data:

Check that these files exist in deployment:
- data/panel.csv.gz
- data/predictions.csv.gz
- data/idsp_parsed.csv
- results/metrics.json

## 🌟 Vercel Benefits

1. **Free hosting** - No cost for hobby projects
2. **Automatic HTTPS** - Secure URLs
3. **Global CDN** - Fast worldwide
4. **Git integration** - Auto-deploys on push
5. **Custom domains** - Add your own domain (optional)

## 📱 Alternative: Streamlit Community Cloud

If Vercel doesn't work, use Streamlit Cloud:

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select: outbreak-ews repository
5. Main file: dashboard.py
6. Click "Deploy"

**Advantage:** Built specifically for Streamlit apps

## 🎓 For Your Submission

**Include in report:**
- Live demo URL: `https://your-app.vercel.app`
- GitHub repo: `https://github.com/Kaustube/outbreak-ews`
- Say: "Deployed on Vercel for live demonstration"

**For presentation:**
- Show live dashboard (not localhost)
- More impressive than local demo
- Accessible from anywhere

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Git repository is up to date
- [ ] All data files are committed
- [ ] requirements.txt is updated
- [ ] vercel.json is configured
- [ ] Dashboard works locally: `streamlit run dashboard.py`

After deploying:
- [ ] Test live URL
- [ ] Check all 5 tabs load
- [ ] Verify data displays correctly
- [ ] Note URL for submission

---

**Your project is now cloud-ready! 🚀**
