# Upload Frontend Files to AWS S3 - Step by Step

This guide walks through building your React frontend and uploading it to your S3 bucket.

## Prerequisites

✅ S3 bucket created
✅ Website hosting enabled
✅ Bucket made public
✅ AWS CLI configured
✅ Your bucket name (e.g., `my-b2ai-frontend-demo-123`)
✅ Frontend source code in `frontend/` folder

## Step 1: Build Your React Frontend

Navigate to your frontend folder and build the project:

```bash
cd frontend
npm install
npm run build
```

**What this does:**
- `npm install` = Installs all dependencies from package.json
- `npm run build` = Creates optimized production build in `dist/` folder

**Expected output:**
```
> vite build

✓ 1234 modules transformed.
dist/index.html                    0.45 kB │ gzip:  0.30 kB
dist/assets/main-abc123.js        45.67 kB │ gzip: 15.23 kB
dist/assets/style-def456.css       5.89 kB │ gzip:  1.23 kB
```

## Step 2: Verify Build Files Exist

Check that `dist/` folder was created with your files:

```bash
ls -la dist/
```

**Expected output:**
```
drwxr-xr-x   3 user  staff     96 Aug 16 10:40 .
drwxr-xr-x  12 user  staff    384 Aug 16 10:39 ..
-rw-r--r--   1 user  staff   456 Aug 16 10:40 index.html
drwxr-xr-x   2 user  staff    128 Aug 16 10:40 assets
```

Perfect! ✅ Your build is ready to upload.

## Step 3: Upload Files to S3

Now upload all files from `dist/` to your S3 bucket:

```bash
aws s3 sync dist/ s3://my-b2ai-frontend-demo-123/
```

**What this does:**
- `aws s3 sync` = Synchronizes files from local folder to S3
- `dist/` = Your local build folder
- `s3://my-b2ai-frontend-demo-123/` = Your S3 bucket

**Replace `my-b2ai-frontend-demo-123` with your bucket name!**

**Expected output:**
```
upload: dist/index.html to s3://my-b2ai-frontend-demo-123/index.html
upload: dist/assets/main-abc123.js to s3://my-b2ai-frontend-demo-123/assets/main-abc123.js
upload: dist/assets/style-def456.css to s3://my-b2ai-frontend-demo-123/assets/style-def456.css
```

## Step 4: Verify Files Were Uploaded

Check that all files are in S3:

```bash
aws s3 ls s3://my-b2ai-frontend-demo-123/
```

**Expected output:**
```
                           PRE assets/
2024-08-16 10:40:00        456 index.html
```

Perfect! ✅ All files are uploaded.

### List Files in assets folder too:

```bash
aws s3 ls s3://my-b2ai-frontend-demo-123/assets/
```

**Expected output:**
```
2024-08-16 10:40:00      45670 main-abc123.js
2024-08-16 10:40:00       5890 style-def456.css
```

Great! ✅ All assets are uploaded.

## Step 5: Access Your Live Website

Get your S3 website URL:

```bash
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123
```

**Expected output:**
```json
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "index.html"
    }
}
```

Your website URL is:
```
http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

**Replace:**
- `my-b2ai-frontend-demo-123` with your bucket name
- `us-east-1` with your region (if different)

### Visit Your Website!

Open the URL in your browser. You should see your B2AI Agentic Commerce frontend! 🎉

## Step 6: Test Your Website

Once the site loads, test:

1. ✅ Type a purchase request: "Buy Nike shoes for $50"
2. ✅ Click Execute button
3. ✅ See the transaction timeline
4. ✅ View the receipt

If everything works, you're done! 🚀

## Summary: Complete Commands

Here's a quick reference for all commands:

```bash
# Step 1: Build frontend
cd frontend
npm install
npm run build

# Step 2: Verify build
ls -la dist/

# Step 3: Upload to S3
aws s3 sync dist/ s3://my-b2ai-frontend-demo-123/

# Step 4: Verify files in S3
aws s3 ls s3://my-b2ai-frontend-demo-123/
aws s3 ls s3://my-b2ai-frontend-demo-123/assets/

# Step 5: Get your URL
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123

# Step 6: Visit your site
# http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

## Updating Your Website

If you make changes to your frontend and want to update the live site:

```bash
# Build again
npm run build

# Upload again (only changed files will be uploaded)
aws s3 sync dist/ s3://my-b2ai-frontend-demo-123/
```

## Troubleshooting

### "Unable to locate credentials"
AWS credentials not configured. Run:
```bash
aws configure
```

### "NoSuchBucket"
Bucket doesn't exist. Check spelling:
```bash
aws s3 ls  # Lists all your buckets
```

### "AccessDenied" when uploading
Your IAM user doesn't have S3 upload permissions. Need AWS admin to grant `s3:PutObject` permission.

### Website shows "404 Not Found"
- Check files were uploaded: `aws s3 ls s3://your-bucket/`
- Wait 30 seconds for CloudFront cache
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### Website shows "Access Denied"
Bucket policy not set correctly. Re-run Step 3 from AWS_S3_MAKE_PUBLIC.md

### Blank page or console errors
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab to see if files loaded
4. Check if backend API is accessible (if using memory/history features)

### React Router 404 on page refresh
This means the error document redirect to index.html is working correctly. The page should still function - just refresh the browser.

## What's Next?

🎉 Your frontend is now live on AWS S3!

### Share Your Site

Your live URL is:
```
http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

You can now:
- 📤 Share URL with judges
- 📹 Record a demo video
- 🔗 Add to GitHub README
- 📊 Monitor traffic in AWS CloudWatch

### Optional: Set Up CloudFront CDN

For faster loading, add CloudFront:

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name my-b2ai-frontend-demo-123.s3.amazonaws.com \
    --default-root-object index.html
```

This gives you a faster, more reliable URL.

### Optional: Set Up Custom Domain

If you have a custom domain (e.g., b2ai-demo.com):
1. Create Route 53 hosted zone
2. Point to S3 bucket endpoint
3. Add HTTPS with ACM certificate

### Monitor Costs

Track your S3 usage:
```bash
# Estimate storage
aws s3api head-bucket --bucket my-b2ai-frontend-demo-123
```

Typical cost for a hackathon demo: **< $1/month**

---

**Your website is now LIVE on AWS S3!** 🚀

