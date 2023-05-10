# Rubberduck
Talk to rubberduck about your code and it will make suggestions automatically
At the moment this uses a modified pyChatGPT in order to send the commands to
ChatGPT via the web interface. It could be adapted fairly easily to send 
commands via the API. 

## Requirements
* Relevant audio drivers to work with pydub
* Working pyChatGPT, you will need to set your access token to an env var 'token'
* Chrome (for pyChatGPT)
* Audio input and output

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 rubberduck.py 2>/dev/null
```

## Configuration
Settings can be manually adjusted in the rubberduck.py file. No fancy config yet.

## Usage
Rubberduck will listen for the following 'wake' words.

#### CHAT_WAKE_WORD 
This mode allows you to simply ask a question. The answer will be automatically 
submitted when you stop talking

#### CONTEXT_WAKE_WORD
This mode reads from the clipboard and will append this content to your question
with the text Code: , so the format will be:
{ Prompt question from audio }
Code:
{ Content from clipboard }

#### WIPE_WAKE_WORD and RESET_CHAT_WAKE_WORD
These commands will archive the output file and start a fresh one. 
Reset will also start a new chatGPT conversation (wipe context)

#### QUIT words
Quits the program gracefully


