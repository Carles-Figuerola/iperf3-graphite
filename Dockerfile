FROM python:3

COPY requirements.txt /app/
RUN pip install --no-cache-dir iperf3

COPY *py /app/
ENTRYPOINT ["python", "/app/iperf3_graphite.py"]
