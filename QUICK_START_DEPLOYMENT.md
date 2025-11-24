# Quick Start - Deploy XIQ Migration Tool

Your application is now ready for deployment with XIQ-based authentication!

## What Was Added

### 1. Authentication System
- Login page with XIQ credentials (username, password, region)
- All routes protected with `@login_required` decorator
- Secure session management

### 2. Deployment Files
- `requirements.txt` - Python dependencies (updated with gunicorn)
- `Procfile` - For Railway/Render deployment
- `railway.toml` - Railway-specific configuration
- `render.yaml` - Render-specific configuration
- `.env.example` - Environment variable template
- `.gitignore` - Prevents sensitive files from being committed
- `DEPLOYMENT.md` - Comprehensive deployment guide

### 3. Security Enhancements
- Environment-based SECRET_KEY
- Secure session cookies (HTTPOnly, SameSite)
- Production-ready Flask configuration
- PORT auto-detection from environment

## Deploy in 3 Steps

### Option A: Railway (Recommended)

1. **Create GitHub Repository**
   ```bash
   cd /Users/thomassophieaii/Documents/Claude/migration
   git init
   git add .
   git commit -m "XIQ Migration Tool - Ready for deployment"
   ```

2. **Push to GitHub**
   - Create a new repository on GitHub
   - Run:
   ```bash
   git remote add origin YOUR_GITHUB_URL
   git push -u origin main
   ```

3. **Deploy on Railway**
   - Go to https://railway.app
   - Sign up/login (free)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Click "Deploy"
   - Generate a domain in Settings
   - Done! Your app will be live at: `your-app.up.railway.app`

### Option B: Render

1-2. Same as Railway (create GitHub repo and push)

3. **Deploy on Render**
   - Go to https://render.com
   - Sign up/login (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Click "Create Web Service"
   - Done! Your app will be live at: `your-app.onrender.com`

## Test Your Deployment

1. Visit your deployed URL
2. You'll see the login page
3. Log in with your XIQ credentials (select correct region!)
4. Start migrating!

## Security Notes

- Users must have valid XIQ credentials to access
- Each user logs in with their own XIQ account
- Sessions expire when browser closes
- All API endpoints require authentication

## Free Tier Info

**Railway:**
- 500 hours/month free
- $5 credit/month
- Perfect for occasional use

**Render:**
- Unlimited hours free
- Sleeps after 15 min inactivity
- 30-60 second cold start

Both are completely free for this application!

## Need Help?

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.
