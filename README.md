
VIEW IN CODE MODE

AutoPipeline/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── chat.py
│   │   │
│   │   ├── core/
│   │   │   ├── __pycache__/
│   │   │   └── config.py
│   │   │
│   │   ├── data/
│   │   │   ├── processed/
│   │   │   │   └── chroma_db/
│   │   │   └── raw/
│   │   │
│   │   └── services/
│   │       ├── ml_service.py
│   │       └── rag_service.py
│   │
│   ├── .env
│   ├── main.py
│   ├── venv/                 # (ignored by git)
│   └── requirements.txt
│
├── frontend/
│   ├── node_modules/          # (ignored by git)
│   │
│   ├── public/
│   │   └── vite.svg
│   │
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── README.md
│
├── .gitignore
└── README.md
