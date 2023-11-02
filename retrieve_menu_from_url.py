import requests
from bs4 import BeautifulSoup
import boto3
import json


# Function to retrieve web data from a URL
def retrieve_web_data(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract and return the text content of the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the <body> tag and extract its contents
            # body_contents = str(soup.find('body'))
            body_contents = soup.find('body').get_text()
            return body_contents
        else:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving data from {url}: {str(e)}")
        return None

# Function to extract a numbered list of menu items with categorization from input text
def get_menu(input_text):
    # Generate a prompt for extracting menu items
    template = (
        f"\n\nHuman: Retrieve menu items from the given text in python array. I want the individual items to be a map which consists of title, ingredients and price. Include ingredients after the menu items. Exclude any drink menus. :\n"
        f"{input_text}"
        f"\n\nAssistant:"
    )

    # Create a PromptTemplate instance with the template and input variables

    bedrock = boto3.client(service_name='bedrock-runtime')

    body = json.dumps({
        "prompt": template,
        "max_tokens_to_sample": 4096, 
        "temperature": 0, 
        "top_p": 0.5
    })  
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    print(response)
    response_body = json.loads(response.get('body').read())

    menu_items = response_body.get('completion')
    return menu_items
    # if response.status_code == 200:
    #     response_body = json.loads(response.get('body').read())
    #     menu_items = response_body.get('completion')
    #     return menu_items
    # else:
    #     print(f"Error calling the API: {response.status_code} - {response.text}")
    #     return None

