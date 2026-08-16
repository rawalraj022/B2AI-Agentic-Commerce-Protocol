# Create AWS S3 Bucket - Step by Step

This guide walks through creating an S3 bucket and enabling website hosting, one command at a time.

## Prerequisites

✅ AWS CLI installed and working
✅ AWS credentials configured with `aws configure`
✅ Choose a unique bucket name (e.g., `my-b2ai-frontend-demo-123`)

## Step 1: Create the S3 Bucket

Open your terminal and run this command:

```bash
aws s3 mb s3://my-b2ai-frontend-demo-123
```

**What this does:**
- `aws s3 mb` = "make bucket"
- `s3://my-b2ai-frontend-demo-123` = your bucket name (must be globally unique across AWS)

**Expected output:**
```
make_bucket: my-b2ai-frontend-demo-123
```

**If you get an error:**
- "BucketAlreadyExists" → Use a different name (add date/username)
- "InvalidBucketName" → Remove special characters, use only lowercase letters/numbers/-
- "AccessDenied" → Check AWS credentials with `aws sts get-caller-identity`

### Choosing a Unique Bucket Name

Bucket names must be unique globally on AWS. Try these patterns:

```bash
# Option 1: Add your GitHub username
aws s3 mb s3://b2ai-frontend-johndoe-2024

# Option 2: Add a timestamp
aws s3 mb s3://b2ai-frontend-20240816

# Option 3: Add project name
aws s3 mb s3://b2ai-agentic-commerce-demo

# Option 4: Use your name
aws s3 mb s3://rajkumar-b2ai-frontend
```

Pick one that works and continue.

## Step 2: Verify Bucket Was Created

Check that your bucket exists:

```bash
aws s3 ls
```

**Expected output:**
```
2024-08-16 10:20:00 my-b2ai-frontend-demo-123
```

If you see your bucket listed, you're good! ✅

## Step 3: Enable Static Website Hosting

Now tell S3 to host your website. Run this command:

```bash
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html
```

**What this does:**
- Enables website hosting on your bucket
- Sets `index.html` as the default page (when someone visits your domain)
- Redirects 404 errors to `index.html` (important for React Router)

**Replace `my-b2ai-frontend-demo-123` with your actual bucket name!**

**Expected output:**
```
(no output means success!)
```

## Step 4: Verify Website Hosting Is Enabled

Check that website hosting is configured:

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

Perfect! ✅ Your bucket is now configured for website hosting.

## Summary: Complete Commands

Here are all the commands together (copy & paste if you want):

```bash
# Step 1: Create bucket
aws s3 mb s3://my-b2ai-frontend-demo-123

# Step 2: Verify bucket exists
aws s3 ls

# Step 3: Enable website hosting
aws s3 website s3://my-b2ai-frontend-demo-123 \
    --index-document index.html \
    --error-document index.html

# Step 4: Verify website hosting
aws s3api get-bucket-website --bucket my-b2ai-frontend-demo-123
```

## What's Next?

Once your bucket is created and website hosting is enabled:

1. ✅ Bucket created
2. ✅ Website hosting enabled
3. ⏭️ **Next:** Make bucket public (so people can access it)
4. ⏭️ **Next:** Upload your frontend files
5. ⏭️ **Next:** Get your live URL

Continue with the AWS_S3_DEPLOYMENT.md guide at **Step 5: Configure S3 Bucket for Public Access**

## Troubleshooting

### "InvalidBucketName"
Bucket names must follow these rules:
- 3-63 characters long
- Only lowercase letters (a-z), numbers (0-9), and hyphens (-)
- Must start and end with a letter or number
- Cannot contain underscores or dots

### "BucketAlreadyExists"
Someone else already created a bucket with that name. Try:
```bash
# Add your name
aws s3 mb s3://b2ai-frontend-yourname-123

# Add current date
aws s3 mb s3://b2ai-frontend-$(date +%s)
```

### "InvalidLocationConstraint"
If using a region other than us-east-1, specify it:
```bash
aws s3api create-bucket \
    --bucket my-b2ai-frontend-demo-123 \
    --region us-west-2 \
    --create-bucket-configuration LocationConstraint=us-west-2
```

### "AccessDenied"
Your AWS credentials don't have S3 permissions. Check:
```bash
# Verify credentials are configured
aws sts get-caller-identity

# Should show your AWS Account ID and User ARN
```

If you see credentials but still get AccessDenied, your IAM user needs S3 permissions. Contact your AWS admin.

---

**Once you complete these 4 steps, your S3 bucket is ready!** 🎉

Continue with Step 5 in AWS_S3_DEPLOYMENT.md to make it public and upload your files.