# AutoML RAG

## Project Title

**AutoML RAG** - An intelligent data analysis platform that combines Automated Machine Learning (AutoML) with Retrieval Augmented Generation (RAG) to provide AI-powered insights and natural language interactions with your datasets.

## Overview

AutoML RAG is an end-to-end platform designed to automate the machine learning pipeline while providing a conversational interface for data analysis. The system seamlessly integrates:

- **Automated Machine Learning**: Automatically detects problem types, selects optimal models, and performs model training
- **Retrieval Augmented Generation**: Indexes datasets for semantic search and enhances responses with contextual data
- **Interactive Chat Interface**: Natural language interaction for exploring datasets and generating insights
- **Data Processing Pipeline**: Automatic preprocessing, feature engineering, and target detection

This platform democratizes ML by requiring minimal technical knowledge from users while maintaining flexibility for advanced users.

## Problem Statement

Businesses and researchers struggle with:
1. **Time-consuming ML pipelines** - Manual model selection and hyperparameter tuning is tedious and error-prone
2. **Data exploration bottlenecks** - Understanding large datasets requires technical expertise and multiple tools
3. **Lack of interpretability** - Black-box ML models don't provide actionable insights
4. **Integration complexity** - Combining ML with generative AI requires significant engineering effort

AutoML RAG addresses these challenges by automating the ML workflow and adding a natural language layer for intuitive data exploration.

## Motivation

The motivation behind AutoML RAG is to:
- **Lower barriers to entry** for non-technical users to leverage machine learning
- **Accelerate ML development cycles** through automation
- **Enhance decision-making** with AI-assisted analysis and insights
- **Reduce human error** in model selection and data preprocessing
- **Provide transparency** through conversational explanations of ML results

## Features

- ✅ **Automatic Problem Detection**: Identifies regression, classification, or time-series problems
- ✅ **Intelligent Model Selection**: Automatically selects optimal models based on data characteristics
- ✅ **Data Preprocessing**: Handles missing values, scaling, encoding, and feature engineering
- ✅ **Target Variable Detection**: Automatically identifies target columns for prediction tasks
- ✅ **Dataset Indexing**: Creates semantic indices for fast retrieval and RAG integration
- ✅ **Conversational Interface**: Chat-based interaction for data exploration and insights
- ✅ **Real-time Progress Tracking**: Background task monitoring for long-running analyses
- ✅ **REST API**: Complete API endpoints for programmatic access
- ✅ **Responsive UI**: Modern React-based frontend with Tailwind CSS

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Chat UI    │  │ Upload Files │  │ View Results │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────┬────────────────────────────────────────────────────────┘
         │ HTTP (CORS)
┌────────▼────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    API Router (v1)                         │ │
│  │  • POST /upload          • POST /analyze                   │ │
│  │  • GET  /datasets        • POST /chat                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Service Layer                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │ ML Service   │  │ RAG Service  │  │ Data Service │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │ Preprocessing│  │  Problem     │  │ Target       │     │ │
│  │  │              │  │  Detection   │  │  Matching    │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Data Layer                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │ Raw Data     │  │ Processed    │  │ ChromaDB     │     │ │
│  │  │ Storage      │  │ Data Storage │  │ Vector Store │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Project Workflow

### 1. **Data Upload**
   - User uploads CSV/data file via frontend
   - Backend generates unique dataset ID
   - File stored in raw data directory

### 2. **Data Processing**
   - Preprocessing service cleans and normalizes data
   - Target variable detection identifies prediction target
   - Feature engineering and scaling applied

### 3. **Problem Detection**
   - Analyzes data characteristics
   - Determines problem type (classification/regression/time-series)
   - Selects appropriate models

### 4. **Model Training** (Background)
   - Runs ML service on processed data
   - Performs hyperparameter tuning
   - Evaluates multiple model candidates
   - Selects best performing model

### 5. **RAG Indexing** (Background)
   - Creates semantic embeddings of dataset
   - Stores in ChromaDB vector database
   - Enables semantic search and retrieval

### 6. **Chat & Analysis**
   - User asks questions about data
   - RAG retrieves relevant context
   - LLM generates natural language responses
   - Results displayed in chat interface

## Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **ML Pipeline**: scikit-learn, pandas, numpy
- **Vector Database**: ChromaDB (with FAISS)
- **LLM Integration**: Google Generative AI
- **Task Queue**: Celery with Redis/RabbitMQ
- **Database**: SQLite (ChromaDB)
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Icons**: Lucide React

### Infrastructure
- **Python**: 3.10+
- **Node.js**: 16+
- **CORS**: Enabled for cross-origin requests

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- Git
- Virtual Environment tool (venv or conda)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Google Generative AI
GOOGLE_API_KEY=your_google_api_key_here

# Database
DATABASE_URL=sqlite:///./data/processed/chroma.db

# RAG Configuration
CHROMA_DB_PATH=./data/processed/chroma_db

# Model Configuration
MODEL_TIMEOUT=300
MAX_WORKERS=4

# Celery Configuration (optional)
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

## Usage

### Start Backend Server

```bash
cd backend

# Activate virtual environment (if not already active)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend

# Start the Vite development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Build Frontend for Production

```bash
cd frontend

# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Currently, the API is open (no authentication required). For production, implement API keys or JWT tokens.

### Endpoints

#### Dataset Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload a new dataset for analysis |
| GET | `/datasets` | List all uploaded datasets |
| GET | `/datasets/{dataset_id}` | Get details of a specific dataset |
| DELETE | `/datasets/{dataset_id}` | Delete a dataset |

#### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Start automated analysis on a dataset |
| GET | `/analysis/{dataset_id}` | Get analysis status and results |
| GET | `/models/{dataset_id}` | Get trained models info |

#### Chat & RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send chat message for dataset analysis |
| GET | `/chat/history/{dataset_id}` | Get chat history |

### Example Requests

**Upload Dataset:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@data.csv" \
  -F "dataset_name=My Dataset"
```

**Start Analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "dataset_uuid"}'
```

**Chat Message:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_uuid",
    "message": "What are the key insights from this data?",
    "conversation_id": "conv_uuid"
  }'
```

## Folder Structure

```
AutoML_RAG/
│
├── README.md                          # This file
├── requirements.txt                   # Python dependencies (root level)
│
├── backend/                           # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── chat.py            # Chat/RAG endpoints
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py              # Configuration and settings
│   │   │
│   │   ├── data/
│   │   │   ├── raw/                   # Original uploaded CSV files
│   │   │   └── processed/
│   │   │       └── chroma_db/         # ChromaDB vector store
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── data_analysis.py       # Analysis utilities
│   │       ├── ml_service.py          # ML pipeline orchestration
│   │       ├── model_runner.py        # Model execution
│   │       ├── model_selection.py     # Automated model selection
│   │       ├── preprocessing.py       # Data preprocessing
│   │       ├── problem_detection.py   # Detect regression/classification
│   │       ├── rag_service.py         # RAG indexing and retrieval
│   │       └── target_detection.py    # Target variable detection
│   │
│   ├── .env                           # Environment variables (create this)
│   ├── .gitignore
│   ├── requirements.txt               # Python package dependencies
│   └── venv/                          # Virtual environment (ignored)
│
├── frontend/                          # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalysisView.jsx       # Dataset analysis display
│   │   │   ├── ChatInterface.jsx      # Chat UI component
│   │   │   ├── DatasetCard.jsx        # Dataset card component
│   │   │   ├── FileUpload.jsx         # File upload component
│   │   │   ├── Header.jsx             # App header
│   │   │   └── NavLink.jsx            # Navigation links
│   │   │
│   │   ├── services/
│   │   │   └── api.js                 # API client
│   │   │
│   │   ├── App.jsx                    # Main app component
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Global styles
│   │
│   ├── public/                        # Static assets
│   │
│   ├── index.html                     # HTML template
│   ├── package.json                   # npm dependencies
│   ├── vite.config.js                 # Vite configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js              # PostCSS config
│   ├── eslint.config.js               # ESLint configuration
│   └── node_modules/                  # npm packages (ignored)
│
└── .gitignore                         # Git ignore rules
```

### Directory Descriptions

| Directory | Purpose |
|-----------|---------|
| `backend/app/api/` | API route handlers and endpoints |
| `backend/app/core/` | Core configuration and constants |
| `backend/app/data/raw/` | Stores uploaded CSV files |
| `backend/app/data/processed/` | Stores processed data and vector embeddings |
| `backend/app/services/` | Business logic and ML pipeline |
| `frontend/src/components/` | React UI components |
| `frontend/src/services/` | API integration layer |

## Configuration

### Backend Configuration (`backend/app/core/config.py`)

Key configuration settings:

```python
# API Settings
API_TITLE = "AutoML RAG API"
API_VERSION = "v1"
DEBUG = True  # Set to False in production

# File Upload
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.json'}

# ML Settings
TEST_SIZE = 0.2
RANDOM_STATE = 42
CROSS_VALIDATE_FOLDS = 5

# RAG Settings
EMBEDDING_MODEL = "embedding-001"
CHROMA_COLLECTION_NAME = "datasets"
TOP_K_RETRIEVAL = 5

# LLM Settings
LLM_MODEL = "gemini-pro"
LLM_TEMPERATURE = 0.7
```

### Frontend Configuration (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Data Flow Configuration

**Data Processing Pipeline** (in `backend/app/services/preprocessing.py`):
- Handle missing values (mean imputation for numeric, mode for categorical)
- Normalize numeric features
- Encode categorical variables
- Detect and handle outliers

**Model Selection** (in `backend/app/services/model_selection.py`):
- Classification: LogisticRegression, RandomForest, SVM, GradientBoosting
- Regression: LinearRegression, RandomForest, SVR, GradientBoosting
- Cross-validation for robust evaluation

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Style

```bash
cd backend
black .
flake8 .
```

### Frontend Linting

```bash
cd frontend
npm run lint
```

## Deployment

### Backend Deployment

```bash
# Build for production
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend Deployment

```bash
# Build optimized bundle
npm run build

# Deploy dist/ folder to static hosting (Netlify, Vercel, etc.)
```

## Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python version is 3.10+
- Verify all dependencies: `pip install -r requirements.txt`
- Check `.env` file exists

**Frontend shows API errors:**
- Verify backend is running on `http://localhost:8000`
- Check CORS is enabled in `backend/app/main.py`
- Verify `VITE_API_BASE_URL` in frontend `.env`

**RAG indexing takes too long:**
- Large datasets (>100MB) require more time
- Check system resources (RAM, CPU)
- Consider batch processing for very large datasets

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request with descriptions

## License

This project is provided as-is for educational and research purposes.

## support

For questions or issues, please check existing documentation or create an issue in the repository.
│   ├── vite.config.js
│   └── README.md
│
├── .gitignore
└── README.md