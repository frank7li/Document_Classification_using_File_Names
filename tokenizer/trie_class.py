import re
class TrieNode:
    def __init__(self, letter='', is_end_of_word=False):
        self.letter = letter
        self.is_end_of_word = is_end_of_word
        self.trie_node_arr = [None] * 36


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char.isalpha():
                index = ord(char) - ord('a')
            elif char.isnumeric():
                index = int(char) + 26
            else:
                return
            if index < 0 or index > 35:
                return
            if not node.trie_node_arr[index]:
                node.trie_node_arr[index] = TrieNode(char)
            node = node.trie_node_arr[index]
        node.is_end_of_word = True

    def is_word(self, word):
        node = self.root
        for char in word:
            if char.isalpha():
                index = ord(char) - ord('a')
            elif char.isnumeric():
                index = int(char) + 26
            else:
                return False
            if index < 0 or index > 35:
                return False
            if not node.trie_node_arr[index]:
                return False
            node = node.trie_node_arr[index]
        return node.is_end_of_word

    def is_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char.isalpha():
                index = ord(char) - ord('a')
            elif char.isnumeric():
                try:
                    index = int(char) + 26
                except ValueError:
                    return False
                # index = int(char) + 26
            else:
                return False
            if index < 0 or index > 35:
                return False
            if not node.trie_node_arr[index]:
                return False
            node = node.trie_node_arr[index]
        return True


class TrieTokenizer:
    def __init__(self):
        self.trie = Trie()

    def add_word(self, word):
        self.trie.insert(word)

    def add_list_word(self, word_list):
        for word in word_list:
            self.trie.insert(word)

    def find_word(self, string):
        length = len(string)
        if length == 0:
            return ""
        left = 0
        right = 1
        last_word = ""
        while left < length-1 and right < length:
            substring = string[left:right]
            while self.trie.is_prefix(substring):
                if self.trie.is_word(substring):
                    last_word = substring

                if right == length:
                    break
                right += 1
                substring = string[left:right]
            left += 1
            right = left + 1
        if last_word != "":
            return last_word



    def tokenize_string(self, string):
        word = self.find_word(string)
        if word is None:
            return [string]
        result = []
        pattern = re.escape(word)
        string_list = re.split(f'({pattern})', string)
        for string in string_list:
            if string == word:
                result.append(string)
            else:
                if string != '':
                    result += self.tokenize_string(string)
        return result


    def tokenize_list(self, list_string):
        result = []
        for string in list_string:
            tokens = self.tokenize_string(string)
            result.append(tokens)
        return result






