import urllib.request
import json
import os
import ssl
import markdown
from IPython.display import display, HTML

from promptflow.tracing import start_trace, trace

from dotenv import load_dotenv
import os

load_dotenv()
pf_api_key = os.getenv("pf_api_key")



def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context



@trace
def prepare_request_data(question):
    """Function to encode question into json format"""

    print("Preparing request data...")
    return str.encode(json.dumps({"question": question, "chat_history": []}))

@trace
def send_request(url, body, headers):
    """Function to send request to PromptFlow endpoint"""

    print("Sending request to PromptFlow endpoint...")
    req = urllib.request.Request(url, body, headers)
    response = urllib.request.urlopen(req)
    return response.read().decode("utf8", 'ignore')

@trace
def process_response(response_text):
    """Function to process response from PromptFlow endpoint"""

    print("Processing response...")
    response_json = json.loads(response_text).get('answer')
    display(HTML(markdown.markdown(str(response_json))))

def ask_insurance_chatbot_with_tracing(question):
    """Function to use PromptFlow chatbot service with tracing"""

    allowSelfSignedHttps(True)  # Self-signed 인증서 허용

    body = prepare_request_data(question)

    url = 'https://pf-eus-fdrydemo.eastus.inference.ml.azure.com/score'
    api_key = pf_api_key
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }

    try:
        response_text = send_request(url, body, headers)
        process_response(response_text)

    except urllib.error.HTTPError as error:
        print("The request failed with status code:", error.code)
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))



if __name__ == "__main__":
    start_trace()
    question = "손가락 골절을 당해도 보장받을 수 있을까?"
    ask_insurance_chatbot_with_tracing(question)