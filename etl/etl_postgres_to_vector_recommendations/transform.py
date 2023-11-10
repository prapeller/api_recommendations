from typing import Any, List
from typing import Dict

import gensim.downloader as api
import numpy as np

# Load pre-trained Word2Vec embeddings
model = api.load('word2vec-google-news-300')


def vectorize(film_text_dict: Dict[str, str], weights: Dict[str, float] = None) -> np.ndarray:
    if weights is None:
        weights = {"description": 2, "type": 1, "genre_names": 3}

    # Initialize an empty vector
    vector = np.zeros(300)  # Word2Vec embeddings are 300-dimensional
    total_weight = 0

    for key, text in film_text_dict.items():
        if text is not None and text != '' and key in weights:
            # Tokenize the text and filter out tokens not in the model's vocabulary
            if isinstance(text, list):
                tokens = [word for word in text if word in model.key_to_index]
            elif isinstance(text, str):
                tokens = [word for word in text.split() if word in model.key_to_index]
            else:
                raise ValueError(f'{text} should be list of strings of string')
            # Calculate the weighted average of the token vectors
            if tokens:
                weighted_vector = np.mean([model[token] for token in tokens], axis=0) * weights[key]
                vector += weighted_vector
                total_weight += weights[key]

    # Normalize the vector by the total weight
    if total_weight > 0:
        vector /= total_weight

    return vector


def transform(rows: List[Dict]) -> Dict[str, np.ndarray]:
    films_vectors = {}
    for row in rows:
        _uuid = row[0]
        description = row[1]
        _type = row[2]
        genre_names = row[3]

        film_text_dict = {
            "description": description,
            "type": _type,
            "genre_names": genre_names,
        }
        film_vector = vectorize(film_text_dict)
        films_vectors[_uuid] = film_vector

    return films_vectors
