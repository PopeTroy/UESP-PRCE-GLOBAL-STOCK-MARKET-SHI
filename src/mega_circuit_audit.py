import os
import boto3
from groq import Groq
import json

# 1. Initialize Clients
s3 = boto3.client(
    's3',
    endpoint_url='https://flatfiles.massive.com', # Your Endpoint
    aws_access_key_id=os.environ['MASSIVE_ACCESS_KEY'],
    aws_secret_access_key=os.environ['MASSIVE_SECRET_KEY']
)

groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])

def perform_global_audit():
    # 2. Fetch Market Data from Massive Flatfiles
    # Targets the 'us_stocks_sip' or 'crypto' paths
    raw_data = s3.list_objects_v2(Bucket='flatfiles', MaxKeys=5)
    
    # 3. Map to GROQ for Mega Circuit Calculation
    # We send the metadata to Groq to act as the UESP Engine
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are the UESP PRCE Engine. Use the 144K Bridge logic. "
                           "Analyze market data to calculate Global SHI (Systemic Health Index). "
                           "Identify the primary bottleneck: Frictions, Bottlenecks, Filters, or Protocols. "
                           "Return ONLY JSON."
            },
            {
                "role": "user",
                "content": f"Audit this data stream: {str(raw_data['Contents'])}"
            }
        ],
        model="mixtral-8x7b-32768", # High-speed groq model
        response_format={"type": "json_object"}
    )

    # 4. Process Results
    audit_result = json.loads(chat_completion.choices[0].message.content)
    
    # Save the 'Global Health Index' for the WP Scroller
    with open('shi_output.json', 'w') as f:
        json.dump(audit_result, f)
    
    print(f"Audit Complete. Current Issue: {audit_result['active_problem']}")

if __name__ == "__main__":
    perform_global_audit()
