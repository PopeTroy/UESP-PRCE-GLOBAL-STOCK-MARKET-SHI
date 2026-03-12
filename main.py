import os
import boto3
import requests
import json
from groq import Groq

# 1. Configuration from GitHub Secrets
MASSIVE_KEY = os.getenv('MASSIVE_ACCESS_KEY')
MASSIVE_SECRET = os.getenv('MASSIVE_SECRET_KEY')
GROQ_KEY = os.getenv('GROQ_API_KEY')
ENDPOINT = "https://flatfiles.massive.com" # Mapping to flatfiles endpoint

def run_global_audit():
    # Initialize Clients
    groq_client = Groq(api_key=GROQ_KEY)
    s3 = boto3.client(
        's3',
        endpoint_url=ENDPOINT,
        aws_access_key_id=MASSIVE_KEY,
        aws_secret_access_key=MASSIVE_SECRET
    )

    try:
        # A. SCRAPE: Access the stock market flatfiles
        # Listing the most recent files to simulate a real-time scrape
        obj_list = s3.list_objects_v2(Bucket='flatfiles', MaxKeys=10)
        file_metadata = str(obj_list.get('Contents', []))

        # B. CALCULATE: Pass data to Groq for the 144K Bridge Audit
        audit_prompt = f"""
        Act as the UESP PRCE Engine. Perform a Global Audit on this data: {file_metadata}
        1. Apply the 144K Bridge logic to detect system resistance.
        2. Calculate the Global SHI (Systemic Health Index) as a value between 0 and 1.
        3. Identify which specific sector is failing: Frictions, Bottlenecks, Filters, or Protocols.
        Return ONLY a JSON object with keys: "shi", "active_problem", "timestamp".
        """

        completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": audit_prompt}],
            response_format={"type": "json_object"}
        )

        # C. OUTPUT: The final result for the WP Scroller
        result = json.loads(completion.choices[0].message.content)
        
        # Save locally so GitHub Action can commit/upload it
        with open('shi_data.json', 'w') as f:
            json.dump(result, f)
            
        print(f"Audit Success: SHI is {result['shi']} - Issue: {result['active_problem']}")

    except Exception as e:
        print(f"Audit Failed: {str(e)}")

if __name__ == "__main__":
    run_global_audit()
