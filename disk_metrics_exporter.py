import os
import time

import psutil
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Gauge, Histogram, Summary, generate_latest

# Create FastAPI app
app = FastAPI()

# Define metrics
free_space_gauge = Gauge("disk_free_space_bytes", "Free space of the disk", ["path"])
directory_size_gauge = Gauge(
    "directory_size_bytes", "Size of the specific directory", ["directory"]
)
disk_used_gauge = Gauge("disk_used_space_bytes", "Used space of the disk", ["path"])
disk_total_gauge = Gauge("disk_total_space_bytes", "Total space of the disk", ["path"])
disk_io_gauge = Gauge(
    "disk_io_operations_total",
    "Total number of disk I/O operations",
    ["device", "type"],
)
disk_read_gauge = Gauge(
    "disk_read_operations_total", "Total number of disk read operations", ["device"]
)
disk_write_gauge = Gauge(
    "disk_write_operations_total", "Total number of disk write operations", ["device"]
)
disk_latency_summary = Summary(
    "disk_latency_seconds", "Summary of disk I/O operation latency", ["device", "type"]
)
disk_latency_histogram = Histogram(
    "disk_latency_histogram_seconds",
    "Histogram of disk I/O operation latency",
    ["device", "type"],
)


# Update metrics function
def update_metrics(path, directory):
    # Get free space, used space, and total space of the disk
    disk_usage = psutil.disk_usage(path)
    free_space_gauge.labels(path=path).set(disk_usage.free)
    disk_used_gauge.labels(path=path).set(disk_usage.used)
    disk_total_gauge.labels(path=path).set(disk_usage.total)

    # Get the size of the specific directory
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    directory_size_gauge.labels(directory=directory).set(total_size)

    # Get disk I/O statistics
    disk_io_counters = psutil.disk_io_counters(perdisk=True)
    for device, counters in disk_io_counters.items():
        disk_io_gauge.labels(device=device, type="read").set(counters.read_count)
        disk_io_gauge.labels(device=device, type="write").set(counters.write_count)
        disk_read_gauge.labels(device=device).set(counters.read_count)
        disk_write_gauge.labels(device=device).set(counters.write_count)

        # Simulate latency for demonstration purposes
        start_time = time.time()
        time.sleep(0.001)  # Simulate a small delay
        latency = time.time() - start_time

        disk_latency_summary.labels(device=device, type="read").observe(latency)
        disk_latency_summary.labels(device=device, type="write").observe(latency)
        disk_latency_histogram.labels(device=device, type="read").observe(latency)
        disk_latency_histogram.labels(device=device, type="write").observe(latency)


# Define endpoint for metrics
@app.get("/metrics")
async def metrics():
    # Update metrics with the desired path and directory
    update_metrics("/", "/var/log/")
    return Response(content=generate_latest(), media_type="text/plain")
