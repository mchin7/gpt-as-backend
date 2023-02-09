# tipping
Tipping GPT

## Getting started
1. Create a virtualenv with conda or mkvirtualenv
2. Install dependency using `pip install -r requirements.txt`

### Getting openai access
1. Generate an API key token
2. Paste API key into the `openai.txt` - Make sure your git is not picking up change on the file

## Starting up server
1. Run `uvicorn main:app --reload`

## Docs
To read swagger, go to `127.0.0.1:8000/docs`