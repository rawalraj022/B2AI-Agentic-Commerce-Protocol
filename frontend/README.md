# B2AI Agentic Commerce — Frontend

A production-ready React frontend for the B2AI Agentic Commerce Protocol hackathon project.

## Features

✅ **Natural Language Purchase Flow** — Type purchase requests like "Buy Nike shoes for $50"
✅ **Real-Time Transaction Timeline** — Watch intent parsing → policy → authorization → settlement
✅ **Agent Provider Selection** — Switch between OpenAI, AWS Bedrock, or Mock LLM
✅ **Memory & History** — View recent purchases and daily spend tracking
✅ **Responsive Design** — Works on desktop, tablet, mobile
✅ **Dark Theme** — Modern, hackathon-ready UI with Tailwind CSS

## Quick Start

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

### Local Development

Start the Vite dev server (proxies to backend on `http://localhost:8000`):

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

**Ensure backend is running on port 8000:**
```bash
# In another terminal, from project root
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Configuration

The frontend automatically proxies API calls to `http://localhost:8000`. 

**To change the backend URL**, edit `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:8000',  // ← Change here
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

## Usage

### Making a Purchase

1. Type a natural language request: `"Buy Apple AirPods for $150"`
2. Select an agent provider (top-right: OpenAI/Bedrock/Mock)
3. Enter a User ID (for tracking history)
4. Click **Execute**
5. Watch the real-time transaction timeline
6. View your receipt and transaction history

### Provider Selection

- **OpenAI**: Uses GPT-4o-mini (requires `OPENAI_API_KEY` on backend)
- **Bedrock**: Uses AWS Claude via Bedrock (requires AWS credentials on backend)
- **Mock**: Rule-based fallback (always works, no API key needed)

Provider selection is **persisted in localStorage** across sessions.

### Tracking Purchases

All purchases are tracked in **Agent Memory**:
- **Recent Purchases**: Last 5 transactions
- **Daily Spend**: Total spend for today
- **Preferences**: User-learned preferences (expandable)

History is automatically loaded when you change the User ID.

## Build for Production

```bash
npm run build
```

Output files in `dist/` — deploy to any static hosting (Vercel, GitHub Pages, AWS S3, etc.)

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── services/
│   │   └── api.js           # Backend API client
│   ├── index.css            # Global styles
│   └── main.jsx             # Entry point
├── index.html               # HTML template
├── vite.config.js          # Vite config + proxy setup
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
└── package.json             # Dependencies
```

## API Endpoints Used

| Method | Path | Description |
|--------|------|-------------|
| POST | `/supervisor/intent` | Execute purchase via supervisor |
| GET | `/memory/{user_id}/recent` | Get recent transactions |
| GET | `/memory/{user_id}/daily-spend` | Get today's total spend |
| GET | `/directory/merchants/{name}/score` | Get merchant scores |
| GET | `/directory/agents/{id}/trust` | Get agent trust scores |

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running on `http://localhost:8000`
- Check proxy config in `vite.config.js`
- Check browser console for CORS errors

### "No recent transactions showing"
- Make a purchase first
- Ensure backend memory is enabled (`MEMORY_ENABLED=true`)
- Check User ID matches what you're querying

### "Provider not switching"
- Clear browser localStorage: Dev Tools → Application → Storage → Clear All
- Reload the page

## Environment Variables (Optional)

Create a `.env` file if you need to override defaults:

```env
# Backend API URL (only needed if not using proxy)
VITE_API_URL=http://localhost:8000

# Default user ID
VITE_DEFAULT_USER_ID=demo_user
```

Note: The proxy in `vite.config.js` handles this automatically in dev mode.

## Deployment

### Vercel (Recommended for Hackathons)

1. Push to GitHub
2. Connect repo to Vercel
3. Set build command: `npm run build`
4. Set output dir: `dist`
5. Add environment variable: `VITE_API_URL=https://your-backend-url`
6. Deploy!

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### GitHub Pages

```bash
# Update vite.config.js:
export default {
  base: '/repo-name/',  # Your repo name
  // ...rest of config
}

npm run build
git add dist
git commit -m "Deploy"
git push
```

Then enable GitHub Pages in repo settings.

## Tech Stack

- **React 18** — UI framework
- **Vite 5** — Build tool & dev server
- **Tailwind CSS 3** — Styling
- **Axios** — HTTP client
- **PostCSS** — CSS processing

## License

This project is part of the B2AI Agentic Commerce Protocol hackathon submission.

## Support

For issues or questions:
1. Check backend logs: `backend/app/main.py`
2. Check browser console (F12)
3. Ensure backend `.env` has required API keys