# Quick Start Guide

Get Olive Marketing Intelligence running locally in minutes.

---

## 🚀 Local Testing (Small Dataset)

### **Option 1: Automated Test Script**

```bash
# Run automated test (generates small dataset and tests backend)
./test_local.sh
```

This will:
- Install dependencies
- Generate test data (7 days, 1000 users)
- Verify database creation
- Test backend API endpoints
- Confirm everything works

**Time: ~2 minutes**

---

### **Option 2: Manual Testing**

#### **Step 1: Install Dependencies**
```bash
cd data-pipeline
pip3 install -r requirements.txt
cd ..
```

#### **Step 2: Generate Test Data**
```bash
# Small dataset for testing
python3 data-pipeline/scripts/generate_data.py --days 7 --users 1000 --campaigns 2
```

**Output:** `instance/marketing.db` (~5-10 MB)

#### **Step 3: Start Backend**
```bash
cd backend
python3 app.py
```

**Backend running at:** http://localhost:5000

#### **Step 4: Test API**
```bash
# In another terminal
curl http://localhost:5000/api/health
curl http://localhost:5000/api/executive/summary?days=7
```

#### **Step 5: Install Frontend Dependencies**
```bash
cd frontend
npm install
```

#### **Step 6: Start Frontend**
```bash
npm start
```

**Frontend running at:** http://localhost:3000

---

## 📊 Full Dataset (Production-Like)

### **Generate Full Data Locally**

```bash
# 90 days, 500K users (takes ~5-10 minutes)
python3 data-pipeline/scripts/generate_data.py --days 90 --users 500000 --campaigns 15
```

**Output:** `instance/marketing.db` (~1.2 GB)

Then start backend and frontend as above.

---

## ☁️ Cloud Workflow (With ML Models)

### **1. Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit: Olive Marketing Intelligence"
git remote add origin https://github.com/YOUR_USERNAME/olive-marketing-intelligence.git
git push -u origin main
```

### **2. Run in Google Colab**

See [COLAB_SETUP.md](COLAB_SETUP.md) for detailed instructions.

**Quick version:**
```python
# In Colab
!git clone https://github.com/YOUR_USERNAME/olive-marketing-intelligence.git
%cd olive-marketing-intelligence

# Install dependencies
!pip install -q -r data-pipeline/requirements.txt

# Generate data (2-3 minutes)
!python data-pipeline/scripts/generate_data.py --days 90 --users 500000

# Package for download
!python package_for_local.py

# Download
from google.colab import files
files.download('deployment_package.zip')
```

### **3. Extract Locally**

```bash
unzip deployment_package.zip
mv marketing.db instance/
```

### **4. Run App**

```bash
# Terminal 1: Backend
cd backend && python3 app.py

# Terminal 2: Frontend
cd frontend && npm start
```

---

## 🔍 Verify Installation

### **Check Database**
```bash
ls -lh instance/marketing.db
```

### **Check Backend**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "channels": 4,
  "timestamp": "2024-..."
}
```

### **Check Frontend**
Open http://localhost:3000 in browser

Should see:
- Executive Dashboard with KPIs
- Charts with data
- Navigation working

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError"**
```bash
# Install dependencies
pip3 install -r data-pipeline/requirements.txt
pip3 install -r backend/requirements.txt
```

### **"Database not found"**
```bash
# Generate data first
python3 data-pipeline/scripts/generate_data.py --days 7 --users 1000
```

### **"Port already in use"**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
export API_PORT=5001
python3 backend/app.py
```

### **Frontend can't connect to backend**
```bash
# Check backend is running
curl http://localhost:5000/api/health

# Check proxy in frontend/package.json
# Should have: "proxy": "http://localhost:5000"
```

---

## 📈 What to Expect

### **Small Test Dataset (7 days, 1000 users)**
- Database: ~5-10 MB
- Generation time: ~10 seconds
- Good for: Testing, development

### **Full Dataset (90 days, 500K users)**
- Database: ~1.2 GB
- Generation time: ~5-10 minutes
- Good for: Demo, production-like testing

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Database generated
- [ ] Backend starts without errors
- [ ] API health check passes
- [ ] Frontend loads successfully
- [ ] Dashboards show data
- [ ] Charts render correctly
- [ ] Navigation works

---

## 🎯 Next Steps

1. **Test locally** with small dataset
2. **Push to GitHub**
3. **Generate full dataset** (locally or Colab)
4. **Explore dashboards**
5. **Customize for your needs**

---

**Need help?** Check [README.md](README.md) for full documentation.
