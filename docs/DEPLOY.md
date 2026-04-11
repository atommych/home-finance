# Deployment Guide

## Prerequisites

- Google Cloud account with billing enabled
- GCP project created
- `gcloud` CLI installed
- Terraform installed
- Supabase account (free tier)

---

## Step 1: Set up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Choose a region close to your users (e.g., `eu-west-1` for Europe)
3. Note your **Project URL** and **anon public key** from Settings > API
4. Run the schema migration:
   - Go to SQL Editor in Supabase Dashboard
   - Paste the contents of `supabase/migrations/001_initial_schema.sql`
   - Click "Run"
5. Verify tables were created in Table Editor

### Supabase Auth setup
- Go to Authentication > Settings
- Enable email/password sign-in
- (Optional) Enable Google OAuth provider
- Set site URL to your Cloud Run URL (update after first deploy)

---

## Step 2: Set up GCP

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com

# Create a service account for CI/CD
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

## Step 3: Deploy with Terraform (Option A)

```bash
cd infra/terraform

# Copy and fill in variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# First, build and push the Docker image
cd ../..
docker build --target production -f infra/docker/Dockerfile -t gcr.io/YOUR_PROJECT_ID/home-finance:latest .
docker push gcr.io/YOUR_PROJECT_ID/home-finance:latest

# Deploy
cd infra/terraform
terraform init
terraform plan
terraform apply
```

---

## Step 3: Deploy with GitHub Actions (Option B)

1. Push code to GitHub
2. Add these repository secrets (Settings > Secrets > Actions):

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Contents of `key.json` (the service account key) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon key |

3. Push to `main` branch — the deploy workflow triggers automatically

---

## Step 4: Manual deploy (quickest)

```bash
# Build
docker build --target production -f infra/docker/Dockerfile -t gcr.io/YOUR_PROJECT_ID/home-finance:latest .

# Push
gcloud auth configure-docker
docker push gcr.io/YOUR_PROJECT_ID/home-finance:latest

# Deploy
gcloud run deploy home-finance \
  --image gcr.io/YOUR_PROJECT_ID/home-finance:latest \
  --region europe-west1 \
  --port 8501 \
  --set-env-vars "SUPABASE_URL=https://xxx.supabase.co,SUPABASE_KEY=xxx,DEBUG=false" \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 3
```

---

## Post-deploy

1. Get the Cloud Run URL from the output
2. Update Supabase Auth site URL (Authentication > URL Configuration)
3. Test the full flow: sign up → upload PDF → view dashboard
4. (Optional) Set up a custom domain in Cloud Run settings

---

## Cost Estimate (monthly)

| Service | Free Tier | Beyond Free |
|---------|-----------|-------------|
| Supabase (DB + Auth) | 500MB DB, 50K MAU | $25/mo Pro |
| Cloud Run | 2M requests, 360K vCPU-sec | ~$0.00002/req |
| Container Registry | 500MB storage | $0.026/GB |
| **Total at launch** | **$0** | |
