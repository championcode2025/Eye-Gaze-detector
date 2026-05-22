import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error

def train_gaze_model(csv_file='gaze_dataset.csv', output_model='gaze_ml_model.pkl'):
    print(f"Loading data from {csv_file}...")
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Run the data collection script first!")
        return

    # 1. Define Features (Inputs) and Targets (Outputs)
    X = df[['raw_gaze_x', 'raw_gaze_y']]
    y = df[['screen_target_x', 'screen_target_y']]

    # 2. Split the data (80% for training, 20% for testing the accuracy)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    print("Training Neural Network... (this should take less than a few seconds)")

    # 3. Create the Neural Network
    # Two hidden layers with 64 neurons each. This is complex enough to learn the 
    # curvature of the eye, but lightweight enough to run at 60+ FPS in real-time.
    model = MLPRegressor(
        hidden_layer_sizes=(64, 64), 
        activation='relu',       # Great for non-linear mapping
        solver='adam',           # Standard robust optimizer
        max_iter=2000,           # Allow plenty of time to converge
        random_state=42
    )

    # 4. Train the model!
    model.fit(X_train, y_train)
    print("Training complete!")

    # 5. Evaluate how accurate it is
    predictions = model.predict(X_test)
    
    # Calculate pixel error
    error_x = mean_absolute_error(y_test['screen_target_x'], predictions[:, 0])
    error_y = mean_absolute_error(y_test['screen_target_y'], predictions[:, 1])
    
    print("-" * 30)
    print("MODEL ACCURACY (on unseen test data):")
    print(f"Average Horizontal (X) Error: {error_x:.1f} pixels")
    print(f"Average Vertical (Y) Error:   {error_y:.1f} pixels")
    print("-" * 30)

    # 6. Save the trained model to a file
    with open(output_model, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✓ Model successfully saved as '{output_model}'")
    print("You can now load this file in gaze_estimator.py!")

if __name__ == "__main__":
    train_gaze_model()