import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

# Define output directory
output_dir = r"C:\DATA1\symptom_dataset"

# Create directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Symptom names and diagnoses
symptoms = ['Fever', 'Cough', 'Sneezing', 'Fatigue', 'Loss of Taste', 'Itchy Eyes']
diagnoses = ['Flu', 'Cold', 'COVID-19', 'Allergy']

# Function to generate symptom patterns based on diagnosis
def generate_symptoms(diagnosis, n_samples):
    data = {sym: np.zeros(n_samples, dtype=int) for sym in symptoms}
    
    if diagnosis == 'Flu':
        # Flu: High chance of Fever, Cough, Fatigue
        data['Fever'] = np.random.choice([1, 0], n_samples, p=[0.8, 0.2])
        data['Cough'] = np.random.choice([1, 0], n_samples, p=[0.7, 0.3])
        data['Fatigue'] = np.random.choice([1, 0], n_samples, p=[0.6, 0.4])
        data['Sneezing'] = np.random.choice([1, 0], n_samples, p=[0.2, 0.8])
        data['Loss of Taste'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
        data['Itchy Eyes'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
    
    elif diagnosis == 'Cold':
        # Cold: High chance of Cough, Sneezing
        data['Fever'] = np.random.choice([1, 0], n_samples, p=[0.3, 0.7])
        data['Cough'] = np.random.choice([1, 0], n_samples, p=[0.8, 0.2])
        data['Sneezing'] = np.random.choice([1, 0], n_samples, p=[0.7, 0.3])
        data['Fatigue'] = np.random.choice([1, 0], n_samples, p=[0.4, 0.6])
        data['Loss of Taste'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
        data['Itchy Eyes'] = np.random.choice([1, 0], n_samples, p=[0.2, 0.8])
    
    elif diagnosis == 'COVID-19':
        # COVID-19: High chance of Fever, Cough, Loss of Taste
        data['Fever'] = np.random.choice([1, 0], n_samples, p=[0.7, 0.3])
        data['Cough'] = np.random.choice([1, 0], n_samples, p=[0.6, 0.4])
        data['Sneezing'] = np.random.choice([1, 0], n_samples, p=[0.2, 0.8])
        data['Fatigue'] = np.random.choice([1, 0], n_samples, p=[0.5, 0.5])
        data['Loss of Taste'] = np.random.choice([1, 0], n_samples, p=[0.6, 0.4])
        data['Itchy Eyes'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
    
    elif diagnosis == 'Allergy':
        # Allergy: High chance of Sneezing, Itchy Eyes
        data['Fever'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
        data['Cough'] = np.random.choice([1, 0], n_samples, p=[0.3, 0.7])
        data['Sneezing'] = np.random.choice([1, 0], n_samples, p=[0.8, 0.2])
        data['Fatigue'] = np.random.choice([1, 0], n_samples, p=[0.3, 0.7])
        data['Loss of Taste'] = np.random.choice([1, 0], n_samples, p=[0.1, 0.9])
        data['Itchy Eyes'] = np.random.choice([1, 0], n_samples, p=[0.7, 0.3])
    
    data['Diagnosis'] = [diagnosis] * n_samples
    return pd.DataFrame(data)

# Dataset 1: Balanced Small Dataset (1000 samples)
n_samples_per_class = 250
dataset1 = pd.concat([
    generate_symptoms('Flu', n_samples_per_class),
    generate_symptoms('Cold', n_samples_per_class),
    generate_symptoms('COVID-19', n_samples_per_class),
    generate_symptoms('Allergy', n_samples_per_class)
], ignore_index=True)
dataset1 = dataset1.sample(frac=1, random_state=42).reset_index(drop=True)
dataset1.to_csv(os.path.join(output_dir, 'symptom_disease_dataset_balanced.csv'), index=False)
print(f"Dataset 1 (Balanced) generated: {os.path.join(output_dir, 'symptom_disease_dataset_balanced.csv')}")

# Dataset 2: Imbalanced Medium Dataset (5000 samples)
dataset2 = pd.concat([
    generate_symptoms('Flu', 2000),  # 40%
    generate_symptoms('Cold', 1500),  # 30%
    generate_symptoms('COVID-19', 1000),  # 20%
    generate_symptoms('Allergy', 500)  # 10%
], ignore_index=True)
dataset2 = dataset2.sample(frac=1, random_state=42).reset_index(drop=True)
dataset2.to_csv(os.path.join(output_dir, 'symptom_disease_dataset_imbalanced.csv'), index=False)
print(f"Dataset 2 (Imbalanced) generated: {os.path.join(output_dir, 'symptom_disease_dataset_imbalanced.csv')}")

# Dataset 3: Large Diverse Dataset (10,000 samples)
dataset3 = pd.concat([
    generate_symptoms('Flu', 3000),  # 30%
    generate_symptoms('Cold', 2500),  # 25%
    generate_symptoms('COVID-19', 2500),  # 25%
    generate_symptoms('Allergy', 2000)  # 20%
], ignore_index=True)
# Add noise: randomly flip 5% of symptom values
for col in symptoms:
    noise_idx = np.random.choice(dataset3.index, size=int(0.05 * len(dataset3)), replace=False)
    dataset3.loc[noise_idx, col] = 1 - dataset3.loc[noise_idx, col]
dataset3 = dataset3.sample(frac=1, random_state=42).reset_index(drop=True)
dataset3.to_csv(os.path.join(output_dir, 'symptom_disease_dataset_large.csv'), index=False)
print(f"Dataset 3 (Large Diverse) generated: {os.path.join(output_dir, 'symptom_disease_dataset_large.csv')}")