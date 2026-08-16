# Deploy Frontend to AWS S3 (Step-by-Step)

## Overview
This guide shows how to build your React frontend and deploy it to AWS S3 for static hosting.

## Prerequisites

1. **AWS Account** (with access to S3)
2. **AWS CLI** installed locally
3. **Node.js 16+**
4. **Frontend source code** (this repo)

## Step 1: Install AWS CLI

### On macOS (using Homebrew)
```bash
brew install awscli
```

### On Windows (using Chocolatey)
```bash
choco install awscli
```

### On Linux (using pip)
```bash
pip install awscli
```

### Verify Installation
```bash
aws --version
```

## Step 2: Configure AWS Credentials

1. Get your AWS Access Key ID and Secret Access Key from AWS Console
   - Go to: https://console.aws.amazon.com/iam/
   - Click "Users" → Your User → "Security Credentials"
   - Create Access Key if you don't have one

2. Run configuration:
```bash
aws configure
```

3. When prompted, enter:
   - **AWS Access Key ID**: `your-access-key`
   - **AWS Secret Access Key**: `your-secret-key`
   - **Default region**: `us-east-1` (or your preferred region)
   - **Default output format**: `json`

## Step 3: Build the Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with all compiled files.

### Verify Build
```bash
ls -la dist/
# You should see index.html, assets/, etc.
```

## Step 4: Create S3 Bucket

### Option A: Using AWS CLI (Recommended)
```bash
# Create bucket (must be globally unique)
aws s3 mb s3://my-b2ai-frontend-demo-123

# Enable static website hosting
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html
```

### Option B: Using AWS Console
1. Go to: https://s3.console.aws.amazon.com/
2. Click "Create Bucket"
3. Enter bucket name (e.g., `my-b2ai-frontend-demo-123`)
4. Choose region
5. Click "Create"

## Step 5: Configure S3 Bucket for Public Access

### Make Bucket Public
```bash
# Remove block public access
aws s3api put-bucket-public-access-block \
    --bucket my-b2ai-frontend-demo-123 \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

### Set Bucket Policy (Allow Public Read)
```bash
aws s3api put-bucket-policy \
    --bucket my-b2ai-frontend-demo-123 \
    --policy '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "PublicReadGetObject",
          "Effect": "Allow",
          "Principal": "*",
          "Action": "s3:GetObject",
          "Resource": "arn:aws:s3:::my-b2ai-frontend-demo-123/*"
        }
      ]
    }'
```

## Step 6: Upload Files to S3

### Upload All Files from dist/
```bash
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/ \
    --delete \
    --cache-control "public, max-age=3600"
```

### Verify Upload
```bash
aws s3 ls s3://my-b2ai-frontend-demo-123/
# You should see index.html and assets/ folder
```

## Step 7: Get Your URL

```bash
# Get bucket website endpoint
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123
```

Or construct it manually:
```
http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

**Replace `us-east-1` with your region if different.**

## Step 8: Update Backend URL (If Using Custom Backend)

Since your frontend now lives on S3 (different domain), you need to update the backend URL in your frontend.

### Edit `frontend/vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'https://your-backend-url.com',  // ← Update this
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

Then rebuild:
```bash
npm run build
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/ --delete
```

## Step 9: (Optional) Set Up CloudFront CDN

For better performance, use CloudFront:

```bash
aws cloudfront create-distribution \
    --origin-domain-name my-b2ai-frontend-demo-123.s3.amazonaws.com \
    --default-root-object index.html
```

Or use AWS Console: https://console.aws.amazon.com/cloudfront/

## Complete Automation Script

Save as `deploy.sh`:

```bash
#!/bin/bash

BUCKET_NAME="my-b2ai-frontend-demo-123"
REGION="us-east-1"

echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "📤 Uploading to S3..."
aws s3 sync frontend/dist/ s3://$BUCKET_NAME/ --delete --cache-control "public, max-age=3600"

echo "✅ Deployment complete!"
echo "📍 URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com/"
```

Run it:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Troubleshooting

### "Access Denied" Error
- Check AWS credentials: `aws sts get-caller-identity`
- Verify bucket policy is set correctly
- Ensure IAM user has S3 permissions

### "Bucket Already Exists"
- Use a unique bucket name (add your name/date)
- Or use existing bucket: `aws s3 ls`

### "Page Not Found (404)"
- Verify files uploaded: `aws s3 ls s3://your-bucket/`
- Check CloudFront cache if using CDN
- Ensure index.html is at root level

### React Router 404 on Refresh
- S3 doesn't handle client-side routing
- Solution: Redirect all 404s to index.html (already in our setup)

## Cost Estimates

- **S3 Storage**: ~$0.023/GB/month
- **Data Transfer**: ~$0.09/GB (outbound)
- **Requests**: ~$0.0004/1000 requests

For a hackathon demo: **< $1/month**

## Next Steps

1. ✅ Frontend deployed to S3
2. 🔗 Ensure backend is accessible (CORS configured)
3. 📊 Monitor S3 metrics in AWS Console
4. 🚀 Share your S3 URL with judges!

## Clean Up

When done, delete resources to avoid charges:

```bash
# Delete bucket and all contents
aws s3 rb s3://my-b2ai-frontend-demo-123 --force

# Or keep bucket but empty it
aws s3 rm s3://my-b2ai-frontend-demo-123 --recursive
```

That's it! Your frontend is now live on AWS S3! 🎉