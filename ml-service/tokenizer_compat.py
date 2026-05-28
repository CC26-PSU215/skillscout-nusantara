"""
StandaloneTokenizer — Compatible re-implementation of keras.preprocessing.text.Tokenizer.

Saat tokenizer.pkl di-export dari ai/export_tokenizer.py menggunakan
StandaloneTokenizer (karena Python 3.14 tidak support TensorFlow),
ml-service perlu class ini untuk men-deserialize pickle file.

Class ini mengimplementasikan interface minimal yang dibutuhkan:
  - tokenizer.texts_to_sequences(texts)
  - tokenizer.word_index (dict)
  - len(tokenizer.word_index)
"""

import re
from collections import OrderedDict


class StandaloneTokenizer:
    """
    Re-implementasi minimal dari keras.preprocessing.text.Tokenizer
    yang kompatibel untuk serialisasi (pickle).
    """

    def __init__(self, num_words=None, oov_token=None, lower=True, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'):
        self.num_words = num_words
        self.oov_token = oov_token
        self.lower = lower
        self.filters = filters
        self.word_index = {}
        self.index_word = {}
        self.word_counts = OrderedDict()
        self.word_docs = {}
        self.document_count = 0
        self._filter_pattern = re.compile(f"[{re.escape(filters)}]")

    def _text_to_word_sequence(self, text):
        """Konversi teks ke list kata (sesuai Keras behavior)."""
        if self.lower:
            text = text.lower()
        text = self._filter_pattern.sub(" ", text)
        return [w for w in text.split() if w]

    def fit_on_texts(self, texts):
        """Bangun vocabulary dari kumpulan teks."""
        self.document_count = 0
        for text in texts:
            self.document_count += 1
            if not isinstance(text, str):
                continue
            words = self._text_to_word_sequence(text)
            for w in words:
                if w in self.word_counts:
                    self.word_counts[w] += 1
                else:
                    self.word_counts[w] = 1
            for w in set(words):
                if w in self.word_docs:
                    self.word_docs[w] += 1
                else:
                    self.word_docs[w] = 1

        sorted_words = sorted(self.word_counts.items(), key=lambda x: (-x[1], x[0]))

        self.word_index = {}
        idx = 1
        if self.oov_token:
            self.word_index[self.oov_token] = idx
            idx += 1
        for word, _ in sorted_words:
            self.word_index[word] = idx
            idx += 1
        self.index_word = {v: k for k, v in self.word_index.items()}

    def texts_to_sequences(self, texts):
        """Konversi list teks ke list sequences (list of list of int)."""
        result = []
        oov_index = self.word_index.get(self.oov_token, 0) if self.oov_token else 0
        for text in texts:
            if not isinstance(text, str):
                result.append([])
                continue
            words = self._text_to_word_sequence(text)
            seq = []
            for w in words:
                idx = self.word_index.get(w)
                if idx is not None:
                    if self.num_words and idx >= self.num_words:
                        if oov_index:
                            seq.append(oov_index)
                    else:
                        seq.append(idx)
                elif oov_index:
                    seq.append(oov_index)
            result.append(seq)
        return result
