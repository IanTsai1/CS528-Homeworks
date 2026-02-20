import functions_framework
from google.cloud import storage
import json
import logging
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
PROJECT = "cs528-485121"   
BUCKET_NAME = "iantsai-hw2"
topic_path = publisher.topic_path(PROJECT, "forbidden-topic")


storage_client = storage.Client()

countries = {
    "North Korea",
    "Iran",
    "Cuba",
    "Myanmar",
    "Iraq",
    "Libya",
    "Sudan",
    "Zimbabwe",
    "Syria"
}

def write_structured_log(request, severity, message, **extra_fields):
    log_entry = {
        "severity": severity,
        "message": message,
        **extra_fields
    }

    trace_header = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        log_entry["logging.googleapis.com/trace"] = (
            f"projects/{PROJECT}/traces/{trace[0]}"
        )

    print(json.dumps(log_entry))  
    logging.info(log_entry)       



@functions_framework.http
def file_service(request):

    if request.method != "GET":
        write_structured_log(
            request,
            "WARNING",
            "invalid_method",
            method=request.method
        )
        return ("Not implemented", 501)

    filename = request.args.get("file")

    if not filename:
        write_structured_log(
            request,
            "WARNING",
            "missing_file_parameter"
        )
        return ("Missing file parameter", 400)
    
    country = request.headers.get("X-country", "Unknown")

    if country in countries:
        write_structured_log(
            request,
            "WARNING",
            "forbidden_country_request",
            country=country
        )

        publisher.publish(
            topic_path,
            json.dumps({"country": country, "message": "forbidden access attempt"}).encode("utf-8")
        )

        return ("Permission denied", 400)

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        if not blob.exists():
            write_structured_log(
                request,
                "WARNING",
                "file_not_found",
                file=filename
            )
            return ("File not found", 404)

        content = blob.download_as_text()

        write_structured_log(
            request,
            "NOTICE",
            "file_served",
            file=filename
        )

        return (content, 200)

    except Exception as e:
        write_structured_log(
            request,
            "ERROR",
            "internal_error",
            error=str(e)
        )
        return ("Internal error", 500)
