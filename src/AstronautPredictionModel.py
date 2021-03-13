#!/usr/bin/env python
import os
import string
import random
import pickle
import data_handler
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


class AstronautPredictionModel:
    
    def __init__(self, frequency_model=None, characters=None):
        self.frequency_model = frequency_model
        self.characters = characters

    @classmethod
    def load_training_data(cls):
        # your code here
        try:
            with open('work/training_tokens.pickle', 'rb') as file:
                corpus = pickle.load(file)
            print("loaded training data from pickle")
        except:
            with open("work/training_data.txt", encoding="utf8") as file:
                corpus = file.read()
                with open('work/training_tokens.pickle', 'wb') as file:
                    pickle.dump(corpus, file)
                print("loading training data")
        return corpus

    @classmethod
    def load_test_data(cls, fname):
        # your code here
        data = []
        with open(fname) as f:
            for line in f:
                inp = line[:-1]  # the last character is a newline
                data.append(inp)
        return data

    @classmethod
    def write_pred(cls, preds, fname):
        with open(fname, 'wt', encoding="utf-8") as f:
            for p in preds:
                f.write('{}\n'.format(p))

    def run_train(self, data, work_dir):
        # your code here
        try:
            with open('work/frequency_model.pickle', 'rb') as file:
                self.frequency_model = pickle.load(file)
            print("loaded model from pickle")
        except:
            self.frequency_model = data_handler.build_frequency_model()
            with open('work/token_frequencies.pickle', 'wb') as file:
                pickle.dump(self.frequency_model, file)
                print("saved token frequencies with pickle")
                
        try:
            with open('work/characters.pickle', "rb") as file:
                self.characters = pickle.load(file)
            print("loaded characters from pickle")
        except:
            self.characters = data_handler.get_characters()
            with open('work/characters.pickle', 'wb') as file:
                pickle.dump(self.characters, file)
                print("saved characters with pickle")

    def run_pred(self, data):
        # your code here
        if self.frequency_model is None:
            training_data = self.load_training_data()
            self.run_train(training_data, "")
        preds = []
        all_chars = string.ascii_letters
        for inp in data:
            top_guesses = [None, None, None]
            top_guesses_counts = [-1, -1, -1]
            last_word = inp.split()[-1]
            first_word = last_word
            for character in self.characters:
                first_word = last_word + character
                top_guesses, top_guesses_counts = self.__update_guesses__(first_word, top_guesses_counts, top_guesses, last_word)
                for character in self.characters:
                    second_word = first_word + character
                    top_guesses, top_guesses_counts = self.__update_guesses__(second_word, top_guesses_counts, top_guesses, last_word)
            for i in range(len(top_guesses)):
                top_guesses[i] = top_guesses[i][len(last_word)] 
            preds.append(''.join(top_guesses))
        return preds
    
    def __update_guesses__(self, new_word, top_guesses_counts, top_guesses, origin):
        if new_word not in self.frequency_model:
            new_word_count = 0
        else:
            new_word_count = self.frequency_model[new_word]
