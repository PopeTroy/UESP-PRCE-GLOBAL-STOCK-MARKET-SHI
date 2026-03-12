import boto3
import os

# Initialize Massive S3 Client
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('MASSIVE_ENDPOINT'),
    aws_access_key_id=os.getenv('MASSIVE_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('MASSIVE_SECRET_KEY')
)

def fetch_latest_market_data():
    # Pulling from the flatfiles/stocks/aggregates path
    response = s3.list_objects_v2(Bucket='flatfiles', Prefix='us_stocks_sip/minute_aggs_v1/2026/03/')
    # Logic to grab the most recent .csv.gz and stream it
    return response['Contents'][-1]
