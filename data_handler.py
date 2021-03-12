from google_trans_new import google_translator
from util import LANGUAGES, SPACE_TOPICS
import os
import sys
import wikipedia
import pickle

def translate_topics():
    translator = google_translator()
    characters = set()
    translated = 0
    total = 0
    for language in LANGUAGES.keys():
        for article_name in SPACE_TOPICS:
            wikipedia.set_lang(language)
            if language == "en":
                translation = article_name
            else:
                print(type(article_name))
                translation = translator.translate(article_name, lang_tgt=language)
                if (isinstance(translation, list)):
                    translation = translation[0]
            total += 1
            try:
                print("getting " + str(translation))
                data = wikipedia.page(translation, auto_suggest=False)
            except wikipedia.PageError:
                try:
                    print("getting " + translation + " with a page error and auto_suggest")
                    data = wikipedia.page(translation, auto_suggest=True)
                    print("Tried to get " + translation + " but an error occurred, getting " + data.title + " to replace")
                except:
                    print("failed to get " + translation)
                    continue
            except wikipedia.DisambiguationError as e:
                try:
                    print("getting " + translation + " post disambiguation error")
                    data = wikipedia.page(e.options[0], auto_suggest=False)
                except:
                    try:
                        print("getting " + translation + " post disambiguation error with auto-suggest")
                        data = wikipedia.page(e.options[0], auto_suggest=True)
                    except:
                        print("failed to get " + translation + "with disambiguationError")
                        continue
            with open("data/" + language + "_" + article_name + ".txt", "w", encoding="utf-8") as file:
                print(data.content, file=file)
            characters.update(data.content.split())
            translated += 1
    print("successfully translated: " + str(translated))
    print("total articles attempted: " + str(total))

def get_characters():
    characters = set()
    for file_name in os.listdir("C:/Users/marki/OneDrive/Desktop/CSE/447/cse447-project/data"):
        with open("data/" + file_name, "r", encoding="utf-8") as f:
            for line in f:
                characters.update(list(line))
    with open("characters.pickle", "wb") as result_file:
        pickle.dump(characters, result_file)

get_characters()
with open("characters.pickle", "rb") as file:
    characters = pickle.load(file)
print(len(characters))
    