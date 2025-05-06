from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
import joblib
import pyttsx3
import os
import re
from sklearn.metrics import mean_absolute_error, mean_squared_error, log_loss
from math import sqrt

app = Flask(__name__)

# Load models and label encoder
# model_path_rf = r"models\cnn_model_large_diverse_10000_samples.h5"
# model_path_fc = r"models\fc_model_large_diverse_10000_samples.h5"
# model_path_rnn = r"C:\DATA1\symptom_dataset\models\rnn_model_large_diverse_10000_samples.h5"
# model_path_cnn = r"C:\DATA1\symptom_dataset\models\cnn_model_large_diverse_10000_samples.h5"
# label_encoder_path = r"C:\DATA1\symptom_dataset\models\label_encoder_large_diverse_10000_samples.pkl"

import os

# Automatically get the absolute path to the project root (where the script is running)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct paths relative to BASE_DIR
model_path_rf = os.path.join(BASE_DIR, "models", "rf_model_large_diverse_10000_samples.pkl")
model_path_fc = os.path.join(BASE_DIR, "models", "fc_model_large_diverse_10000_samples.h5")
model_path_rnn = os.path.join(BASE_DIR, "models", "rnn_model_large_diverse_10000_samples.h5")
model_path_cnn = os.path.join(BASE_DIR, "models", "cnn_model_large_diverse_10000_samples.h5")
label_encoder_path = os.path.join(BASE_DIR, "models", "label_encoder_large_diverse_10000_samples.pkl")


try:
    model_rf = joblib.load(model_path_rf)
    model_fc = tf.keras.models.load_model(model_path_fc)
    model_rnn = tf.keras.models.load_model(model_path_rnn)
    model_cnn = tf.keras.models.load_model(model_path_cnn)
    label_encoder = joblib.load(label_encoder_path)
except Exception as e:
    print(f"Error loading models or label encoder: {e}")
    raise

# Symptom names and mappings
symptom_names = ['Fever', 'Cough', 'Sneezing', 'Fatigue', 'Loss of Taste', 'Itchy Eyes']
diseases = label_encoder.classes_.tolist()
test_map = {
    'Flu': 'Influenza A/B test',
    'Cold': 'Nasal swab',
    'COVID-19': 'PCR test',
    'Allergy': 'Allergy skin test'
}
medicine_map = {
    'Flu': 'Oseltamivir (Tamiflu)',
    'Cold': 'Rest, fluids, antihistamines',
    'COVID-19': 'Isolation + Paracetamol',
    'Allergy': 'Loratadine or Cetirizine'
}

# Function to parse symptoms from text (expanded keywords)
def parse_symptoms(text):
    symptom_map = {
        'Fever': ['fever', 'high temperature', 'hot', 'warm', 'chills', 'sweating'],
        'Cough': ['cough', 'coughing', 'hack', 'dry cough', 'wet cough'],
        'Sneezing': ['sneeze', 'sneezing', 'sneezes'],
        'Fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'lethargic', 'no energy'],
        'Loss of Taste': ['loss of taste', 'no taste', 'taste loss', 'lost my sense of taste', 'can\'t taste'],
        'Itchy Eyes': ['itchy eyes', 'eye itch', 'eyes itching', 'irritated eyes', 'scratchy eyes']
    }
    symptoms = [0] * 6  # [Fever, Cough, Sneezing, Fatigue, Loss of Taste, Itchy Eyes]
    text = text.lower()
    
    for i, (symptom, keywords) in enumerate(symptom_map.items()):
        for keyword in keywords:
            if keyword in text:
                symptoms[i] = 1
                print(f"Matched symptom '{symptom}' with keyword '{keyword}'")
                break
    
    return symptoms

# Speak function
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")

# Prediction with uncertainty
def predict_with_uncertainty(model, x, n_iter=100, is_rnn=False, is_cnn=False, is_rf=False):
    if is_rnn or is_cnn:
        x = x.reshape(-1, 6, 1)
    if is_rf:
        # Random Forest: Single prediction for probability
        preds = np.array([model.predict_proba(x) for _ in range(n_iter)])
    else:
        # Neural networks: Monte Carlo dropout for uncertainty
        preds = np.array([model(x, training=True).numpy() for _ in range(n_iter)])
    mean = preds.mean(axis=0)
    std = preds.std(axis=0)
    return mean, std

# Compute MAPE
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    if np.sum(non_zero) == 0:
        return np.nan
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100

