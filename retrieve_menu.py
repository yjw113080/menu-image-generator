import os
from langchain import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import langchain.document_loaders

def get_llm():
    
    model_kwargs = { #AI21
        "maxTokens": 8000, 
        "temperature": 0, 
        "topP": 0.5, 
        "stopSequences": [], 
        "countPenalty": {"scale": 0 }, 
        "presencePenalty": {"scale": 0 }, 
        "frequencyPenalty": {"scale": 0 } 
    }
    
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), #sets the profile name to use for AWS credentials (if not the default)
        region_name=os.environ.get("BWB_REGION_NAME"), #sets the region name (if not the default)
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), #sets the endpoint URL (if necessary)
        model_id="anthropic.claude-v2", #set the foundation model
        model_kwargs=model_kwargs) #configure the properties for Claude
    
    return llm

pdf_path = "uploaded_file.pdf"

def get_example_file_bytes(): #provide the file bytes so the user can download a ready-made example
    with open("2022-Shareholder-Letter.pdf", "rb") as file:
        file_bytes = file.read()
    
    return file_bytes


def save_file(file_bytes): #save the uploaded file to disk to summarize later
    
    with open(pdf_path, "wb") as f: 
        f.write(file_bytes)
    
    return f"Saved {pdf_path}"

def get_docs():
    
    loader = PyPDFLoader(file_path=pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "], chunk_size=4000, chunk_overlap=100 
    )
    docs = text_splitter.split_documents(documents=documents)
    
    return docs


def retrieve_web_data(url):
    try:
        # TODO: Implement web content retrieval using langchain.document_loaders or your chosen library
        # For example, you can use requests library for simple HTTP GET requests.
        # Replace the following line with your actual code to retrieve web content.
        response = langchain.document_loaders.load_document(url)
        
        # Assuming you have the content in a variable named 'content'
        content = response.text
        return content
    except Exception as e:
        print(f"Error retrieving content from {url}: {str(e)}")
        return None

def get_menu(return_intermediate_steps=True):
    docs = get_docs()
    # docs = 
    map_prompt_template = "{text}\n\nPlease retrieve a numbered list of menus items with categorization from the given file:"
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=[docs])
    
    # combine_prompt_template = "{text}\n\nWrite a detailed analysis of the above:"
    # combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
    
    
    llm = get_llm()
    
    return llm.predict(map_prompt) #return a response to the prompt

