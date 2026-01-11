# Lead Sniper - Cloud Run Deployment Guide

**110% Protocol | FAANG Enterprise-Grade | Zero Human Hands**

This guide provides multiple methods to deploy the Lead Sniper autonomous pipeline to Google Cloud Run for 24/7 operation.

---

## 🎯 Deployment Overview

The Lead Sniper system will be deployed as:

- **Cloud Run Service**: Containerized application with 4GB RAM, 2 CPUs
- **Cloud Scheduler**: Automated daily execution at 5 AM EST
- **Firestore**: Real-time lead database
- **BigQuery**: Analytics and reporting
- **Vertex AI**: Lead scoring and analysis
- **Cloud Storage**: Results backup

---

## 📋 Prerequisites

1. **GCP Project**: `infinity-x-one-systems`
2. **Service Account**: `infinity-x-one-systems@appspot.gserviceaccount.com`
3. **APIs Enabled**:
   - Cloud Run API
   - Cloud Build API
   - Cloud Scheduler API
   - Firestore API
   - BigQuery API
   - Vertex AI API
   - Container Registry API

4. **Secrets Configured**:
   - `GEMINI_API_KEY`: Gemini API key
   - `GCP_SA_KEY`: Service account JSON key

---

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Recommended)

**Fully automated CI/CD pipeline with zero manual intervention.**

1. **Setup GitHub Secrets**:
   ```
   Go to: Settings → Secrets and variables → Actions
   Add:
   - GCP_SA_KEY (service account JSON)
   - GEMINI_API_KEY (Gemini API key)
   ```

2. **Trigger Deployment**:
   ```bash
   # Push to main branch
   git push origin main
   
   # Or manually trigger
   Go to: Actions → Deploy Lead Sniper to Cloud Run → Run workflow
   ```

3. **Automatic Schedule**:
   - Workflow runs daily at 5 AM EST automatically
   - Pipeline executes on Cloud Run
   - Results sync to Firestore/BigQuery

---

### Method 2: Cloud Shell (Manual)

**Deploy directly from Google Cloud Shell.**

1. **Open Cloud Shell**:
   ```
   https://console.cloud.google.com/cloudshell
   ```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/InfinityXOneSystems/lead-sniper.git
   cd lead-sniper
   ```

3. **Run Deployment Script**:
   ```bash
   ./deploy-to-cloud-run.sh
   ```

4. **Verify Deployment**:
   ```bash
   gcloud run services describe lead-sniper --region=us-central1
   ```

---

### Method 3: Local Deployment (Advanced)

**Deploy from local machine with gcloud CLI.**

1. **Install gcloud SDK**:
   ```bash
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project infinity-x-one-systems
   ```

3. **Deploy**:
   ```bash
   cd lead-sniper
   ./deploy-to-cloud-run.sh
   ```

---

## 🔧 Configuration

### Environment Variables

The following environment variables are automatically configured:

| Variable | Description | Source |
|----------|-------------|--------|
| `PROJECT_ID` | GCP project ID | Hardcoded |
| `GEMINI_API_KEY` | Gemini API key | Secret Manager |
| `GCP_SA_KEY` | Service account key | Secret Manager |

### Resource Limits

| Resource | Value | Reason |
|----------|-------|--------|
| Memory | 4 GB | Supports 100 parallel browser instances |
| CPU | 2 cores | Handles concurrent scraping |
| Timeout | 3600s (1 hour) | Allows full pipeline execution |
| Concurrency | 1 | One pipeline run at a time |
| Max Instances | 10 | Auto-scaling limit |

---

## ⏰ Scheduled Execution

### Cloud Scheduler Configuration

```yaml
Name: lead-sniper-daily
Schedule: 0 5 * * * (5 AM EST daily)
Target: Cloud Run service endpoint
Method: POST
Timeout: 3600s (1 hour)
Retry: 3 attempts with exponential backoff
```

### Manual Trigger

```bash
# Trigger pipeline manually
curl -X POST https://lead-sniper-[hash]-uc.a.run.app/run

# Or via gcloud
gcloud scheduler jobs run lead-sniper-daily --location=us-central1
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Real-time logs
gcloud run services logs tail lead-sniper --region=us-central1

# Recent logs
gcloud run services logs read lead-sniper --region=us-central1 --limit=100
```

### Cloud Console

- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud Scheduler**: https://console.cloud.google.com/cloudscheduler
- **Logs Explorer**: https://console.cloud.google.com/logs
- **Firestore**: https://console.cloud.google.com/firestore
- **BigQuery**: https://console.cloud.google.com/bigquery

---

## 🔍 Verification

### Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe lead-sniper \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Trigger pipeline run
curl -X POST $SERVICE_URL/run
```

### Check Results

```bash
# View Firestore leads
gcloud firestore export gs://infinity-x-one-systems-leads/export

# Query BigQuery
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total_leads FROM `infinity-x-one-systems.leads.validated_leads`'
```

---

## 🛠 Troubleshooting

### Common Issues

**1. Build Timeout**
```bash
# Increase timeout
gcloud builds submit --timeout=30m
```

**2. Memory Exceeded**
```bash
# Increase memory
gcloud run services update lead-sniper --memory=8Gi
```

**3. Authentication Errors**
```bash
# Verify service account permissions
gcloud projects get-iam-policy infinity-x-one-systems
```

**4. Scheduler Not Running**
```bash
# Check scheduler status
gcloud scheduler jobs describe lead-sniper-daily --location=us-central1

# Manually trigger
gcloud scheduler jobs run lead-sniper-daily --location=us-central1
```

---

## 🔄 Updates & Rollbacks

### Deploy New Version

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/infinity-x-one-systems/lead-sniper:v2
gcloud run deploy lead-sniper --image gcr.io/infinity-x-one-systems/lead-sniper:v2
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service=lead-sniper --region=us-central1

# Rollback to previous
gcloud run services update-traffic lead-sniper \
  --to-revisions=lead-sniper-00001-abc=100
```

---

## 📈 Scaling

### Auto-Scaling Configuration

```bash
# Update scaling
gcloud run services update lead-sniper \
  --min-instances=1 \
  --max-instances=20
```

### Cost Optimization

- **Min Instances**: Set to 0 for cost savings (cold starts acceptable)
- **Max Instances**: Set to 10 to control costs
- **CPU Allocation**: CPU only allocated during request processing

---

## 🔐 Security

### Service Account Permissions

Required roles for `infinity-x-one-systems@appspot.gserviceaccount.com`:

- Cloud Run Invoker
- Firestore User
- BigQuery Data Editor
- Vertex AI User
- Storage Object Admin

### Network Security

- Service is publicly accessible (for scheduler)
- Authentication via service account
- Rate limiting enabled
- DDoS protection via Cloud Armor (optional)

---

## 📞 Support

For issues or questions:

1. Check logs: `gcloud run services logs read lead-sniper`
2. Review GitHub Actions: https://github.com/InfinityXOneSystems/lead-sniper/actions
3. Contact: InfinityXOneSystems team

---

**Built with ❤️ by InfinityXOneSystems**

*Powered by Manus Core | Vision Cortex | Vertex AI*
