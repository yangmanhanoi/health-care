from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
import joblib
import pyttsx3
import os
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, log_loss
from math import sqrt
from flask_cors import CORS
app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Automatically get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct paths relative to BASE_DIR
model_path_rf = os.path.join(BASE_DIR, "models1", "rf_model_synthetic.pkl")
model_path_fc = os.path.join(BASE_DIR, "models1", "fc_model_synthetic.h5")
model_path_rnn = os.path.join(BASE_DIR, "models1", "rnn_model_synthetic.h5")
model_path_cnn = os.path.join(BASE_DIR, "models1", "cnn_model_synthetic.h5")
label_encoder_path = os.path.join(BASE_DIR, "models1", "label_encoder_synthetic.pkl")
json_path = os.path.join(BASE_DIR, "chatbot_medical_data.json")

# Load chatbot_medical_data.json
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        medical_data = json.load(f)
    print(f"Loaded {len(medical_data)} diseases from {json_path}")
except FileNotFoundError:
    print(f"Error: {json_path} not found")
    raise
except Exception as e:
    print(f"Error loading {json_path}: {e}")
    raise

# Standardize disease names (merge COVID-19 variants)
for disease in medical_data:
    if disease['name'] == "Coronavirus disease (COVID-19)":
        disease['name'] = "COVID-19"

# Load models and label encoder
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
symptom_map = {
    'Fever': ['fever', 'high temperature', 'hot', 'yellowing of the skin and eyes (jaundice)'],
    'Cough': ['cough', 'coughing', 'prolonged cough', 'cough (sometimes with blood)'],
    'Sneezing': ['sneeze', 'sneezing'],
    'Fatigue': ['fatigue', 'tired', 'exhausted', 'feeling very tired', 'weakness'],
    'Loss of Taste': ['loss of taste', 'no taste', 'taste loss', 'lost my sense of taste'],
    'Itchy Eyes': ['itchy eyes', 'eye itch', 'eyes itching'],
    'Sore Throat': ['sore throat', 'throat pain'],
    'Headache': ['headache', 'head pain'],
    'Muscle Pain': ['muscle pain', 'body ache'],
    'Runny Nose': ['runny nose', 'nasal congestion'],
    'Shortness of Breath': ['shortness of breath', 'difficulty breathing'],
    'Rash': ['rash', 'skin rash'],
    'Depressed Mood': ['depressed mood', 'sadness', 'empty', 'loss of pleasure', 'loss of interest'],
    'Swollen Lymph Nodes': ['swollen lymph nodes'],
    'Weight Loss': ['weight loss', 'unintentional weight loss'],
    'Night Sweats': ['night sweats'],
    'Chest Pain': ['chest pain'],
    'Blurred Vision': ['blurred vision', 'vision loss'],
    'Nausea': ['nausea', 'vomiting'],
    'Abdominal Pain': ['pain in the abdomen', 'abdominal pain']
}
symptom_names = list(symptom_map.keys())
diseases = label_encoder.classes_.tolist()

# Function to parse symptoms from text
def parse_symptoms(text):
    symptoms = [0] * len(symptom_names)
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
        x = x.reshape(-1, len(symptom_names), 1)
    if is_rf:
        preds = np.array([model.predict_proba(x) for _ in range(n_iter)])
    else:
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
    model_type = data.get('model_type', 'rnn')  # Default to RNN as per previous request
    
    # Select model and set flags
    model_map = {
        'rf': ('Random Forest', model_rf, False, False, True),
        'fcnn': ('Fully Connected NN', model_fc, False, False, False),
        'rnn': ('RNN', model_rnn, True, False, False),
        'cnn': ('CNN', model_cnn, False, True, False)
    }
    if model_type not in model_map:
        model_type = 'rnn'  # Fallback to RNN
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
            
            # Compute metrics (placeholder for single prediction)
            mae = mean_absolute_error([most_likely], [most_likely])
            mse = mean_squared_error([most_likely], [most_likely])
            rmse = sqrt(mse)
            mape = mean_absolute_percentage_error([most_likely + 1], [most_likely + 1])
            loss = log_loss([most_likely], mean_probs, labels=list(range(len(diseases))))
            
            prob_text = '\n'.join([f"{dis}: P={mean_probs[0][i]:.3f}, Uncertainty={std_probs[0][i]:.3f}" 
                                   for i, dis in enumerate(diseases)])
            
            # Get up to 3 tests and treatments from JSON
            tests = ["Consult a healthcare professional for appropriate testing."]
            treatments = ["Consult a healthcare professional for treatment options."]
            for disease in medical_data:
                if disease['name'] == diagnosis:
                    if disease['tests']:
                        tests = disease['tests'][:3] if len(disease['tests']) > 3 else disease['tests'][:3]
                    if disease['treatments']:
                        treatments = disease['treatments'][:3] if len(disease['treatments']) > 3 else disease['treatments'][:3]
                    break
            
            test_str = "; ".join(tests)
            treatment_str = "; ".join(treatments)
            
            response = (f"Detected symptoms: {[name for i, name in enumerate(symptom_names) if symptoms[i] == 1]}\n\n"
                       f"Diagnosis (using {model_name}):\n{prob_text}\n\n"
                       f"You may have {diagnosis} (±{std_probs[0][most_likely]:.3f}).\n"
                       f"Metrics: MAE={mae:.3f}, MSE={mse:.3f}, RMSE={rmse:.3f}, MAPE={mape:.2f}%, Loss={loss:.3f}\n"
                       f"Recommended Tests: {test_str}\n"
                       f"Recommended Treatments: {treatment_str}\n"
                       f"Please consult a doctor for professional advice.")
            
            speak(f"You may have {diagnosis}. I recommend you take the following tests: {test_str} and consider the following treatments: {treatment_str}")
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
        
        mae = mean_absolute_error([most_likely], [most_likely])
        mse = mean_squared_error([most_likely], [most_likely])
        rmse = sqrt(mse)
        mape = mean_absolute_percentage_error([most_likely + 1], [most_likely + 1])
        loss = log_loss([most_likely], mean_probs, labels=list(range(len(diseases))))
        
        prob_text = '\n'.join([f"{dis}: P={mean_probs[0][i]:.3f}, Uncertainty={std_probs[0][i]:.3f}" 
                               for i, dis in enumerate(diseases)])
        
        tests = ["Consult a healthcare professional for appropriate testing."]
        treatments = ["Consult a healthcare professional for treatment options."]
        for disease in medical_data:
            if disease['name'] == diagnosis:
                if disease['tests']:
                    tests = disease['tests'][:3] if len(disease['tests']) > 3 else disease['tests'][:3]
                if disease['treatments']:
                    treatments = disease['treatments'][:3] if len(disease['treatments']) > 3 else disease['treatments'][:3]
                break
        
        test_str = "; ".join(tests)
        treatment_str = "; ".join(treatments)
        
        response = (f"Diagnosis (using {model_name}):\n{prob_text}\n\n"
                   f"You may have {diagnosis} (±{std_probs[0][most_likely]:.3f}).\n"
                   f"Metrics: MAE={mae:.3f}, MSE={mse:.3f}, RMSE={rmse:.3f}, MAPE={mape:.2f}%, Loss={loss:.3f}\n"
                   f"Recommended Tests: {test_str}\n"
                   f"Recommended Treatments: {treatment_str}\n"
                   f"Please consult a doctor for professional advice.")
        
        speak(f"You may have {diagnosis}. I recommend you take the following tests: {test_str} and consider the following treatments: {treatment_str}")
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