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
    with open("work/characters.pickle", "wb") as result_file:
        pickle.dump(characters, result_file)
    return characters
        
def get_characters_length(characters: set, from_pickle=False):
    if (from_pickle):
        with open("work/characters.pickle", "rb") as file:
            characters = pickle.load(file)
        return len(characters)
    else:
        return len(characters)
    
def build_frequency_model():
    frequency_model = dict()
    for file_name in os.listdir("C:/Users/marki/OneDrive/Desktop/CSE/447/cse447-project/data"):
        with open("data/" + file_name, "r", encoding="utf-8") as f:
            for line in f:
                words = line.split()
                for word in words:
                    if word not in frequency_model.keys():
                        frequency_model[word] = 0
                    frequency_model[word] += 1
    with open("work/frequency_model.pickle", "wb") as file:
        pickle.dump(frequency_model, file)
    return frequency_model

def load_frequency_model():
    with open("work/frequency_model.pickle", "rb") as f:
        frequency_model = pickle.load(f)
        return frequency_model
    
def merge_language_files():
    with open("work/training_data.txt", "w", encoding="utf-8") as output_file:
        for file_name in os.listdir("C:/Users/marki/OneDrive/Desktop/CSE/447/cse447-project/data"):
            with open("data/" + file_name, "r", encoding="utf-8") as current_file:
                for line in current_file:
                    output_file.write(line)
