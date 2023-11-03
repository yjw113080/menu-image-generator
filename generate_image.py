import os
import boto3 #import aws sdk and supporting libraries
import json
import base64
from io import BytesIO


bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

bedrock_model_id = "stability.stable-diffusion-xl-v0" #use the Stable Diffusion model



def get_response_image_from_payload(response): #returns the image bytes from the model response payload

    payload = json.loads(response.get('body').read()) #load the response body into a json object
    images = payload.get('artifacts') #extract the image artifacts
    image_data = base64.b64decode(images[0].get('base64')) #decode image

    return BytesIO(image_data) #return a BytesIO object for client app consumption



def get_image_response(prompt_content): #text-to-text client function
    print("============================")
    print("Prompt content given to get_image_response: ", prompt_content)
    request_body = json.dumps({"text_prompts": 
                               [ {"text": prompt_content } ], #prompts to use
                               "cfg_scale": 20, #how closely the model tries to match the prompt
                               "steps": 50, }) #number of diffusion steps to perform
    
    response = bedrock.invoke_model(body=request_body, modelId=bedrock_model_id) #call the Bedrock endpoint
    
    output = get_response_image_from_payload(response) #convert the response payload to a BytesIO object for the client to consume
    
    return output
    
