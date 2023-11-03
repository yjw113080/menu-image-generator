# menu-image-generator

This repository holds a Python app calling Amazon Bedrock APIs to 1) retrieve menu items dynamically from the web url, and 2) generate images from the retrieved menu. 

https://github.com/yjw113080/menu-image-generator/assets/35519343/e287a34e-4be2-4940-a9bc-1023ebad2535

Disclaimer: This repository has not reviewed by AWS security process yet and it's purely meant to be refered as an example as of 11/3/2023.

## Retrieve menus using Claude V2

```
    template = (
        f"\n\nHuman: Retrieve menu items from the given text in python array. 
            I want the individual items to be a map which consists of title, ingredients and Price. 
            Include ingredients after the menu items. Exclude any drink menus. :\n"
        f"{input_text}"
        f"\n\nAssistant:"
    )

    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

    body = json.dumps({
        "prompt": template,
        "max_tokens_to_sample": 4096, 
        "temperature": 0, 
        "top_p": 0.5
    })  
    modelId = 'anthropic.claude-v2',
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
```

## Generate images using Stable Diffusion

```
    request_body = json.dumps({"text_prompts": 
                               [ {"text": prompt_content } ], #prompts to use
                               "cfg_scale": 20, #how closely the model tries to match the prompt
                               "steps": 50, }) #number of diffusion steps to perform
    
    response = bedrock.invoke_model(body=request_body, modelId=bedrock_model_id) #call the Bedrock endpoint
    
    output = get_response_image_from_payload(response) #convert the response payload to a BytesIO object for the client to consume
    
```

Please contact jiwony@amazon.com if you have any questions or feedback!
