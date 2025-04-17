# Coffee Shop Chatbot Trainer
import json
import random
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder
import pickle

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('wordnet')

# Load and preprocess data
def load_and_preprocess_data():
    with open('data.json', encoding='utf-8') as file:
        data = json.load(file)

    lemmatizer = WordNetLemmatizer()
    words = []
    classes = []
    documents = []
    ignore_letters = ['?', '!', '.', ',']

    for intent in data['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))

    return words, classes, documents, data

def create_training_data(words, classes, documents):
    lemmatizer = WordNetLemmatizer()
    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = []
        pattern_words = document[0]
        pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1

        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training, dtype=object)
    train_x = np.array(list(training[:, 0]))
    train_y = np.array(list(training[:, 1]))
    
    return train_x, train_y

def build_model(input_shape, output_shape):
    model = Sequential()
    model.add(Dense(128, input_shape=(input_shape,), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(output_shape, activation='softmax'))

    adam = Adam(learning_rate=0.001)
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
    return model

def main():
    print("Loading and preprocessing data...")
    words, classes, documents, data = load_and_preprocess_data()
    
    print("Creating training data...")
    train_x, train_y = create_training_data(words, classes, documents)
    
    print("Building model...")
    model = build_model(len(train_x[0]), len(train_y[0]))
    
    print("Training model...")
    model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
    
    print("Saving model and artifacts...")
    model.save('coffee_chatbot_model.h5')
    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))
    
    print(f"Model trained with {len(words)} words and {len(classes)} intents")

if __name__ == "__main__":
    main()