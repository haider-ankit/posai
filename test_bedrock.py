import boto3
import json

# Initialize the Bedrock client
client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

model_id = "amazon.nova-micro-v1:0"

# Simple prompt to test connection
prompt = "Explain POS systems in one sentence."

native_request = {
    "inferenceConfig": {"max_new_tokens": 50, "temperature": 0},
    "messages": [{"role": "user", "content": [{"text": prompt}]}]
}

try:
    response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
    model_response = json.loads(response["body"].read())
    print("Success! AI Response:", model_response["output"]["message"]["content"][0]["text"])
except Exception as e:
    print(f"Error: {str(e)}")