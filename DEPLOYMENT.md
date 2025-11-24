# Deployment Guide - XIQ to Edge Services Migration Tool

This guide explains how to deploy the XIQ Migration Tool web application to cloud platforms.

## Prerequisites

- Git repository (GitHub, GitLab, or Bitbucket)
- Account on Railway.app or Render.com (both have free tiers)

## Option 1: Deploy to Railway

Railway offers 500 hours/month free tier with $5 credit.

### Steps:

1. **Push your code to GitHub**
   ```bash
   cd /path/to/xiq-edge-migration
   git init
   git add .
   git commit -m "Initial commit - XIQ Migration Tool"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the `railway.toml` and deploy

3. **Configure Environment Variables**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add: `SECRET_KEY` = (generate a random string)
   - Railway will automatically set `PORT`

4. **Access your application**
   - Railway will provide a public URL like: `your-app.up.railway.app`
   - Click "Generate Domain" in the Settings tab

### Railway Configuration Files
- `railway.toml` - Railway-specific configuration
- `Procfile` - Process configuration
- `requirements.txt` - Python dependencies

## Option 2: Deploy to Render

Render offers free tier for web services.

### Steps:

1. **Push your code to GitHub** (same as Railway step 1)

2. **Deploy to Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect Python and use `render.yaml`

3. **Verify Configuration**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web_ui:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Render will auto-generate `SECRET_KEY`

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - You'll get a URL like: `your-app.onrender.com`

### Render Configuration Files
- `render.yaml` - Render-specific configuration
- `requirements.txt` - Python dependencies

## Environment Variables

Both platforms need these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask session secret key | Yes |
| `PORT` | Application port (auto-set by platform) | Auto |
| `FLASK_ENV` | Set to `production` | Auto |

## Security Features

The deployed application includes:

- **XIQ Authentication**: Users must log in with their XIQ credentials
- **Session Management**: Secure session cookies with HTTPOnly and SameSite flags
- **HTTPS**: Both Railway and Render provide free SSL/TLS certificates
- **Login Required**: All API endpoints require authentication

## Post-Deployment

1. **Test the Login**
   - Visit your deployed URL
   - You should see the login page
   - Log in with valid XIQ credentials

2. **Share the URL**
   - Share the public URL with authorized users
   - Users must have valid XIQ credentials to access

3. **Monitor Usage**
   - Railway: Check dashboard for usage metrics
   - Render: Check dashboard for logs and metrics

## Troubleshooting

**Application won't start:**
- Check deployment logs in Railway/Render dashboard
- Verify all dependencies in `requirements.txt` are installed
- Ensure `SECRET_KEY` is set

**Login fails:**
- Verify XIQ credentials are correct
- Check selected region matches your XIQ account
- Check application logs for authentication errors

**502 Bad Gateway:**
- Application might be starting up (wait 30-60 seconds)
- Check logs for startup errors

## Free Tier Limitations

**Railway:**
- 500 hours/month (≈20 days)
- $5 free credit/month
- App sleeps after 30 minutes of inactivity

**Render:**
- Unlimited hours
- App sleeps after 15 minutes of inactivity
- Cold starts take 30-60 seconds

## Costs

Both platforms are **free** for this application under normal usage. You'll only pay if you:
- Exceed free tier limits
- Upgrade to paid plans for better performance
- Keep the app running 24/7 (Render paid tier)

## Support

For deployment issues:
- Railway: https://railway.app/help
- Render: https://render.com/docs

For application issues:
- Check application logs in the platform dashboard
- Review the Migration Logs in the web UI
