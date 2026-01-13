# Vercel Deployment Guide

## Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/new
   - Login with your GitHub account

2. **Import Repository**
   - Click "Import Git Repository"
   - Select `fredwang0216/pg-wechat-saas`
   - Choose branch: `claude/deploy-vercel-e2e-tests-4xKjM`

3. **Configure Project**
   - Vercel will auto-detect `vercel.json` configuration
   - Framework: Vite (already configured)
   - No environment variables needed for basic deployment

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Copy the deployment URL (e.g., `https://pg-wechat-saas.vercel.app`)

## Option 2: Deploy via Vercel CLI (Advanced)

### Step 1: Get a Valid Token

1. Go to: https://vercel.com/account/tokens
2. Click "Create Token"
3. Name it: "CLI Deployment"
4. Scope: Full Account (or specific project)
5. Copy the token (format: `vercel_xxxxxxxxxxxxxxxx` or similar long string)

### Step 2: Deploy Using Token

```bash
vercel deploy --token=YOUR_ACTUAL_TOKEN --yes --prod
```

## Option 3: If Already Deployed

If this project is already deployed on Vercel:

1. Check your Vercel dashboard: https://vercel.com/dashboard
2. Find the project
3. Get the deployment URL
4. Run E2E tests directly (see below)

## Running End-to-End Tests

Once deployed, run the comprehensive test suite:

```bash
python3 test_e2e_vercel.py https://your-deployment-url.vercel.app
```

This will test:
- ✅ `/api/health` - Health check endpoint
- ✅ `/api/date` - Canary endpoint
- ✅ `/api/test_health` - Test health endpoint
- ✅ `/api/generate` - Generate endpoint

## Troubleshooting

### Invalid Token Error
- Tokens must be generated from https://vercel.com/account/tokens
- Tokens are long alphanumeric strings (50+ characters)
- Tokens expire - create a new one if needed

### Deployment Fails
- Check `vercel.json` configuration
- Ensure `api/requirements.txt` lists all dependencies
- Check Vercel dashboard for build logs

### Tests Fail
- Ensure deployment is complete (check Vercel dashboard)
- Verify the URL is accessible in a browser
- Check API endpoint paths match the configuration
