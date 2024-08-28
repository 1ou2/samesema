import gensim.downloader as api

# Load pre-trained Word2Vec embeddings
word_vectors = api.load('word2vec-google-news-300')

# Now you can use the embeddings
vector = word_vectors['computer']  # Get the vector for 'computer'
similar_words = word_vectors.most_similar('game')  # Find words similar to 'game'
