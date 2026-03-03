#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID=$(gcloud config get-value project)
ZONE="us-central1-c"
SERVICE_ACCOUNT="webserver-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Starting HW4 Infrastructure Deployment..."

# 1. Create VM1 (Python Web Server)
echo "Creating VM1..."
gcloud compute instances create vm1 \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server \
    --address=34.122.143.212 \
    --metadata-from-file startup-script=startup.sh,main-py=main.py

# 2. Create VM3 (Forbidden Country Reporting Service)
echo "Creating VM3..."
gcloud compute instances create vm3 \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --metadata-from-file startup-script=startup.sh,report-service-py=../hw3/report_service.py

# Wait for VMs to be RUNNING
for vm in vm1 vm3; do
    echo "Waiting for $vm to be RUNNING..."
    while [[ "$(gcloud compute instances describe $vm --zone=$ZONE --project=$PROJECT_ID --format='value(status)')" != "RUNNING" ]]; do
        sleep 5
    done
    echo "$vm is RUNNING."
done

echo "Waiting for startup scripts to complete (polling for lock file)..."
for vm in vm1 vm3; do
    echo "Waiting for $vm to finish startup..."
    until gcloud compute ssh "$vm" \
        --zone=$ZONE \
        --project=$PROJECT_ID \
        --quiet \
        --command="test -f /var/log/startup_already_done" 2>/dev/null; do
        sleep 15
    done
    echo "$vm startup complete."
done

echo ""
echo "Deployment complete."
# echo "Test with:"
# echo "  curl 'http://34.122.143.212:8080/?file=generated_html/1.html'"
# echo "  curl -H 'X-country: Iran' 'http://34.122.143.212:8080/?file=generated_html/1.html'"
