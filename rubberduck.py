import speech_recognition as sr
from pyChatGPT import ChatGPT
from torch.autograd.forward_ad import enter_dual_level
import whisper
import re
import asyncio
from datetime import datetime
import os
import pydub
import pyperclip
from pydub import playback

# OUTPUT SETTINGS
home = os.environ.get('HOME')
rd_path = home + "/.rubber_duck/"
if not os.path.exists(rd_path):
    os.makedirs(rd_path)
rd_out_filename = rd_path + "rubber_duck.out"
with open(rd_out_filename, 'w') as file:
    pass

# PLUGIN SETTINGS
PLUGIN = "nvim"
NVIM_SERVER = "/tmp/nvim_server.pipe"

# AUDIO SETTINGS
TMP_AUDIO_FILE = "/tmp/audio.wav"

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
CONTEXT_WAKE_WORD = "context"
CHAT_WAKE_WORD = "ducky"
WIPE_WAKE_WORD = "wipe"
RESET_CHAT_WAKE_WORD = "reset"
QUIT_WORD = "quit"

# AUDIO RECOGNITION MODELS
base_model = whisper.load_model("base.en")
tiny_model = whisper.load_model("tiny.en")

# GPT SETTINGS
GPT_MODEL = "4"
token = os.environ.get('CHATGPT_TOKEN')
api = ChatGPT(token, model=GPT_MODEL)




def get_wake_word(phrase):
    if CONTEXT_WAKE_WORD in phrase.lower():
        return CONTEXT_WAKE_WORD
    elif CHAT_WAKE_WORD in phrase.lower():
        return CHAT_WAKE_WORD
    elif WIPE_WAKE_WORD in phrase.lower():
        return WIPE_WAKE_WORD
    elif RESET_CHAT_WAKE_WORD in phrase.lower():
        return RESET_CHAT_WAKE_WORD
    elif QUIT_WORD in phrase.lower():
        return QUIT_WORD
    else:
        return None


def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")
    playback.play(sound)


def exit_graceful(text):
    os.remove(TMP_AUDIO_FILE)
    print(f"Exiting. Reason: {text}")
    exit()


def write_answer(text):
    chat_file = open(rd_out_filename, "a")
    chat_file.write(text)
    chat_file.close()
    after_write_action(PLUGIN)


def after_write_action(plugin):
    if plugin == "nvim":
        os.system(f'nvim --remote-expr "nvim_command(\'checktime\')" --server {NVIM_SERVER}')


def cycle_out_file():
    current_datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
    destination_path = f'{rd_path}_{current_datetime_str}.txt'
    os.rename(rd_out_filename, destination_path)
    with open(rd_out_filename, 'w'):
        pass
    after_write_action(PLUGIN)


async def main():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Waiting for wake words '{CONTEXT_WAKE_WORD}' or '{CHAT_WAKE_WORD}'")
            while True:
                audio = recognizer.listen(source)
                try:
                    with open(TMP_AUDIO_FILE, "wb") as f:
                        f.write(audio.get_wav_data())
                    # Use the preloaded tiny_model
                    result = tiny_model.transcribe(TMP_AUDIO_FILE)
                    phrase = result["text"]
                    print(f"You said: {phrase}")

                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print("No wake word detected.")
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue

            context = ""
            if wake_word == QUIT_WORD:
                play_audio(AUD_QUIT)
                exit_graceful("Quit word detected.")
            elif wake_word == WIPE_WAKE_WORD:
                play_audio(AUD_CHAT_WIPED)
                cycle_out_file()
            elif wake_word == RESET_CHAT_WAKE_WORD:
                play_audio(AUD_CHAT_RESET)
                cycle_out_file()
                response = api.reset_conversation()
            elif wake_word == CONTEXT_WAKE_WORD:
                # Get clipboard, check if it is empty or short
                clipboard_content = pyperclip.paste()
                if len(clipboard_content) < 100:
                    clipboard_content = ""
                context += clipboard_content

            if wake_word == CHAT_WAKE_WORD or wake_word == CONTEXT_WAKE_WORD:
                print("Speak a prompt...")
                play_audio(AUD_RD_LISTEN)
                audio = recognizer.listen(source)
                user_input = ""
                try:
                    with open(TMP_AUDIO_FILE, "wb") as f:
                        f.write(audio.get_wav_data())
                    result = base_model.transcribe(TMP_AUDIO_FILE)
                    user_input = result["text"]
                    write_answer(f"User: {user_input}\n")
                    print(f"You said: {user_input}")
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue
                if len(user_input) > 35:
                    if len(context) > 50:
                        user_input = user_input + f"---\nCode:\n{context}\n---"
                    response = api.send_message(message=user_input, id="0")
                    # This library will only return one message, unlike the API
                    message = response["choices"][0]["message"]["content"]
                    chat_response = re.sub('\[\^\d+\^\]', '', message)
                    print("GPT's response:", chat_response)
                    write_answer(f"CHAT_GPT_{GPT_MODEL}:\n{chat_response}")
                    play_audio(AUD_NEW_ANSWER)
                else:
                    print(f"User input too short. Suspected bad transcription. User input: {user_input}")


if __name__ == "__main__":
    asyncio.run(main())
