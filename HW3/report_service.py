# report_service.py on your laptop
from google.cloud import pubsub_v1
from google.cloud import storage

PROJECT = "cs528-485121"   
BUCKET_NAME = "iantsai-hw2"

storage_client = storage.Client()

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT, "forbidden-topic-sub")

def callback(message):
    data = message.data.decode("utf-8")
    print(f"{data}")
    
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("forbidden_logs/log.txt")

    existing = ""
    if blob.exists():
        existing = blob.download_as_text()

    blob.upload_from_string(existing + f'{data}' + "\n")
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

print(f"Listening for messages on {subscription_path}...")

# i want it to keep this listener in the background running
# used chatgpt for help here
with subscriber:
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        print("\nStopped listening.")