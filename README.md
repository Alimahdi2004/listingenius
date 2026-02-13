# ListinGenius

AI-Powered Real Estate Marketing - Turn listing photos into scroll-stopping videos in 60 seconds.

## Features

- AI Video Generation (Kling 3.0)
- Smart Descriptions (Claude AI)
- Social Media Posts for 5 platforms
- 3 Video Formats (Vertical, Square, Landscape)

## Deploy to Vercel

1. Push this repo to GitHub
2. Connect to Vercel
3. Add environment variables (see below)
4. Deploy!

## Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `HF_API_KEY` | Higgsfield API key (optional) |
| `HF_API_SECRET` | Higgsfield API secret (optional) |

## Project Structure

```
├── public/
│   ├── index.html      # Landing page
│   ├── app.html        # Main app
│   ├── signup.html     # Sign up
│   └── login.html      # Login
├── api/
│   └── index.py        # Serverless API
├── requirements.txt    # Python deps
└── vercel.json         # Vercel config
```

## Tech Stack

- Frontend: HTML/CSS/JS
- Backend: Python (Vercel Serverless)
- AI: Claude Sonnet, Kling 3.0

## License

MIT
