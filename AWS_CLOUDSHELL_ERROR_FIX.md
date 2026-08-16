# Fix AWS CloudShell Permission Error

This guide fixes the error: `User is not authorized to perform: cloudshell:CreateEnvironment`

## What This Error Means

```
Unable to create the environment. This may be due to insufficient permissions 
to create environments, or because the environment no longer exists. To use 
CloudShell terminal, choose Open ap-southeast-2 or Create VPC environment.
```

Translation: "Your AWS account doesn't have permission to use CloudShell in ap-southeast-2"

This is an **organizational policy restriction**, not a personal permission issue.

## Why This Happens

Your AWS organization has a **Service Control Policy (SCP)** that explicitly denies CloudShell access:

```
service_control_policy: arn:aws:organizations::752388617102:policy/o-rtsonwc1v9/service_control_policy
```

This is a **security policy at the organization level** that your team admin set up.

## Solutions

### Solution 1: Use Local Terminal Instead (Recommended for Hackathons)

**You don't actually need CloudShell!** Use your local computer's terminal instead:

```bash
# On your Mac/Linux/Windows terminal (NOT in AWS console)

# Configure AWS CLI locally
aws configure
# Enter your credentials

# Create bucket in ap-southeast-2
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

# Set policy
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
```

This works perfectly and **doesn't require CloudShell at all!**

### Solution 2: Ask AWS Account Admin

If you need CloudShell, contact your team's AWS administrator:

**Message to send:**
```
Hi, I need CloudShell access in ap-southeast-2 for the hackathon.
My user: arn:aws:sts::676787762767:assumed-role/AWSReservedSSO_AdministratorAccess_24ebab67f6872000/team-27-user

Can you modify the SCP to allow cloudshell:CreateEnvironment for my user?
```

Your admin can then modify the Service Control Policy.

### Solution 3: Use a Different Region

If CloudShell is blocked in ap-southeast-2, try us-east-1:

```bash
# In AWS CloudShell (us-east-1)
aws s3 mb s3://my-b2ai-frontend-demo-123
aws s3 website s3://my-b2ai-frontend-demo-123 --index-document index.html --error-document index.html
# etc...
```

Then your website URL will be:
```
http://my-b2ai-frontend-demo-123.s3-website-us-east-1.amazonaws.com/
```

## Recommended Approach for Hackathon

**Use local terminal on your computer:**

1. Install AWS CLI locally (if not already installed)
2. Configure with `aws configure`
3. Run all S3 commands from your computer
4. Build and upload from your computer

**Advantages:**
- No permission issues
- Faster uploads
- Works offline
- Same commands work anywhere

## Step-by-Step Local Setup

### 1. Install AWS CLI

**On Mac (using Homebrew):**
```bash
brew install awscli
```

**On Windows (using Chocolatey):**
```bash
choco install awscli
```

**On Linux:**
```bash
sudo apt-get install awscli
```

### 2. Configure Credentials

```bash
aws configure
```

Enter:
```
AWS Access Key ID [None]: AKIAZ3E5RWZHUF5B4EXC
AWS Secret Access Key [None]: (ask your team lead)
Default region name [None]: ap-southeast-2
Default output format [None]: json
```

**Note:** Use NEW credentials that your team provided, not the old ones shared in chat!

### 3. Verify AWS CLI Works

```bash
aws sts get-caller-identity
```

Should show your account info:
```json
{
    "UserId": "AIDA...",
    "Account": "676787762767",
    "Arn": "arn:aws:iam::676787762767:user/..."
}
```

### 4. Deploy Frontend

From your project directory:

```bash
# Build
cd frontend
npm install
npm run build
cd ..

# Create bucket
aws s3api create-bucket \
    --bucket my-b2ai-frontend-rajkumar \
    --region ap-southeast-2 \
    --create-bucket-configuration LocationConstraint=ap-southeast-2

# Enable website hosting
aws s3 website s3://my-b2ai-frontend-rajkumar \
    --index-document index.html \
    --error-document index.html

# Make public
aws s3api put-public-access-block \
    --bucket my-b2ai-frontend-rajkumar \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# Set policy
aws s3api put-bucket-policy --bucket my-b2ai-frontend-rajkumar --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-b2ai-frontend-rajkumar/*"
  }]
}'

# Upload files
aws s3 sync frontend/dist/ s3://my-b2ai-frontend-rajkumar/

# Verify
aws s3 ls s3://my-b2ai-frontend-rajkumar/

# Visit
# http://my-b2ai-frontend-rajkumar.s3-website-ap-southeast-2.amazonaws.com/
```

## Troubleshooting Local AWS CLI

### "Unable to locate credentials"

Credentials not configured:

```bash
aws configure
# Enter your access key and secret key
```

Or check your credentials file:

```bash
# Mac/Linux
cat ~/.aws/credentials

# Windows
type %USERPROFILE%\.aws\credentials
```

### "An error occurred (InvalidAccessKeyId)"

Access key is wrong or expired. Get a new key from your team lead.

### "botocore.parsers.ResponseParserError"

AWS CLI needs updating:

```bash
pip install --upgrade awscli
```

### Commands work locally but still getting 404 in browser

Make sure:
1. ✅ Bucket is public (set policy)
2. ✅ Website hosting enabled
3. ✅ Files uploaded with `aws s3 sync`
4. ✅ Using correct URL with region code

See AWS_S3_TROUBLESHOOT_404.md for more help.

## Quick Command Cheat Sheet

```bash
# Configure
aws configure

# Verify credentials
aws sts get-caller-identity

# Create bucket
aws s3api create-bucket --bucket my-bucket --region ap-southeast-2 --create-bucket-configuration LocationConstraint=ap-southeast-2

# Enable hosting
aws s3 website s3://my-bucket --index-document index.html --error-document index.html

# Make public
aws s3api put-public-access-block --bucket my-bucket --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# Set policy
aws s3api put-bucket-policy --bucket my-bucket --policy '{JSON_POLICY}'

# Upload
aws s3 sync frontend/dist/ s3://my-bucket/

# List files
aws s3 ls s3://my-bucket/

# Verify bucket
aws s3api get-bucket-location --bucket my-bucket
```

---

**Bottom Line:** Use your local computer's terminal instead of CloudShell. It's faster, doesn't require special permissions, and works better for hackathons! 🚀