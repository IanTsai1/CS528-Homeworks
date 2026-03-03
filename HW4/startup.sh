#!/bin/bash

# Run-once guard — startup script runs on every boot, this prevents re-running
if [ -f /var/log/startup_already_done ]; then
    echo "Startup script already ran once. Skipping."
    exit 0
fi

# Detect which VM this script is running on
INSTANCE_NAME=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/name" \
    -H "Metadata-Flavor: Google")

# Install dependencies (runs as root, no sudo needed)
DEBIAN_FRONTEND=noninteractive apt-get update -y -q
DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends python3-pip python3-venv

if [[ "$INSTANCE_NAME" == "vm1" ]]; then

    # Create Python virtual environment
    python3 -m venv /opt/venv
    source /opt/venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install \
        google-cloud-logging \
        google-cloud-storage \
        google-cloud-pubsub

    # Retrieve main.py from instance metadata
    curl -sf \
      "http://metadata.google.internal/computeMetadata/v1/instance/attributes/main-py" \
      -H "Metadata-Flavor: Google" > /root/main.py

    # Start web server using venv Python
    nohup /opt/venv/bin/python /root/main.py \
        > /var/log/server.log 2>&1 &


elif [[ "$INSTANCE_NAME" == "vm3" ]]; then

    # Create Python virtual environment
    python3 -m venv /opt/venv
    source /opt/venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install \
        google-cloud-pubsub \
        google-cloud-storage

    # Retrieve report_service.py from metadata
    curl -sf \
      "http://metadata.google.internal/computeMetadata/v1/instance/attributes/report-service-py" \
      -H "Metadata-Flavor: Google" > /root/report_service.py

    # Start report service using venv Python
    nohup /opt/venv/bin/python -u /root/report_service.py \
        > /var/log/report_service.log 2>&1 &
fi

# Create lock file to prevent re-running on reboot
touch /var/log/startup_already_done
echo "Startup complete on $INSTANCE_NAME."
