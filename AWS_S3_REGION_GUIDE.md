# AWS S3 Regions Guide - ap-southeast-2 Setup

This guide helps you use AWS regions other than `us-east-1`, specifically `ap-southeast-2` (Sydney, Australia).

## What is ap-southeast-2?

- **Region Name:** Asia Pacific (Sydney)
- **Region Code:** `ap-southeast-2`
- **Location:** Sydney, Australia
- **Best For:** Users in Australia, New Zealand, Asia
- **Lower Latency:** If your users are in this region

## Step 1: Configure AWS CLI for ap-southeast-2

When you run `aws configure`, set the region:

```bash
aws configure
```

When prompted:
```
AWS Access Key ID [None]: your-access-key
AWS Secret Access Key [None]: your-secret-key
Default region name [None]: ap-southeast-2
Default output format [None]: json
```

Or set region for a single command:

```bash
aws s3 mb s3://my-b2ai-frontend-demo-123 --region ap-southeast-2
```

## Step 2: Create S3 Bucket in ap-southeast-2

For regions OTHER than `us-east-1`, you need to specify the region:

```bash
aws s3api create-bucket \
    --bucket my-b2ai-frontend-demo-123 \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=ap-southeast-2
```

**Why the extra `--create-bucket-configuration`?**
- `us-east-1` is the default, so it doesn't need this
- Other regions need this to specify where the bucket is located

**Expected output:**
```json
{
    "Location": "http://my-b2ai-frontend-demo-123.s3.ap-southeast-2.amazonaws.com/"
}
```

## Step 3: Enable Website Hosting

Same as before:

```bash
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html
```

## Step 4: Make Bucket Public

Same as before:

```bash
aws s3api put-public-access-block \
    --bucket my-b2ai-frontend-demo-123 \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

Then set the bucket policy:

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

## Step 5: Upload Files

Same as before:

```bash
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/
```

## Step 6: Get Your Website URL

For `ap-southeast-2`, your URL format is:

```
http://my-b2ai-frontend-demo-123.s3-website-ap-southeast-2.amazonaws.com/
```

**NOT** `us-east-1`, but `ap-southeast-2`!

**Parts:**
- `my-b2ai-frontend-demo-123` = Your bucket name
- `ap-southeast-2` = Your region (Sydney)

## Complete Setup for ap-southeast-2

Here's all commands together:

```bash
# Configure AWS CLI
aws configure
# Set region to: ap-southeast-2

# Create bucket in Sydney
aws s3api create-bucket \
    --bucket my-b2ai-frontend-demo-123 \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=ap-southeast-2

# Enable website hosting
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html

# Make public
aws s3api put-public-access-block \
    --bucket my-b2ai-frontend-demo-123 \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# Set bucket policy
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

# Build and upload
cd frontend
npm install
npm run build
cd ..
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-demo-123/

# Visit your site
# http://my-b2ai-frontend-demo-123.s3-website-ap-southeast-2.amazonaws.com/
```

## Common AWS Regions Reference

| Region | Region Code | Location | Website URL Format |
|--------|------------|----------|-------------------|
| US East (N. Virginia) | `us-east-1` | Virginia, USA | `s3-website-us-east-1.amazonaws.com` |
| US West (Oregon) | `us-west-2` | Oregon, USA | `s3-website-us-west-2.amazonaws.com` |
| EU (Ireland) | `eu-west-1` | Ireland | `s3-website-eu-west-1.amazonaws.com` |
| Asia Pacific (Sydney) | `ap-southeast-2` | Sydney, Australia | `s3-website-ap-southeast-2.amazonaws.com` |
| Asia Pacific (Tokyo) | `ap-northeast-1` | Tokyo, Japan | `s3-website-ap-northeast-1.amazonaws.com` |
| Asia Pacific (Singapore) | `ap-southeast-1` | Singapore | `s3-website-ap-southeast-1.amazonaws.com` |

## Key Differences for Non-us-east-1 Regions

### When Creating Bucket

**For us-east-1:**
```bash
aws s3 mb s3://my-bucket
```

**For other regions (like ap-southeast-2):**
```bash
aws s3api create-bucket \
    --bucket my-bucket \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=ap-southeast-2
```

### When Getting Website URL

**For us-east-1:**
```
http://my-bucket.s3-website-us-east-1.amazonaws.com/
```

**For ap-southeast-2:**
```
http://my-bucket.s3-website-ap-southeast-2.amazonaws.com/
```

**Always include the region in the URL!**

## Troubleshooting ap-southeast-2

### "InvalidLocationConstraint"

This means your LocationConstraint doesn't match the region:

```bash
# WRONG - LocationConstraint must match region
aws s3api create-bucket \
    --bucket my-bucket \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=us-east-1  ❌

# RIGHT - LocationConstraint matches region
aws s3api create-bucket \
    --bucket my-bucket \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=ap-southeast-2  ✅
```

### "BucketAlreadyExists"

Bucket names are global. If someone created the name, try:

```bash
aws s3 mb s3://my-b2ai-frontend-rajkumar-sydney --region ap-southeast-2
```

### Website URL not working

Make sure you're using the correct region code:

```bash
# WRONG
http://my-bucket.s3-website-us-east-1.amazonaws.com/  ❌

# RIGHT
http://my-bucket.s3-website-ap-southeast-2.amazonaws.com/  ✅
```

### Latency Issues

If your website is slow:
- Choose a region closer to your users
- Sydney (`ap-southeast-2`) = Good for Australia/NZ
- Singapore (`ap-southeast-1`) = Good for Southeast Asia
- Tokyo (`ap-northeast-1`) = Good for Japan/Korea

## Verify Your Bucket Region

To check what region your bucket is in:

```bash
aws s3api get-bucket-location --bucket my-b2ai-frontend-demo-123
```

**Expected output for Sydney:**
```json
{
    "LocationConstraint": "ap-southeast-2"
}
```

## Switch Regions

To use a different region for future buckets:

```bash
aws configure
# Set Default region name to: ap-southeast-2
```

Or for a single command:

```bash
aws s3 ls --region ap-southeast-2
```

## Cost Comparison

Prices vary slightly by region:

- **us-east-1** (N. Virginia) — Cheapest ($0.023/GB)
- **ap-southeast-2** (Sydney) — Slightly more ($0.025/GB)
- **eu-west-1** (Ireland) — Similar to Sydney

For a hackathon: **< $1 difference per month**

---

**Your B2AI frontend is now ready to deploy in ap-southeast-2 (Sydney)!** 🚀

Use the complete setup commands above, and remember to use the correct region code in all commands!