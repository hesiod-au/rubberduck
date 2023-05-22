import os
import argparse
# Import whisper module

# Set up argument parser
parser = argparse.ArgumentParser(description='Rubber Duck settings')
parser.add_argument('--rd-path', default=os.path.join(os.environ.get('HOME'), ".rubber_duck/"))
parser.add_argument('--plugin', default="nvim")
parser.add_argument('--nvim-server', default="/tmp/nvim_server.pipe")
parser.add_argument('--tmp-audio-file', default="/tmp/audio.wav")
parser.add_argument('--context-wake-word', default="context")
parser.add_argument('--code-wake-word', default="code")
parser.add_argument('--chat-wake-word', default="ducky")
parser.add_argument('--wipe-wake-word', default="wipe")
parser.add_argument('--reset-wake-word', default="reset")
parser.add_argument('--quit-wake-word', default="quit")

# Add arguments for rest of the wake words here...
parser.add_argument('--gpt-model', default="4")
parser.add_argument('--chatgpt-token', default=os.environ.get('CHATGPT_TOKEN'))

args = parser.parse_args()

# OUTPUT SETTINGS
rd_path = args.rd_path
if not os.path.exists(rd_path):
    os.makedirs(rd_path)
rd_out_filename = os.path.join(rd_path, "rubber_duck.out")

# PLUGIN SETTINGS
PLUGIN = args.plugin
NVIM_SERVER = args.nvim_server

# AUDIO SETTINGS
TMP_AUDIO_FILE = args.tmp_audio_file

# AUDIO FILES
AUD_CHAT_WIPED = "audio/chat_wiped.mp3"
AUD_CHAT_RESET = "audio/conversation_reset.mp3"
AUD_DONE = "audio/done.mp3"
AUD_NEW_ANSWER = "audio/new_answer.mp3"
AUD_QUIT = "audio/quitting.mp3"
AUD_RD_LISTEN = "audio/rubberduck_listening.mp3"
AUD_FILE_CLEARED = "audio/display_cleared.mp3"
AUD_CHAT_SUBMITTED = "audio/chat_submitted.mp3"

# WAKE WORDS
CONTEXT_WAKE_WORD = args.context_wake_word
CODE_WAKE_WORD = args.code_wake_word
CHAT_WAKE_WORD = args.chat_wake_word
WIPE_WAKE_WORD = args.wipe_wake_word
RESET_WAKE_WORD = args.reset_wake_word
QUIT_WAKE_WORD = args.quit_wake_word

# GPT SETTINGS
GPT_MODEL = args.gpt_model
TOKEN = args.chatgpt_token
