def dict_chunks_generator(dictionary, chunk_size):
    """Yield chunk_size elements chunks from dictionary."""
    dict_keys = iter(dictionary.keys())
    while True:
        # Extract the next chunk of keys
        chunk_keys = [next(dict_keys, None) for _ in range(chunk_size)]
        # Remove any `None` keys that signify the end of the iterator
        chunk_keys = [key for key in chunk_keys if key is not None]
        if not chunk_keys:
            break
        yield {key: dictionary[key] for key in chunk_keys}
