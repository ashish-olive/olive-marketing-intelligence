# Google Colab Setup Guide

Complete guide for generating data and training ML models in Google Colab.

---

## 📋 Prerequisites

- Google account
- Google Colab access (free)
- GitHub repository created

---

## 🚀 Step-by-Step Instructions

### **Step 1: Open Google Colab**

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Create a new notebook
3. Enable GPU: Runtime → Change runtime type → T4 GPU

### **Step 2: Clone Repository**

```python
# Cell 1: Clone your repository
!git clone https://github.com/YOUR_USERNAME/olive-marketing-intelligence.git
%cd olive-marketing-intelligence
!ls -la
```

### **Step 3: Install Dependencies**

```python
# Cell 2: Install data pipeline dependencies
!pip install -r data-pipeline/requirements.txt

# Cell 3: Install ML dependencies
!pip install -r ml-models/requirements.txt
```

### **Step 4: Generate Data**

```python
# Cell 4: Generate marketing data
!python data-pipeline/scripts/generate_data.py --days 90 --users 500000

# This will take 2-3 minutes
# Output: instance/marketing.db (~1.2 GB)
```

### **Step 5: Train ML Models**

```python
# Cell 5: Train all ML models on GPU
!python ml-models/scripts/train_all.py --use-gpu --epochs 100

# This will take 20-25 minutes on T4 GPU
# Output: ml-models/trained_models/*.pth (4 models)
```

### **Step 6: Package for Download**

```python
# Cell 6: Create deployment package
!python package_for_local.py

# Output: deployment_package.zip (~1.3 GB)
```

### **Step 7: Download Package**

```python
# Cell 7: Download to your computer
from google.colab import files
files.download('deployment_package.zip')
```

---

## 📦 What Gets Generated

### **Database (marketing.db)**
- 4 marketing channels
- 60 campaigns
- 180 creatives
- 5,400 daily performance records
- 500,000 user installs
- 5,000,000 user sessions
- 90 organic metrics
- 12-15 performance signals

### **ML Models**
- `ltv_predictor.pth` - LTV prediction model
- `campaign_forecaster.pth` - Campaign forecasting model
- `churn_predictor.pth` - Churn prediction model
- `budget_optimizer.pth` - Budget optimization model
- `metadata.json` - Model training metrics

---

## ⏱️ Time Estimates

| Task | Time | Notes |
|------|------|-------|
| Setup Colab | 2 min | One-time |
| Install dependencies | 3 min | pip install |
| Generate data | 2-3 min | CPU-bound |
| Train models | 20-25 min | GPU-accelerated |
| Package & download | 2 min | Compression |
| **Total** | **~30 min** | End-to-end |

---

## 🔧 Troubleshooting

### **Out of Memory**
```python
# Reduce dataset size
!python data-pipeline/scripts/generate_data.py --days 60 --users 300000
```

### **GPU Not Available**
```python
# Check GPU
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# If not available, enable in: Runtime → Change runtime type → T4 GPU
```

### **Download Fails**
```python
# Alternative: Save to Google Drive
from google.colab import drive
drive.mount('/content/drive')

!cp deployment_package.zip /content/drive/MyDrive/
print("Saved to Google Drive!")
```

---

## 📊 Monitoring Progress

### **Check Data Generation**
```python
# After step 4
!ls -lh instance/marketing.db
!python -c "from pathlib import Path; print(f'Size: {Path('instance/marketing.db').stat().st_size / (1024**2):.1f} MB')"
```

### **Check Model Training**
```python
# After step 5
!ls -lh ml-models/trained_models/
!cat ml-models/trained_models/metadata.json
```

---

## 🎯 Complete Colab Notebook Template

```python
# ============================================================
# OLIVE MARKETING INTELLIGENCE - COLAB SETUP
# ============================================================

# Cell 1: Setup
!git clone https://github.com/YOUR_USERNAME/olive-marketing-intelligence.git
%cd olive-marketing-intelligence

# Cell 2: Install Dependencies
!pip install -q -r data-pipeline/requirements.txt
!pip install -q -r ml-models/requirements.txt

# Cell 3: Verify GPU
import torch
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")

# Cell 4: Generate Data (2-3 minutes)
!python data-pipeline/scripts/generate_data.py --days 90 --users 500000

# Cell 5: Train Models (20-25 minutes)
!python ml-models/scripts/train_all.py --use-gpu --epochs 100

# Cell 6: Package Everything
!python package_for_local.py

# Cell 7: Download
from google.colab import files
files.download('deployment_package.zip')

print("\n✓ COMPLETE! Download the zip file and extract locally.")
```

---

## 💻 Local Setup (After Download)

### **Extract Package**
```bash
cd ~/Documents/GitHub/Marketing\ Insights/
unzip ~/Downloads/deployment_package.zip

# Move files to correct locations
mv marketing.db instance/
mv trained_models/* ml-models/trained_models/
```

### **Install Local Dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### **Run Application**
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm start
```

### **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

---

## ✅ Verification Checklist

After completing Colab setup:

- [ ] `deployment_package.zip` downloaded (~1.3 GB)
- [ ] Extracted `marketing.db` to `instance/` folder
- [ ] Extracted models to `ml-models/trained_models/`
- [ ] 4 `.pth` files present
- [ ] `metadata.json` present
- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Dashboards show data

---

## 🆘 Need Help?

**Common Issues:**

1. **"No module named 'shared'"**
   - Make sure you're in the project root directory
   - Check `sys.path` includes project root

2. **"Database not found"**
   - Verify `instance/marketing.db` exists
   - Check file size is >1 GB

3. **"Models not loading"**
   - Check `ml-models/trained_models/*.pth` exist
   - App will work with fallback predictions if models missing

---

## 📝 Notes

- Colab sessions timeout after 12 hours
- Save work frequently to Google Drive
- GPU is free but limited to ~12 hours/day
- Data generation is one-time (reuse database)
- Can retrain models anytime

---

**Ready to start? Copy the notebook template above into Colab and run!**
