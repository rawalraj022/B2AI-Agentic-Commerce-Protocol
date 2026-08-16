# Fix AWS S3 404 Error - "The specified key does not exist"

This guide helps fix the error: `NoSuchKey - The specified key does not exist. Key: index.html`

## What This Error Means

Your S3 bucket is set up correctly, but **files haven't been uploaded yet** or **they're in the wrong location**.

Error breakdown:
```
Code: NoSuchKey
Message: The specified key does not exist.
Key: index.html
```

Translation: "S3 is looking for `index.html` but can't find it in your bucket"

## Quick Fix (5 Steps)

### Step 1: Verify You Built the Frontend

Check that the build folder has files:

```bash
ls -la frontend/dist/
```

**Should show:**
```
-rw-r--r--   index.html
drwxr-xr-x   assets/
```

**If you see nothing**, rebuild:
```bash
cd frontend
npm install
npm run build
```

### Step 2: Check Files Are In dist/

Specifically check for index.html:

```bash
ls -la frontend/dist/index.html
```

**Should output:**
```
-rw-r--r--  1 user  staff  456 Aug 16 10:40 frontend/dist/index.html
```

**If file doesn't exist**, your build failed. Rebuild:
```bash
cd frontend
npm run build
```

### Step 3: Verify Your Bucket Name

Double-check your bucket exists:

```bash
aws s3 ls
```

**Should show:**
```
2024-08-16 10:20:00 my-b2ai-frontend-demo-123
```

**If your bucket is NOT listed**, go back and create it (AWS_S3_CREATE_BUCKET.md)

### Step 4: Check Files In S3 Bucket

See what's actually in your S3 bucket:

```bash
aws s3 ls s3://my-b2ai-frontend-demo-123/
```

**Expected output if files uploaded:**
```
                           PRE assets/
2024-08-16 10:40:00        456 index.html
```

**If output is empty**, files weren't uploaded. Go to Step 5.

**If you see files but still get 404**, skip to "Advanced Troubleshooting" below.

### Step 5: Upload Files to S3

Upload your build folder to S3:

```bash
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/ --delete
```

**What this does:**
- `sync` = Copy all files from local to S3
- `frontend/dist/` = Your build folder
- `s3://my-b2ai-frontend-demo-123/` = Your bucket
- `--delete` = Remove files from S3 if they're not in dist/

**Expected output:**
```
upload: frontend/dist/index.html to s3://my-b2ai-frontend-demo-123/index.html
upload: frontend/dist/assets/main.js to s3://my-b2ai-frontend-demo-123/assets/main.js
upload: frontend/dist/assets/style.css to s3://my-b2ai-frontend-demo-123/assets/style.css
```

### Step 6: Verify Files Uploaded

Check files in S3 again:

```bash
aws s3 ls s3://my-b2ai-frontend-demo-123/
```

**Should show index.html now:**
```
                           PRE assets/
2024-08-16 10:40:00        456 index.html
```

### Step 7: Clear Browser Cache & Reload

The error might be cached. Do a hard refresh:

**On Mac:**
```
Cmd + Shift + R
```

**On Windows/Linux:**
```
Ctrl + Shift + R
```

Or open the URL in an **incognito/private window**.

## Verify Website Loads

Visit your S3 URL:
```
http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

**Replace:**
- `my-b2ai-frontend-demo-123` = your bucket name
- `us-east-1` = your region

You should now see your B2AI frontend! ✅

## Advanced Troubleshooting

If you still see 404 after these steps:

### Check Website Hosting Is Enabled

```bash
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123
```

**Should show:**
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

**If you get "NoSuchWebsiteConfiguration" error**, website hosting isn't enabled:

```bash
# Re-enable website hosting
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html
```

### Check Bucket Policy Is Set

```bash
aws s3api get-bucket-policy --bucket my-b2ai-frontend-demo-123
```

**Should show a policy with "Effect": "Allow"**

**If you get "NoSuchBucketPolicy" error**, bucket isn't public. Set the policy:

```bash
aws s3api put-bucket-policy --bucket my-b2ai-frontend-demo-123 --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-b2ai-frontend-demo-123/*"
  }]
}'
```

### Check Files Have Correct Content-Type

```bash
aws s3api head-object --bucket my-b2ai-frontend-demo-123 --key index.html
```

**Should show ContentType: text/html**

If ContentType is wrong, re-upload with correct type:

```bash
aws s3 cp frontend/dist/index.html s3://my-b2ai-frontend-demo-123/index.html --content-type text/html
```

### Check Browser Console for Errors

1. Visit your S3 URL
2. Right-click → "Inspect" (or press F12)
3. Click "Console" tab
4. Look for red error messages
5. Report the error

Common errors:
- **CORS error** = Backend API isn't accessible from S3 domain
- **404 for assets** = CSS/JS files didn't upload correctly
- **Blank page** = index.html loaded but React didn't initialize

### Clear CloudFront Cache

If using CloudFront CDN:

```bash
# Find your distribution ID
aws cloudfront list-distributions --query 'DistributionList.Items[0].Id'

# Invalidate cache (replace DISTRIBUTION_ID)
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

## Complete Debug Checklist

Run through these commands:

```bash
# 1. Check local build exists
ls -la frontend/dist/index.html

# 2. Check bucket exists
aws s3 ls | grep my-b2ai-frontend-demo-123

# 3. Check files in S3
aws s3 ls s3://my-b2ai-frontend-demo-123/

# 4. Check website hosting enabled
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123

# 5. Check bucket policy set
aws s3api get-bucket-policy --bucket my-b2ai-frontend-demo-123

# 6. Check file content-type
aws s3api head-object --bucket my-b2ai-frontend-demo-123 --key index.html
```

If any of these fail, follow the fix in Advanced Troubleshooting.

## Still Getting 404?

Try these final steps:

### Force Re-upload Everything

```bash
# Delete all files from S3
aws s3 rm s3://my-b2ai-frontend-demo-123 --recursive

# Wait 10 seconds
sleep 10

# Re-upload everything
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/

# Verify upload
aws s3 ls s3://my-b2ai-frontend-demo-123/
```

### Rebuild and Re-upload

```bash
# Go to frontend folder
cd frontend

# Fresh build
rm -rf dist/
npm run build

# Upload to S3
cd ..
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/ --delete

# Verify
aws s3 ls s3://my-b2ai-frontend-demo-123/
```

### Check AWS Account Limits

Make sure you have:
- S3 bucket creation enabled
- Upload permissions
- Public access enabled

Run:
```bash
aws sts get-caller-identity
```

Shows your AWS Account ID. Contact AWS support if you hit limits.

## Success Indicators

You've fixed it when:

✅ `aws s3 ls s3://your-bucket/` shows `index.html`
✅ `aws s3api get-bucket-website` returns your bucket config
✅ `aws s3api get-bucket-policy` shows Allow policy
✅ Browser visits `http://your-bucket.s3-website-region.amazonaws.com/` successfully
✅ You see your B2AI frontend (not 404)

## Need More Help?

Check these files:
- **AWS_S3_CREATE_BUCKET.md** — Bucket setup
- **AWS_S3_MAKE_PUBLIC.md** — Public access
- **AWS_S3_UPLOAD_FILES.md** — File upload

---

**Your S3 website should now be working!** 🎉

If you're still having issues, the problem is likely:
1. Files not in dist/ folder
2. Files not uploaded to S3
3. Website hosting not enabled
4. Bucket not made public

Re-check those 4 things and you'll fix it! ✅