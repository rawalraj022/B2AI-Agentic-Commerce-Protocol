# Frontend Setup Guide

## One-Command Quick Start

```bash
cd frontend && npm install && npm run dev
```

That's it! The app will be available at `http://localhost:5173`

## Prerequisites

1. **Backend running** on `http://localhost:8000`
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Node.js 16+** installed
   ```bash
   node --version  # should be v16+
   ```

## Step-by-Step Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Open in Browser
Visit `http://localhost:5173`

## Features

- 🎯 **Natural Language Purchases** — Say "Buy Nike shoes for $50"
- 🔄 **Provider Switching** — Toggle OpenAI/Bedrock/Mock LLM
- 📊 **Transaction History** — See all purchases + daily spend
- 🎨 **Dark Theme** — Modern hackathon UI
- 📱 **Fully Responsive** — Works on mobile, tablet, desktop

## Demo Purchases

Try these natural language requests:
- "Buy Nike running shoes for $40"
- "Buy AirPods from Apple for $150"
- "Buy a Kindle from Amazon for $100"

## Troubleshooting

**Q: "Cannot connect to backend"**
A: Make sure backend is running on `localhost:8000`. Check `vite.config.js` proxy settings.

**Q: "Provider selector not working"**
A: Clear localStorage (`Dev Tools → Application → Storage → Clear All`) and reload.

**Q: "No transaction history"**
A: Backend memory must be enabled. Check `MEMORY_ENABLED=true` in backend `.env`.

## For Production Deployment

### Vercel (2 minutes)
1. `git push` to GitHub
2. Connect repo to Vercel
3. Set `VITE_API_URL=https://your-backend-url` in environment
4. Deploy!

### Build Locally
```bash
npm run build
# Output in `dist/` folder
```

## Architecture

```
Frontend (React + Vite)
        ↓ (axios + proxy)
Backend (FastAPI on :8000)
        ↓
Agent Memory + Policy Engine + Settlement
```

No CORS issues — Vite proxy handles it!

## File Structure

```
frontend/
├── src/App.jsx              # Main React component
├── src/services/api.js      # Backend API client
├── src/index.css            # Tailwind CSS
├── vite.config.js          # Dev server + proxy
└── package.json             # Dependencies
```

That's all you need! 🚀