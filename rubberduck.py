import speech_recognition as sr
from pyChatGPT import ChatGPT
import whisper
import re
import asyncio
from datetime import datetime
import os
import pydub
import pyperclip
from pydub import playback
import time
import settings

# AUDIO RECOGNITION MODELS
base_model = whisper.load_model("base.en")
tiny_model = whisper.load_model("tiny.en")

# GPT SETTINGS
api = ChatGPT(settings.TOKEN, model=settings.GPT_MODEL)


def get_wake_word(phrase):
    if settings.CONTEXT_WAKE_WORD in phrase.lower():
        return settings.CONTEXT_WAKE_WORD
    elif settings.CHAT_WAKE_WORD in phrase.lower():
        return settings.CHAT_WAKE_WORD
    elif settings.CODE_WAKE_WORD in phrase.lower():
        return settings.CODE_WAKE_WORD
    elif settings.WIPE_WAKE_WORD in phrase.lower():
        return settings.WIPE_WAKE_WORD
    elif settings.RESET_WAKE_WORD in phrase.lower():
        return settings.RESET_WAKE_WORD
    elif settings.QUIT_WAKE_WORD in phrase.lower():
        return settings.QUIT_WAKE_WORD
    else:
        return None


def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")
    playback.play(sound)


def exit_graceful(text):
    os.remove(settings.TMP_AUDIO_FILE)
    print(f"Exiting. Reason: {text}")
    exit()


def write_answer(text):
    chat_file = open(settings.rd_out_filename, "a")
    chat_file.write(text)
    chat_file.close()
    after_write_action(settings.PLUGIN)


def after_write_action(plugin):
    if plugin == "nvim":
        os.system(f'nvim --remote-expr "nvim_command(\'checktime\')" --server {settings.NVIM_SERVER}')


def cycle_out_file():
    current_datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
    destination_path = f'{settings.rd_path}_{current_datetime_str}.txt'
    os.rename(settings.rd_out_filename, destination_path)
    with open(settings.rd_out_filename, 'w'):
        pass
    after_write_action(settings.PLUGIN)


def do_code_reflection(api, message):
    time.sleep(3)
    code_reflection_message = "Analyze your previous code output as an "\
    "expert software developer. Look for any errors in the code or ways in "\
    "which it will not produce the outcome desired in the original question. "\
    "Re-output the code, with any errors or issues solved. Output only code, "\
    "only provide explanations for advanced concepts, and a short message to "\
    "state your confidence in the code working as intended. Let's take this "\
    "step by step so we don't make any mistakes."
    response = api.send_message(message=code_reflection_message, id="0")
    message = response["choices"][0]["message"]["content"]
    return message


async def main():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Waiting for wake words '{settings.CONTEXT_WAKE_WORD}' or '{settings.CHAT_WAKE_WORD}'"
            f" or '{settings.CODE_WAKE_WORD}' || other commands: '{settings.RESET_WAKE_WORD}',"
            f" '{settings.WIPE_WAKE_WORD}', '{settings.QUIT_WAKE_WORD}'")
            while True:
                audio = recognizer.listen(source)
                try:
                    with open(settings.TMP_AUDIO_FILE, "wb") as f:
                        f.write(audio.get_wav_data())
                    # Use the preloaded tiny_model
                    result = tiny_model.transcribe(settings.TMP_AUDIO_FILE)
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
            if wake_word == settings.QUIT_WAKE_WORD:
                play_audio(settings.AUD_QUIT)
                exit_graceful("Quit word detected.")
            elif wake_word == settings.WIPE_WAKE_WORD:
                play_audio(settings.AUD_CHAT_WIPED)
                cycle_out_file()
            elif wake_word == settings.RESET_WAKE_WORD:
                play_audio(settings.AUD_CHAT_RESET)
                cycle_out_file()
                response = api.reset_conversation()
            elif wake_word == settings.CONTEXT_WAKE_WORD:
                # Get clipboard, check if it is empty or short
                clipboard_content = pyperclip.paste()
                if len(clipboard_content) < 100:
                    clipboard_content = ""
                context += clipboard_content

            if wake_word == settings.CHAT_WAKE_WORD or wake_word == settings.CONTEXT_WAKE_WORD or wake_word == settings.CODE_WAKE_WORD:
                print("Speak a prompt...")
                play_audio(settings.AUD_RD_LISTEN)
                audio = recognizer.listen(source)
                user_input = ""
                try:
                    with open(settings.TMP_AUDIO_FILE, "wb") as f:
                        f.write(audio.get_wav_data())
                    result = base_model.transcribe(settings.TMP_AUDIO_FILE)
                    user_input = result["text"]
                    write_answer(f"User: {user_input}\n")
                    print(f"You said: {user_input}")
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue
                if len(user_input) > 15:
                    if len(context) > 15:
                        user_input = user_input + f"---\nCode:\n{context}\n---"
                    user_input  = user_input + "\nAnswer: Answer as an expert. Let's take this step by step so we don't make any mistakes."
                    response = api.send_message(message=user_input, id="0")
                    # This library will only return one message, unlike the API
                    message = response["choices"][0]["message"]["content"]
                    if wake_word == settings.CONTEXT_WAKE_WORD or wake_word == settings.CODE_WAKE_WORD:
                        new_message = do_code_reflection(api)
                        chat_response = re.sub('\[\^\d+\^\]', '', new_message)
                    else:
                        chat_response = re.sub('\[\^\d+\^\]', '', message)
                    print("GPT's response:", chat_response)
                    write_answer(f"CHAT_GPT_{settings.GPT_MODEL}:\n{chat_response}")
                    play_audio(settings.AUD_NEW_ANSWER)
                else:
                    print(f"User input too short. Suspected bad transcription. User input: {user_input}")


if __name__ == "__main__":
    asyncio.run(main())
