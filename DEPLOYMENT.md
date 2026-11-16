# 🚀 Deployment Guide - Streamlit Community Cloud

## ⚠️ Important: Use Streamlit Cloud (NOT Vercel)

Streamlit apps work best on Streamlit Community Cloud (free and built specifically for Streamlit).

---

## 📱 QUICK DEPLOY (5 MINUTES)

### Step 1: Go to Streamlit Cloud
1. Visit: **https://share.streamlit.io/**
2. Click "Sign in" 
3. Choose "Continue with GitHub"
4. Authorize Streamlit to access your repositories

### Step 2: Create New App
1. Click **"New app"** button (top right)
2. Fill in the form:
   - **Repository:** `Kaustube/outbreak-ews`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL (optional):** `outbreak-ews` (or leave default)

3. Click **"Deploy!"**

### Step 3: Wait for Deployment
- Status will show: "Your app is being deployed..."
- Takes 2-3 minutes to install packages and start
- You'll see the dashboard once ready!

### Step 4: Get Your Live URL
Your app will be at:
```
https://outbreak-ews-kaustube.streamlit.app
```
or
```
https://[your-custom-name].streamlit.app
```

**✅ DONE! Share this URL in your submission!**

---

## 🎯 Why Streamlit Cloud?

| Feature | Streamlit Cloud | Vercel | Other Hosts |
|---------|----------------|--------|-------------|
| **Built for Streamlit** | ✅ Perfect | ❌ Doesn't work | ⚠️ Complex setup |
| **Free Forever** | ✅ Yes | ✅ Yes | Varies |
| **Auto-deploys on Git push** | ✅ Yes | ✅ Yes | ⚠️ Manual |
| **Configuration needed** | ✅ None | ❌ Lots | ⚠️ Some |
| **Data files support** | ✅ 1GB limit | ⚠️ 100MB | Varies |

---

## 📦 What Gets Deployed

**Files included in deployment:**
- ✅ `dashboard.py` - Main Streamlit app
- ✅ `data/` folder - All CSV files (panel.csv.gz, predictions.csv.gz, etc.)
- ✅ `results/metrics.json` - Model performance
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `requirements.txt` - Python dependencies

**Total size:** ~21 MB (well within 1GB limit)

---

## 🔧 Configuration Files

### 1. `.streamlit/config.toml` ✅
Already created! This configures:
- App theme (colors, fonts)
- Server settings (headless mode, CORS)
- Browser settings (no usage stats)

### 2. `requirements.txt` ✅
Updated with correct versions:
```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
streamlit>=1.28.0
plotly>=5.18.0
pdfplumber>=0.10.0
```

---

## 🚨 Troubleshooting

### Issue: "App is starting... (taking too long)"

**Cause:** Large dependencies installing

**Solution:** Wait 3-5 minutes on first deploy. Subsequent deploys are faster (cached).

---

### Issue: "ModuleNotFoundError"

**Cause:** Missing package in requirements.txt

**Solution:** 
1. Go to your app on Streamlit Cloud
2. Click "Manage app" → "Reboot"
3. If still fails, check requirements.txt has all packages

---

### Issue: "FileNotFoundError: data/panel.csv.gz"

**Cause:** Data files not in GitHub repository

**Solution:** 
1. Check GitHub has `data/` folder with all CSVs
2. File sizes:
   - panel.csv.gz (18 MB) ✅
   - predictions.csv.gz (2.4 MB) ✅
   - districts.csv, epiclim.csv, idsp_parsed.csv ✅

---

### Issue: "App not loading data"

**Cause:** Path issues in code

**Solution:** All paths in dashboard.py are relative (e.g., `data/panel.csv.gz`) - should work automatically.

---

## 🎓 For Your Submission

### Include in Report:
1. **Live Demo URL:** `https://outbreak-ews-kaustube.streamlit.app`
2. **GitHub Repo:** `https://github.com/Kaustube/outbreak-ews`
3. **Statement:** 
   > "Project deployed on Streamlit Community Cloud for live demonstration. Dashboard accessible at [URL]."

