from flask import Flask
from flask import jsonify
import feature_extraction
import requests
import pickle
import numpy as np
import sklearn
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
model = pickle.load(open('RandomForestClassifier.pkl', 'rb'))

@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')


standard_to = StandardScaler()
@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        url = request.form['url']
        print(url)
        X_new = []

        X_input = url
        X_new=feature_extraction.generate_data_set(X_input)
        print(X_new)
        X_new = np.array(X_new).reshape(1,-1)
        print(X_new)


        prediction = model.predict(X_new)
        print(prediction)
        output = prediction[0] 
        print(output)
        if output == 1:
            return render_template('index.html',prediction_text = "Good Url")
        else:
            return render_template('index.html',prediction_text1 = "Malicious Url")
# =============================================================================
#         except:
#             return render_template('index.html',prediction_text = "Close to Phishing Url")
# =============================================================================


            

if __name__=="__main__":
    app.run(debug=True)
