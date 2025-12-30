# 🌍 CirculoMetrix AI

## Intelligent LCA & Circularity Analysis Platform for Metals

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

CirculoMetrix AI is a comprehensive platform for Life Cycle Assessment (LCA) and circular economy analysis of metals. It combines advanced AI/ML models with industry-standard LCA methodologies to help manufacturers, sustainability consultants, and researchers optimize their material flows and reduce environmental impact.

---

## ✨ Key Features

### 🔬 **LCA Analysis**
- Complete cradle-to-grave carbon footprint calculation
- Multi-stage environmental impact assessment (mining, processing, manufacturing, transport, EOL)
- ISO 14040/14044 compliant methodology
- Real-time emissions tracking with breakdown by lifecycle stage

### ♻️ **Circularity Metrics**
- Material Circularity Indicator (MCI) calculation
- Recycled content analysis
- End-of-life recovery potential
- Circular economy scoring based on Ellen MacArthur Foundation framework

### 🤖 **AI-Powered Insights**
- Predictive modeling for emissions and circularity scores
- Hotspot detection using clustering algorithms
- SHAP-based explainability for model predictions
- Anomaly detection in material flows

### 📊 **Advanced Visualizations**
- Interactive Sankey diagrams for material and energy flows
- Geospatial mapping of supply chain impacts
- Comparative analysis across metals and scenarios
- Real-time dashboard with KPI tracking

### 🎯 **What-If Scenarios**
- Simulate different recycling rates
- Compare virgin vs recycled material impacts
- Transport mode optimization
- Process efficiency improvements

### 📄 **Automated Reporting**
- PDF report generation with charts and metrics
- Compliance-ready documentation
- Customizable report templates
- Export to CSV/JSON for further analysis

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React.js)    │
└────────┬────────┘
         │
    ┌────▼────┐
    │   API   │
    │ Gateway │
    └────┬────┘
         │
┌────────▼──────────┐
│  FastAPI Backend  │
├───────────────────┤
│ • LCA Engine      │
│ • AI/ML Models    │
│ • Circularity Calc│
│ • PDF Generator   │
└────────┬──────────┘
         │
    ┌────▼────┐
    │Database │
    │(MongoDB)│
    └─────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts, Plotly.js
- **Diagrams**: D3.js for Sankey
- **Maps**: Leaflet
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB Atlas
- **ML**: Scikit-learn, XGBoost
- **Explainability**: SHAP
- **PDF**: ReportLab
- **Validation**: Pydantic

### ML Pipeline
- **Training**: Jupyter Notebooks
- **Models**: Random Forest, XGBoost
- **Features**: 25+ engineered features
- **Preprocessing**: StandardScaler, imputation

### DevOps
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **Deployment**: Render, Vercel
- **CI/CD**: GitHub Actions ready

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker (optional)

### Installation

#### Option 1: Local Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

#### Option 2: Docker
```bash
docker-compose up --build
```

Access the application:
- Frontend: [Link](https://circulometrix-ai.vercel.app)
- Backend API: [Link](https://circulometrix-ai.onrender.com)
- API Docs: [Link](https://circulometrix-ai.onrender.com/docs)

---

## 📖 API Documentation

### Main Endpoints

#### LCA Analysis
```http
POST /api/lca/calculate
Content-Type: application/json

{
  "metal_type": "aluminium",
  "mass_kg": 1000,
  "recycled_content": 30,
  "transport_distance_km": 500,
  "manufacturing_process": "extrusion"
}
```

#### Circularity Score
```http
POST /api/circularity/calculate
Content-Type: application/json

{
  "metal_type": "copper",
  "virgin_material": 700,
  "recycled_material": 300,
  "utility_factor": 0.8,
  "recovery_rate": 0.75
}
```

#### AI Predictions
```http
POST /api/ai/predict
Content-Type: application/json

{
  "features": {
    "mass_kg": 1000,
    "recycled_content": 30,
    "transport_distance_km": 500,
    ...
  }
}
```

#### Generate Report
```http
POST /api/report/generate
Content-Type: application/json

{
  "project_name": "Aluminum Can Manufacturing",
  "lca_results": {...},
  "circularity_results": {...}
}
```

Full API documentation: [Link](https://circulometrix-ai.onrender.com/docs)

---

## 📊 Sample Use Cases

### 1. **Automotive Manufacturer**
Compare the environmental impact of using virgin vs recycled aluminum for car body panels.

### 2. **Electronics Producer**
Assess copper supply chain circularity and identify hotspots for improvement.

### 3. **Construction Company**
Evaluate steel rebar lifecycle emissions and optimize end-of-life recovery.

### 4. **Sustainability Consultant**
Generate compliance-ready LCA reports for client projects with automated calculations.

---

## 📁 Project Structure

```
circulometrix-ai/
├── frontend/          # React application
├── backend/           # FastAPI backend
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic
│   ├── models/        # Database models
│   ├── ml_models/     # Trained ML models
│  └── datasets/      # Reference data
```

---

## 🔬 LCA Methodology

CirculoMetrix follows **ISO 14040/14044** standards:

1. **Goal & Scope Definition**: System boundaries, functional unit
2. **Inventory Analysis**: Data collection for all lifecycle stages
3. **Impact Assessment**: GWP (CO2eq), energy use, water consumption
4. **Interpretation**: Hotspot analysis, recommendations

### Lifecycle Stages Covered:
- ⛏️ Mining & extraction
- 🏭 Material processing
- 🔧 Manufacturing
- 🚚 Transportation
- ♻️ End-of-life (recycling/landfill)

---

## 🎓 Circularity Metrics

### Material Circularity Indicator (MCI)
Based on Ellen MacArthur Foundation methodology:

```
MCI = 1 - (LFI × F(X,V)) - WFI/W
```

Where:
- **LFI**: Linear Flow Index
- **F(X,V)**: Utility factor
- **WFI**: Waste Flow Index
- **X/V**: Lifetime ratio

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **CirculoMetrix Team** - *Initial work*

---

## 🙏 Acknowledgments

- ISO 14040/14044 LCA standards
- Ellen MacArthur Foundation circularity framework
- European Commission PEF methodology
- Ecoinvent database for emission factors

---

## 📧 Contact

- **Email**: www.squadsyntax72@gmail.com

---

## 🗺️ Roadmap

- [ ] Support for additional metals (titanium, lithium)
- [ ] Integration with Ecoinvent API
- [ ] Blockchain traceability for material flows
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Real-time IoT sensor integration

---

**⭐ Star this repo if you find it useful!**
