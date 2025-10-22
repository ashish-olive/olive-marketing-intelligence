# Olive Marketing Intelligence Platform

AI-powered marketing analytics with real-time performance signals, ML-driven predictions, and scenario modeling.

## 🚀 Features

### **Performance Signals**
- AI-powered anomaly detection
- Actionable recommendations
- Statistical significance testing
- Priority scoring

### **ML Models (4 Production Models)**
- **LTV Prediction**: Predict 180-day user lifetime value
- **Campaign Forecasting**: 7-day performance predictions
- **Churn Prediction**: Identify at-risk users
- **Budget Optimization**: RL-based allocation recommendations

### **Dashboards**
- **Executive Dashboard**: High-level KPIs and top signals
- **Paid Media Dashboard**: Channel and campaign performance
- **Organic Dashboard**: App store, social, and influencer metrics
- **Attribution Dashboard**: Cross-channel analysis and halo effects
- **Scenario Studio**: ML-powered what-if modeling

### **Data Scale**
- 500K user installs
- 5M user sessions
- 90 days historical data
- 4 marketing channels
- 60 campaigns

---

## 📁 Project Structure

```
olive-marketing-intelligence/
├── shared/                      # Shared infrastructure
│   ├── data_layer/             # Database models & repositories
│   └── utils/                  # Utilities & helpers
├── data-pipeline/              # 🔵 CLOUD: Data generation
│   ├── generators/             # Data generation logic
│   └── scripts/                # CLI scripts
├── ml-models/                  # 🟢 CLOUD: ML training
│   ├── trainers/               # Training scripts
│   ├── models/                 # Model architectures
│   └── trained_models/         # Saved models (gitignored)
├── backend/                    # 💻 LOCAL: Flask API
│   ├── api/                    # API endpoints
│   └── services/               # Business logic
├── frontend/                   # 💻 LOCAL: React app
│   ├── src/pages/              # Dashboard pages
│   └── src/components/         # Reusable components
└── instance/                   # 📦 Database (gitignored)
```

---

## 🔧 Setup

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- Google Colab account (for GPU training)
- Git

---

## 📊 Cloud Workflow (Google Colab)

### **1. Clone Repository in Colab**
```python
!git clone https://github.com/yourusername/olive-marketing-intelligence.git
%cd olive-marketing-intelligence
```

### **2. Install Dependencies**
```python
!pip install -r data-pipeline/requirements.txt
!pip install -r ml-models/requirements.txt
```

### **3. Generate Data**
```python
!python data-pipeline/scripts/generate_data.py --days 90 --users 500000
```
**Output:** `instance/marketing.db` (~1.2 GB)  
**Time:** 2-3 minutes

### **4. Train ML Models**
```python
!python ml-models/scripts/train_all.py --use-gpu --epochs 100
```
**Output:** `ml-models/trained_models/*.pth` (4 models)  
**Time:** 20-25 minutes on T4 GPU

### **5. Package for Download**
```python
!python package_for_local.py
```
**Output:** `deployment_package.zip` (~1.3 GB)

### **6. Download Package**
```python
from google.colab import files
files.download('deployment_package.zip')
```

---

## 💻 Local Workflow (Your Laptop)

### **1. Extract Package**
```bash
unzip deployment_package.zip
mv marketing.db instance/
mv trained_models/* ml-models/trained_models/
```

### **2. Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **3. Install Frontend Dependencies**
```bash
cd frontend
npm install
```

### **4. Run Backend**
```bash
cd backend
python app.py
```
**API:** http://localhost:5000

### **5. Run Frontend**
```bash
cd frontend
npm start
```
**App:** http://localhost:3000

---

## 🎯 API Endpoints

### **Executive**
- `GET /api/executive/summary?days=30`
- `GET /api/executive/trends?days=30`

### **Paid Media**
- `GET /api/paid/channels?days=30`
- `GET /api/paid/campaigns?channel=Meta&days=30`

### **Organic**
- `GET /api/organic/summary?days=30`
- `GET /api/organic/halo-effect?days=30`

### **Signals**
- `GET /api/signals?days=7&severity=all`
- `POST /api/signals/{id}/dismiss`

### **Scenarios**
- `POST /api/scenarios/predict` (ML-powered predictions)

---

## 🤖 ML Models

### **LTV Predictor**
- **Architecture:** 3-layer neural network
- **Input:** 30 features (retention, sessions, geo, device)
- **Output:** Predicted 180-day LTV
- **Training data:** 400K users
- **Accuracy:** RMSE < $2.50

### **Campaign Forecaster**
- **Architecture:** LSTM (2 layers, 128 units)
- **Input:** Historical performance (14 days)
- **Output:** Next 7 days CPI/volume
- **Training data:** 5,400 campaign-days
- **Accuracy:** MAPE < 12%

### **Churn Predictor**
- **Architecture:** XGBoost (GPU-accelerated)
- **Input:** Behavioral features (20+)
- **Output:** Churn probability (7-day window)
- **Training data:** 500K users
- **Accuracy:** AUC-ROC > 0.82

### **Budget Optimizer**
- **Architecture:** Deep Q-Network (DQN)
- **State:** Channel performance, budget, day
- **Action:** Budget allocation
- **Training:** 10K+ simulated episodes
- **Performance:** +8% efficiency vs baseline

---

## 📈 Data Model

### **Key Entities**
- **Channels**: Meta, Google, TikTok, Programmatic
- **Campaigns**: 60 campaigns (15 per channel)
- **Creatives**: 180 creatives (3 per campaign)
- **UserInstalls**: 500K users with full attribution
- **UserSessions**: 5M sessions with engagement metrics
- **Signals**: Pre-calculated insights with actions

### **Golden Events** (Injected for Demo)
1. TikTok creative breakthrough (Day 31)
2. Meta creative fatigue (Day 46)
3. Influencer organic surge (Day 42)
4. Google efficiency drop (Day 68)
5. Budget pacing alert (Day 20)
6. Cross-channel synergy (Day 55)

---

## 🐛 Troubleshooting

### **Database Not Found**
```bash
# Ensure you've extracted deployment_package.zip
ls instance/marketing.db
```

### **Models Not Loading**
```bash
# Check models exist
ls ml-models/trained_models/*.pth
```

### **Port Already in Use**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

---

## 📝 Development Notes

### **Data Generation Time**
- Campaign data: 30 seconds
- User installs (500K): 60 seconds
- User sessions (5M): 90 seconds
- **Total:** ~3 minutes

### **ML Training Time (T4 GPU)**
- LTV Predictor: 3-5 minutes
- Campaign Forecaster: 4-6 minutes
- Churn Predictor: 2-3 minutes
- Budget Optimizer: 8-10 minutes
- **Total:** ~20 minutes

### **Database Size**
- SQLite file: ~1.2 GB
- Compressed: ~400 MB

---

## 🙏 Tech Stack

**Backend:**
- Flask 3.0
- SQLAlchemy 2.0
- PyTorch 2.1 (CPU inference)
- NumPy, Pandas

**Frontend:**
- React 18
- Material-UI v5
- Recharts
- Axios

**ML Training:**
- PyTorch 2.1 (CUDA 11.8)
- XGBoost (GPU)
- Scikit-learn

---

## 📄 License

MIT License

---

## 🚀 Quick Start Summary

**Cloud (Colab):**
```bash
1. Clone repo
2. Generate data (3 min)
3. Train models (20 min)
4. Download package
```

**Local (Laptop):**
```bash
1. Extract package
2. Install dependencies
3. Run backend + frontend
4. Demo ready!
```

**Total Time:** 25-30 minutes for data + models, then instant local deployment.
