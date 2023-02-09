import os
import json
import openai
import ast
import re
from fastapi import FastAPI, Query, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

MODEL_NAME = "text-davinci-003"
## Initialize openai key
OPENAI_KEY_FILEPATH = "./openai.txt"
with open(OPENAI_KEY_FILEPATH, "r") as f:
    os.environ["OPENAI_API_KEY"] = f.read()

# TODO: Handle missing openai key file

# Load openai api key
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class UnstructuredText(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get(
    "/test-openai/",
    description="Endpoint to test the OpenAPI integration to make sure it works"
    )
def test_openai(q: str = Query(None, description="The prompt to send to OpenAI")):
    if not q:
        return {"message": "No query provided"}
    print(f"Query: {q}")
    response = openai.Completion.create(model = MODEL_NAME, prompt = q)
    print(f"Response: {response}")

    return response.get('choices')[0].get('text')

@app.post(
    "/stateless-prompt",
    description="""
    General purpose stateless prompt.
    Example: 
    Usecase 1: 'Convert the following to html table '<unstructured text goes here>'"""
)
def to_html(body: UnstructuredText):
    print(f"{body.text}")
    response = openai.Completion.create(
        model = MODEL_NAME, 
        prompt = body.text,
        max_tokens = 256)

    return response.get('choices')[0].get('text')

@app.get(
    "/generic/{method_name}"
)
def generic(method_name: str):
    db = json.loads(open("db.json", "r").read())
    small_prompt = db["prompt"] 
    state = db["state"]

    prompt = f"""
    {small_prompt}

    API Call (indexes are zero-indexed):
    {method_name}

    Database State:
    {state}
    Output the API response as json prefixed with '!API response!:'. 
    Then output the new database state as json, prefixed with '!New Database State!:'. 
    If the API call is only requesting data, then don't change the database state, 
    but base your 'API Response' off what's in the database.
    If insertion is perform on an existing userId in the state, return "ERROR: ID already exists"
    If deletion is performed on a non-existent userId in the state, return "ERROR: ID does not exist"
    """
    response = openai.Completion.create(
        model = MODEL_NAME,
        prompt = f"{prompt}",
        max_tokens = 256
    )
    completion = response.get('choices')[0].get('text')

    print(completion)
    # TODO: save new state
     # parsing "API Response" and "New Database State" with regex
    # api_response_match = re.search("(?<=!API Response!:).*(?=!New Database State!:)", completion, re.DOTALL)
    new_database_match = re.search("(?<=!New Database State!:).*", completion, re.DOTALL)

    print(new_database_match)
    # converting regex result into json string
    # api_response_text = api_response_match.string[api_response_match.regs[0][0]:api_response_match.regs[0][1]].strip()
    new_database_text = new_database_match.string[new_database_match.regs[0][0]:new_database_match.regs[0][1]].strip()

    print(new_database_text)
    new_state = json.loads(json.dumps(ast.literal_eval(new_database_text)))
    print("NEW_STATE")
    print(new_state)

    db["state"] = new_state
    json.dump(db, open("db.json", "w"), indent=4, default=lambda x: x.__dict__)

    return new_database_text