### For Presentation:
- Open the Streamlit Cloud URL (NOT localhost!)
- More impressive - shows it's production-ready
- Accessible from any device with internet
- No setup required for judges/audience

---

## 🔄 Auto-Deploy on Git Push

**Feature:** Streamlit Cloud auto-redeploys when you push to GitHub!

**How it works:**
1. You push code changes to GitHub: `git push origin main`
2. Streamlit Cloud detects the change
3. Automatically rebuilds and redeploys your app
4. URL stays the same - no downtime

**Use case:**
- Fix a bug → Push → Auto-updates live app
- Add a feature → Push → Live in 2 minutes

---

## 📊 App Management

### View Logs:
1. Go to https://share.streamlit.io/
2. Click on your app
3. Click "Manage app" → "Logs"
4. See real-time application logs

### Reboot App:
If app is stuck or not responding:
1. "Manage app" → "Reboot"
2. Takes 30 seconds to restart

### Delete App:
If you need to redeploy fresh:
1. "Manage app" → "Settings" → "Delete app"
2. Redeploy using steps above

---

## 🌟 Alternative Deployment Options

### Option 2: Render.com (Backup)

If Streamlit Cloud doesn't work:

1. Go to **https://render.com/**
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect `Kaustube/outbreak-ews`
5. Settings:
   - **Name:** `outbreak-ews`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Click "Create Web Service"

**URL format:** `https://outbreak-ews.onrender.com`

---

### Option 3: Heroku (If you have Heroku account)

1. Create `Procfile`:
   ```
   web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   heroku create outbreak-ews
   git push heroku main
   ```

---

## ✅ Deployment Checklist

### Before deploying:
- [x] All code committed to GitHub
- [x] Data files (panel.csv.gz, predictions.csv.gz) in repo
- [x] requirements.txt updated
- [x] .streamlit/config.toml created
- [x] Dashboard works locally

### After deploying:
- [ ] Test live URL - does it load?
- [ ] Check all 5 tabs work
- [ ] Verify data displays correctly
- [ ] Test interactive features (sliders, dropdowns)
- [ ] Note URL for submission form

---

## 🎬 Demo Day Checklist

### Before presentation:
- [ ] Open Streamlit Cloud URL in browser
- [ ] Test internet connection
- [ ] Bookmark the URL
- [ ] Have GitHub repo URL ready
- [ ] Close unnecessary tabs

### During presentation:
- [ ] Show live dashboard (not localhost!)
- [ ] Navigate through all 5 tabs
- [ ] Highlight: "Live on Streamlit Cloud - accessible from anywhere"
- [ ] Show GitHub repo
- [ ] Mention: "Auto-deploys on git push"

---

## 💡 Pro Tips

### Tip 1: Pre-load Dashboard Before Demo
Open the URL 5 minutes before presenting. First load can take 30 seconds.

### Tip 2: Have Backup Plan
If internet fails during demo:
- Show screenshots of dashboard tabs
- Walk through code on localhost
- Show results/metrics.json directly

### Tip 3: Custom Domain (Optional)
Streamlit Cloud allows custom domains:
- Settings → Custom domain
- Add your own domain (if you have one)
- Example: `outbreak-ews.yourdomain.com`

---

## 📞 Quick Reference

| What | Link/Command |
|------|--------------|
| **Deploy Site** | https://share.streamlit.io/ |
| **Your GitHub** | https://github.com/Kaustube/outbreak-ews |
| **Main File** | `dashboard.py` |
| **Config** | `.streamlit/config.toml` |
| **Dependencies** | `requirements.txt` |
| **Test Locally** | `streamlit run dashboard.py` |

---

## 🎯 Success Criteria

✅ **Dashboard loads within 3 seconds**
✅ **All 5 tabs are interactive**
✅ **Data displays correctly (no errors)**
✅ **Maps render properly**
✅ **URL is shareable and persistent**

---

**Your app is now cloud-ready! 🚀**

**Deployment time: 5 minutes**
**Cost: FREE forever**
**Maintenance: ZERO (auto-updates)**

Go deploy and get that live URL for tomorrow! 💯


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
