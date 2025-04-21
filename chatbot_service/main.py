from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import pyttsx3
import matplotlib.pyplot as plt

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model
model = tf.keras.models.load_model('health_assistant_model.h5')

# Diseases list
diseases = ["Flu", "Cold", "COVID-19", "Allergy"]

# Speak function
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Prediction with uncertainty
def predict_with_uncertainty(model, x, n_iter=100):
    preds = np.array([model(x, training=True).numpy() for _ in range(n_iter)])
    mean = preds.mean(axis=0)
    std = preds.std(axis=0)
    return mean, std

@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.get_json()  # Get JSON data from the request
    symptom_names = ["Fever", "Cough", "Sneezing", "Fatigue", "Loss of Taste", "Itchy Eyes"]
    
    # Extract symptoms from JSON
    input_symptoms = [1 if data.get(symptom) == 'Y' else 0 for symptom in symptom_names]
    input_array = np.array([input_symptoms], dtype=np.float32)
    
    # Predict diagnosis
    mean_probs, std_probs = predict_with_uncertainty(model, input_array)
    most_likely = np.argmax(mean_probs)
    diagnosis = diseases[most_likely]

    # Prepare response data
    test_map = {
        "Flu": "Influenza A/B test",
        "Cold": "Nasal swab",
        "COVID-19": "PCR test",
        "Allergy": "Allergy skin test"
    }
    medicine_map = {
        "Flu": "Oseltamivir (Tamiflu)",
        "Cold": "Rest, fluids, antihistamines",
        "COVID-19": "Isolation + Paracetamol",
        "Allergy": "Loratadine or Cetirizine"
    }

    response = {
        'diagnosis': diagnosis,
        'probabilities': {dis: float(mean_probs[0][i]) for i, dis in enumerate(diseases)},
        'uncertainty': {dis: float(std_probs[0][i]) for i, dis in enumerate(diseases)},
        'test': test_map[diagnosis],
        'medicine': medicine_map[diagnosis]
    }

    # Send response
    speak(f"You may have {diagnosis}. I recommend you take a {test_map[diagnosis]} and consider taking {medicine_map[diagnosis]}")
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
