#!/bin/bash
#
# Lead Sniper - Cloud Run Deployment Script
# 110% Protocol | FAANG Enterprise-Grade | Zero Human Hands
#
# This script deploys the Lead Sniper autonomous pipeline to Google Cloud Run
# with full integration of Firestore, BigQuery, Vertex AI, and Cloud Scheduler.
#
# Usage:
#   ./deploy-to-cloud-run.sh
#

set -e

# Configuration
PROJECT_ID="infinity-x-one-systems"
SERVICE_NAME="lead-sniper"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SERVICE_ACCOUNT="infinity-x-one-systems@appspot.gserviceaccount.com"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                       LEAD SNIPER CLOUD DEPLOYMENT                           ║"
echo "║                  110% Protocol | FAANG Enterprise-Grade                      ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Set project
echo "📋 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Step 2: Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  containerregistry.googleapis.com

# Step 3: Build and push Docker image
echo "🐳 Building Docker image..."
gcloud builds submit --tag ${IMAGE}:latest --timeout=20m

# Step 4: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --concurrency 1 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "PROJECT_ID=${PROJECT_ID}" \
  --service-account ${SERVICE_ACCOUNT}

# Step 5: Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')
echo "✅ Service deployed at: ${SERVICE_URL}"

# Step 6: Setup Cloud Scheduler
echo "⏰ Setting up Cloud Scheduler for daily execution..."

# Delete existing job if it exists
gcloud scheduler jobs delete lead-sniper-daily --location=${REGION} --quiet 2>/dev/null || true

# Create new scheduler job
gcloud scheduler jobs create http lead-sniper-daily \
  --schedule="0 5 * * *" \
  --uri="${SERVICE_URL}/run" \
  --http-method=POST \
  --time-zone="America/New_York" \
  --location=${REGION} \
  --attempt-deadline=3600s \
  --description="Lead Sniper autonomous pipeline - Daily execution at 5 AM EST"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                       DEPLOYMENT COMPLETE ✅                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Deployment Summary:"
echo "   • Service Name: ${SERVICE_NAME}"
echo "   • Service URL: ${SERVICE_URL}"
echo "   • Region: ${REGION}"
echo "   • Schedule: Daily at 5:00 AM EST"
echo "   • Memory: 4 GB"
echo "   • CPU: 2 cores"
echo "   • Max Instances: 10"
echo ""
echo "🎯 Next Steps:"
echo "   1. Test the deployment: curl -X POST ${SERVICE_URL}/run"
echo "   2. View logs: gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
echo "   3. Monitor execution: gcloud scheduler jobs describe lead-sniper-daily --location=${REGION}"
echo ""
echo "🔗 Access URLs:"
echo "   • Cloud Run Console: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}"
echo "   • Cloud Scheduler: https://console.cloud.google.com/cloudscheduler"
echo "   • Firestore: https://console.cloud.google.com/firestore"
echo "   • BigQuery: https://console.cloud.google.com/bigquery"
echo ""
