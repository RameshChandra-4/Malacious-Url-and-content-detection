from joblib import load
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = load("vectorizer.joblib")
def model(shape, out):
    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(input_shape=shape),
      tf.keras.layers.Dense(128, activation='relu'),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(out, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    model.summary()
    return model
loaded_model = model((14313,1),2)
# loaded_model.save("Model.h5")
loaded_model.load_weights("Model.h5")
def malacius(q):
  try:
    vec = vectorizer.transform([q]).toarray()
    vec = vec.reshape(1,14313,1)
    if np.argmax(loaded_model.predict(vec)):
      return 0
    else:
      return 1
  except:  
    return 1
  

