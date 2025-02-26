import trie_class
from transformers import AutoTokenizer
from urllib.parse import urlparse
from urllib.parse import unquote
import nltk
from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
import re


nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
nltk.download('words')
word_list = set(words.words())

wordnet_lemmatizer = WordNetLemmatizer()

def is_english_word_nltk(word):
    return word.lower() in word_list


class Tokenizer:
    def __init__(self, model):
        if model == "trie":
            self.tokenizerr = trie_class.TrieTokenizer()
            self.type = 1
        elif model == "bert":
            self.tokenizerr = AutoTokenizer.from_pretrained("bert-base-cased")
            self.type = 2
        else:
            self.tokenizerr = 0
            self.type = 0


    def decode_file_name_list(self, file_name_list):
        result = []
        for element in file_name_list:
            file_name = element[0]
            category = element[1]
            result.append([self.decode_file_name(file_name), category])
        return result


    def decode_file_name(self, file_name):
        file_name = re.split(r'[:/.]', file_name)
        unquoted_filename = []
        for parts in file_name:
            unquoted_filename.append(unquote(parts))

        cleaned_filename = [token for token in unquoted_filename if token != ""]

        tokens = []
        for parts in cleaned_filename:
            tokens += split_by_punc(parts)

        if len(cleaned_filename) >= len(tokens):
            tokenized = False
        else:
            tokenized = True

        tokens2 = []
        for word in tokens:
            if (word not in stop_words) and (word != "www") and (word != "https") and (word != "http") and (word.upper() != "PDF"):
                tokens2 += split_by_camel_case(word)

        tokens3 = []
        for token in tokens2:
            tmp = special_split(token)
            if tmp == []:
                tokens3.append(token)
            else:
                tokens3 += tmp


        tokens3 = [token.lower() for token in tokens3]

        result = []
        for token in tokens3:
            result.append(wordnet_lemmatizer.lemmatize(token))

        final_tokens = []
        for token in result:
            final_tokens += split_on_transition(token)

        return [final_tokens, tokenized]


    def decode_url(self, url):
        us = urlparse(url)
        result = []
        for u in us:
            result.append(self.decode_file_name(u))
        return result

    def add_to_dictionary(self, all_tokens, min_freq, min_length):
        if self.type == 0:
            return

        frequency_dict = {}
        for tokens in all_tokens:
            for token in tokens:
                if token not in frequency_dict:
                    frequency_dict[token] = 1
                else:
                    frequency_dict[token] += 1
        for token in frequency_dict:
            if frequency_dict[token] >= min_freq and len(token) >= min_length:
                if self.type == 1:
                    self.tokenizerr.add_word(token)
                elif self.type == 2:
                    self.tokenizerr.add_tokens(token)

    def add_to_dictionary_tf_idf(self, tf_idf_dict, min_val, min_length):
        if self.type == 0:
            return
        for category in tf_idf_dict:
            for token in tf_idf_dict[category]:
                tf_idf = tf_idf_dict[category][token]
                if len(token) >= min_length and tf_idf >= min_val:
                    if self.type == 1:
                        self.tokenizerr.add_word(token)
                    elif self.type == 2:
                        self.tokenizerr.add_tokens(token)
                    print(token)


    def tokenize(self, all_tokens):
        if self.type == 0:
            return [element[0][0] for element in all_tokens]
        result = []
        for [tokens, processed], category in all_tokens:
            new_tokens = []
            processed_tokens = []
            if processed:
                for token in tokens:
                    if not any(char.isdigit() for char in token):
                        processed_tokens.append(token)
                    else:
                        if self.type == 1:
                            tmp_tokens = self.tokenizerr.tokenize_string(token)
                        elif self.type == 2:
                            tmp_tokens = self.tokenizerr.tokenize(token)

                        for tok in tmp_tokens:
                            tok = tok.replace("#", "")
                            if len(tok) > 1:
                                processed_tokens.append(tok)

                result.append(processed_tokens)
            else:
                for token in tokens:
                    if is_english_word_nltk(token):
                        new_tokens.append(token)
                    else:
                        if self.type == 1:
                            new_tokens += self.tokenizerr.tokenize_string(token)
                        elif self.type == 2:
                            new_tokens += self.tokenizerr.tokenize(token)

                for tok in new_tokens:
                    tok = tok.replace("#", "")
                    if len(tok) > 1 and tok != 'pdf':
                        processed_tokens.append(tok)


                result.append(processed_tokens)
        return result


def split_by_punc(text):
    # text = text.lower()
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~=+'''
    for ele in text:
        if ele in punc:
            text = text.replace(ele, " ")

    ts = text.split()
    return ts


def split_by_camel_case(string):
    l = 0
    r = 1
    while r < len(string):
        if string[l].islower() and string[r].isupper():
            string = string[:l+1] + " " + string[r:]
        l += 1
        r += 1
    tokens = string.split(" ")
    return tokens


def split_on_transition(s):
    return re.findall(r'[a-zA-Z]+|\d+', s)


# Check if the string has consecutive uppercase characters followed by consecutive lowercase characters
def special_split(s):
        i = 0
        n = len(s)

        # Find the end of the consecutive uppercase characters
        while i < n and s[i].isupper():
            i += 1

        # If no uppercase characters or no lowercase characters after uppercase characters
        if i <= 2 or i == n:
            return []

        # Ensure the remaining characters are all lowercase
        for j in range(i, n):
            if not s[j].islower():
                return []

        first_part = s[:i-1]
        second_part = s[i-1:]

        return [first_part, second_part]
