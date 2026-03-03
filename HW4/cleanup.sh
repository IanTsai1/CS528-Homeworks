#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID=$(gcloud config get-value project)
ZONE="us-central1-c"

echo "Starting HW4 Infrastructure Teardown..."

echo "Deleting VM1..."
gcloud compute instances delete vm1 \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null || echo "VM1 not found, skipping."

echo "Deleting VM3..."
gcloud compute instances delete vm3 \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null || echo "VM3 not found, skipping."

echo "Teardown complete."