# case: standard all unique predicting characters -> shift
# case: duplicate predicting, new_word_count higher -> replace and potentially reorder 
# case: duplicate predicting, new_word_count lower -> do nothing
        if new_word_count > top_guesses_counts[0]:
            # [happz] [happyx] [happl] new_word = [happyt] --> [happyt] [happz] [happl] reorder on second item duplicate
            if (top_guesses[1] is not None and top_guesses[1][len(origin)] == new_word[len(origin)]):
                top_guesses[1] = top_guesses[0]
                top_guesses[0] = new_word
                top_guesses_counts[1] = top_guesses_counts[0]
                top_guesses_counts[0] = new_word_count
            # [happz] [happl] [happyx] new_word = [happyt] --> [happyt] [happz] [happl] reorder on third item duplicate
            elif (top_guesses[2] is not None and top_guesses[2][len(origin)] == new_word[len(origin)]):
                top_guesses[2] = top_guesses[1]
                top_guesses[1] = top_guesses[0]
                top_guesses[0] = new_word
                top_guesses_counts[2] = top_guesses_counts[1]
                top_guesses_counts[1] = top_guesses_counts[0]
                top_guesses_counts[0] = new_word_count
            elif (top_guesses[0] is not None and top_guesses[0][len(origin)] == new_word[len(origin)]): # [happyx] [happl] [happz] new_word - [happyt] --> [happyt] [happl] [happz] reorder on first (replace)
                top_guesses[0] = new_word
                top_guesses_counts[0] = new_word_count
            else: # default caes, shift on frist
                top_guesses_counts[2] = top_guesses_counts[1]
                top_guesses_counts[1] = top_guesses_counts[0]
                top_guesses_counts[0] = new_word_count
                top_guesses[2] = top_guesses[1]
                top_guesses[1] = top_guesses[0]
                top_guesses[0] = new_word
        elif new_word_count > top_guesses_counts[1]:
            # [happy] [happl] [happz] new_word = [happyt] --> [happy] [happl] [happz] duplicate on first, do nothing
            if (top_guesses[0] is not None and top_guesses[0][len(origin)] == new_word[len(origin)]):
                return top_guesses, top_guesses_counts
            # [happl] [happy] [happz] new_word = [happyt] --> [happl] [happyt] [happz] duplicate on second, replace
            elif (top_guesses[1] is not None and top_guesses[1][len(origin)] == new_word[len(origin)]):
                top_guesses[1] = new_word
                top_guesses_counts[1] = new_word_count
            # [happl] [happz] [happy] new_word = [happyt] --> [happl] [happyt] [happz] duplicate on third, shift
            elif (top_guesses[2] is not None and top_guesses[2][len(origin)] == new_word[len(origin)]):
                top_guesses[2] = top_guesses[1]
                top_guesses[1] = new_word
                top_guesses_counts[2] = top_guesses_counts[1]
                top_guesses_counts[1] = new_word_count
            else: # all unique -> reorder on second
                top_guesses_counts[2] = top_guesses_counts[1]
                top_guesses_counts[1] = new_word_count
                top_guesses[2] = top_guesses[1]
                top_guesses[1] = new_word
        elif new_word_count > top_guesses_counts[2]:
            # [happy] [happz] [happl] new_word = [happyt] --> [happy] [happz] [happl] duplicate on first, do nothing 
            # [happz] [happy] [happl] new_word = [happyt] --> [happz] [happy] [happl] duplicate on second, do nothing
            if ((top_guesses[0] is not None and top_guesses[0][len(origin)] == new_word[len(origin)]) 
                or (top_guesses[1] is not None and top_guesses[1][len(origin)] == new_word[len(origin)])):
                return top_guesses, top_guesses_counts
            # [happz] [happl] [happy] new_word = [happyt] --> [happz] [happl] [happyt] duplicate on third, replace
            if (top_guesses[2] is not None and top_guesses[2][len(origin)] == new_word[len(origin)]):
                top_guesses[2] = new_word
                top_guesses_counts[2] = new_word_count
            else: # all unique, reorder on third (replace)
                top_guesses_counts[2] = new_word_count
                top_guesses[2] = new_word
        return top_guesses, top_guesses_counts

    def save(self, work_dir):
        # your code here
        # this particular model has nothing to save, but for demonstration purposes we will save a blank file
        with open("work/frequency_model.pickle", "wb") as f:
            pickle.dump(self.frequency_model, f)
        
        with open("work/characters.pickle", "wb") as f:
            pickle.dump(self.characters, f)
            

    @classmethod
    def load(cls, work_dir):
        # your code here
        # this particular model has nothing to load, but for demonstration purposes we will load a blank file
        try:
            with open("work/frequency_model.pickle", "rb") as f:
                frequency_model = pickle.load(f)
            with open("work/characters.pickle", "rb") as f:
                characters = pickle.load(f)
                print("loading successful")
            return AstronautPredictionModel(frequency_model=frequency_model, characters=characters)
        except:
            return AstronautPredictionModel()


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('mode', choices=('train', 'test'), help='what to run')
    parser.add_argument('--work_dir', help='where to save', default='work')
    parser.add_argument('--test_data', help='path to test data', default='example/input.txt')
    parser.add_argument('--test_output', help='path to write test predictions', default='pred.txt')
    args = parser.parse_args()

    random.seed(0)

    if args.mode == 'train':
        if not os.path.isdir(args.work_dir):
            print('Making working directory {}'.format(args.work_dir))
            os.makedirs(args.work_dir)
        print('Instatiating model')
        model = AstronautPredictionModel()
        print('Loading training data')
        train_data = AstronautPredictionModel.load_training_data()
        print('Training')
        model.run_train(train_data, args.work_dir)
        print('Saving model')
        model.save(args.work_dir)
    elif args.mode == 'test':
        print('Loading model')
        model = AstronautPredictionModel.load(args.work_dir)
        print('Loading test data from {}'.format(args.test_data))
        test_data = AstronautPredictionModel.load_test_data(args.test_data)
        print('Making predictions')
        pred = model.run_pred(test_data)
        print('Writing predictions to {}'.format(args.test_output))
        assert len(pred) == len(test_data), 'Expected {} predictions but got {}'.format(len(test_data), len(pred))
        model.write_pred(pred, args.test_output)
    else:
        raise NotImplementedError('Unknown mode {}'.format(args.mode))