@app.route('/')
def index():
    return render_template('index.html', symptom_names=symptom_names)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip().lower()
    step = int(data.get('step', -1))
    symptoms = data.get('symptoms', [])
    model_type = data.get('model_type', 'rnn')  # Default to FCNN
    print(model_type)
    
    # Select model and set flags
    model_map = {
        'rf': ('Random Forest', model_rf, False, False, True),
        'fcnn': ('Fully Connected NN', model_fc, False, False, False),
        'rnn': ('RNN', model_rnn, True, False, False),
        'cnn': ('CNN', model_cnn, False, True, False)
    }
    if model_type not in model_map:
        model_type = 'fcnn'  # Fallback to FCNN
    model_name, model, is_rnn, is_cnn, is_rf = model_map[model_type]
    
    print(f"Received: message='{user_message}', step={step}, symptoms={symptoms}, model_type={model_type}")

    if user_message == 'start':
        print("Starting symptom checker")
        return jsonify({
            'response': 'Please describe your symptoms (e.g., "I have a fever and cough") or type "ask" to answer Y/N questions:',
            'step': 0,
            'symptoms': [],
            'model_type': model_type
        })
    
    if step == 0:
        if user_message == 'ask':
            print("User selected 'ask', starting Y/N questions")
            return jsonify({
                'response': f"Do you have {symptom_names[0]}? (Y/N)",
                'question': symptom_names[0],
                'step': 1,
                'symptoms': [],
                'model_type': model_type
            })
        
        symptoms = parse_symptoms(user_message)
        print(f"Parsed symptoms: {symptoms}, sum={sum(symptoms)}")
        if sum(symptoms) > 0:
            input_array = np.array([symptoms], dtype=np.float32)
            mean_probs, std_probs = predict_with_uncertainty(model, input_array, is_rnn=is_rnn, is_cnn=is_cnn, is_rf=is_rf)
            most_likely = np.argmax(mean_probs)
            diagnosis = diseases[most_likely]
            pred_label = most_likely
            pred_probs = mean_probs
            
            # Compute metrics (placeholder for single prediction)
            mae = mean_absolute_error([most_likely], [most_likely])
            mse = mean_squared_error([most_likely], [most_likely])
            rmse = sqrt(mse)
            mape = mean_absolute_percentage_error([most_likely + 1], [most_likely + 1])
            loss = log_loss([most_likely], pred_probs, labels=list(range(len(diseases))))
            
            prob_text = '\n'.join([f"{dis}: P={mean_probs[0][i]:.3f}, Uncertainty={std_probs[0][i]:.3f}" 
                                   for i, dis in enumerate(diseases)])
            response = (f"Detected symptoms: {[name for i, name in enumerate(symptom_names) if symptoms[i] == 1]}\n\n"
                       f"Diagnosis (using {model_name}):\n{prob_text}\n\n"
                       f"You may have {diagnosis} (±{std_probs[0][most_likely]:.3f}).\n"
                       f"Metrics: MAE={mae:.3f}, MSE={mse:.3f}, RMSE={rmse:.3f}, MAPE={mape:.2f}%, Loss={loss:.3f}\n"
                       f"Recommended Test: {test_map[diagnosis]}\n"
                       f"Recommended Medicine: {medicine_map[diagnosis]}\n"
                       f"Please consult a doctor for professional advice.")
            
            speak(f"You may have {diagnosis}. I recommend you take a {test_map[diagnosis]} and consider taking {medicine_map[diagnosis]}")
            print(f"Diagnosis: {diagnosis}")
            
            return jsonify({
                'response': response,
                'step': -1,
                'symptoms': [],
                'model_type': model_type
            })
        else:
            print("No symptoms detected, starting Y/N questions")
            return jsonify({
                'response': f"No symptoms detected. Do you have {symptom_names[0]}? (Y/N)",
                'question': symptom_names[0],
                'step': 1,
                'symptoms': [],
                'model_type': model_type
            })
    
    if step >= 1 and step <= len(symptom_names):
        print(f"Processing Y/N question {step}, answer: {user_message}")
        symptoms.append(1 if user_message == 'y' else 0)
        next_step = step + 1
        
        if next_step <= len(symptom_names):
            print(f"Asking next question: {symptom_names[next_step - 1]}")
            return jsonify({
                'response': f"Do you have {symptom_names[next_step - 1]}? (Y/N)",
                'question': symptom_names[next_step - 1],
                'step': next_step,
                'symptoms': symptoms,
                'model_type': model_type
            })
        
        input_array = np.array([symptoms], dtype=np.float32)
        mean_probs, std_probs = predict_with_uncertainty(model, input_array, is_rnn=is_rnn, is_cnn=is_cnn, is_rf=is_rf)
        most_likely = np.argmax(mean_probs)
        diagnosis = diseases[most_likely]
        pred_label = most_likely
        pred_probs = mean_probs
        
        mae = mean_absolute_error([most_likely], [most_likely])
        mse = mean_squared_error([most_likely], [most_likely])
        rmse = sqrt(mse)
        mape = mean_absolute_percentage_error([most_likely + 1], [most_likely + 1])
        loss = log_loss([most_likely], pred_probs, labels=list(range(len(diseases))))
        
        prob_text = '\n'.join([f"{dis}: P={mean_probs[0][i]:.3f}, Uncertainty={std_probs[0][i]:.3f}" 
                               for i, dis in enumerate(diseases)])
        response = (f"Diagnosis (using {model_name}):\n{prob_text}\n\n"
                   f"You may have {diagnosis} (±{std_probs[0][most_likely]:.3f}).\n"
                   f"Metrics: MAE={mae:.3f}, MSE={mse:.3f}, RMSE={rmse:.3f}, MAPE={mape:.2f}%, Loss={loss:.3f}\n"
                   f"Recommended Test: {test_map[diagnosis]}\n"
                   f"Recommended Medicine: {medicine_map[diagnosis]}\n"
                   f"Please consult a doctor for professional advice.")
        
        speak(f"You may have {diagnosis}. I recommend you take a {test_map[diagnosis]} and consider taking {medicine_map[diagnosis]}")
        print(f"Diagnosis: {diagnosis}")
        
        return jsonify({
            'response': response,
            'step': -1,
            'symptoms': [],
            'model_type': model_type
        })
    
    print("Invalid state, resetting")
    return jsonify({
        'response': 'Please type "start" to begin the symptom checker.',
        'step': -1,
        'symptoms': [],
        'model_type': model_type
    })

if __name__ == '__main__':
    app.run(debug=True)