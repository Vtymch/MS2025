from flask import Flask
from prometheus_client import start_http_server, Counter, Gauge
import random

app = Flask(__name__)

# Counter to track total HTTP requests
http_requests_total = Counter('http_requests_total', 'Total HTTP requests')

# Gauge to simulate ping latency
ping_latency = Gauge('ping_latency_seconds', 'Simulated ping latency')

@app.route('/')
def home():
    http_requests_total.inc()  # Increment the request counter
    return "Hello, Prometheus!"

@app.route('/ping')
def ping():
    latency = random.uniform(0.1, 1.5)  # Simulate random ping latency
    ping_latency.set(latency)  # Update the gauge metric
    return f"Ping latency: {latency} sec"

if __name__ == '__main__':
    start_http_server(8001)  # Start Prometheus metrics exporter on port 8001
    app.run(host='0.0.0.0', port=5000)  # Run Flask app on port 5000
