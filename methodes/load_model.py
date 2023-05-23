import pickle
import numpy as np


def load_model(model, X):
    X = np.array(X)
    X = X.reshape(-1, 1)
    # charger le model
    model = pickle.load(open(model, 'rb'))
    y_pred = model.predict(X)
    return y_pred