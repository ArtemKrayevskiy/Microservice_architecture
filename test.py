from influxdb_client import InfluxDBClient
import os

client = InfluxDBClient(
    url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
    token=os.getenv("INFLUXDB_TOKEN", "my-super-token"),
    org=os.getenv("INFLUXDB_ORG", "my-org")
)

query = """
from(bucket: "logs")
  |> range(start: -1h)
  |> limit(n: 1)
"""

tables = client.query_api().query(query)
if tables and any(tables):
    print("Logs found.")
else:
    print("No logs found.")
