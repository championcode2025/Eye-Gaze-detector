

import numpy as np
import json
from pathlib import Path
import pickle
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class GazeEstimator:
    """
    Takes raw gaze_ratio [0,1] from EyeExtractor (P2)
    Outputs calibrated normalized gaze for screen control (P3)
    
    INPUT: gaze_ratio_x, gaze_ratio_y ∈ [0, 1]
    OUTPUT: {"gaze_x": float, "gaze_y": float, "confidence": float}
    """
    
    def __init__(self, calibration_file="calibration.json"):
        self.calibration_file = calibration_file
        self.calib_coef_x = None
        self.calib_coef_y = None
        
        # Smoothing parameters
        self.alpha = 0.4  
        self.prev_x = 0.5
        self.prev_y = 0.5
        
        self.calibration_points = []
        self.load_calibration()
        
        # INTEGRATION: Load the ML Model brain
        self.ml_model = None
        try:
            with open('gaze_ml_model.pkl', 'rb') as f:
                self.ml_model = pickle.load(f)
                print("✓ Successfully loaded Machine Learning Gaze Model!")
        except FileNotFoundError:
            print("⚠ ML model file 'gaze_ml_model.pkl' not found. Running raw pass-through.")

 
    
    def estimate(self, gaze_ratio_x, gaze_ratio_y, frame_width, frame_height):
        
        if self.ml_model is not None:
            # Predict screen pixel coordinates using the trained model
            prediction = self.ml_model.predict([[gaze_ratio_x, gaze_ratio_y]])
            screen_px_x = prediction[0][0]
            screen_px_y = prediction[0][1]
            
            # Normalize pixel points to a [0, 1] range relative to your screen resolution
            gaze_x = max(0.0, min(1.0, screen_px_x / 1920)) # Change to your monitor width if different
            gaze_y = max(0.0, min(1.0, screen_px_y / 1080)) # Change to your monitor height if different
        else:
            # Fallback to raw inputs if model isn't built yet
            gaze_x = gaze_ratio_x
            gaze_y = gaze_ratio_y
        
        # Apply your smoothing filter to stabilize the point
        gaze_x, gaze_y = self.smooth(gaze_x, gaze_y)
        
        return {
            "gaze_x": round(gaze_x, 4),
            "gaze_y": round(gaze_y, 4),
            "confidence": 0.95
        }

    
    def start_calibration(self, frame_width, frame_height):
        """
        Start 9-point calibration process.
        
        Call this once when user presses "Calibrate" button.
        
        Returns:
            list: [(x1, y1), (x2, y2), ..., (x9, y9)]
                  9 dots to display in 3x3 grid
        
        P4 (Frontend) will use these coordinates to show dots.
        """
        self.calibration_points = []
        
        # Create 3x3 grid of calibration points
        # Positions: quarter marks on the screen (25%, 50%, 75%)
        dots = []
        for row in range(3):
            for col in range(3):
                x = int((col + 1) * frame_width / 4)
                y = int((row + 1) * frame_height / 4)
                dots.append((x, y))
        
        print(f"Starting calibration. Show these {len(dots)} dots:")
        for i, (x, y) in enumerate(dots):
            print(f"  Dot {i+1}: ({x}, {y})")
        
        return dots

    def record_calibration_sample(self, gaze_ratio_x, gaze_ratio_y, screen_x, screen_y):
        """
        Record one calibration point.
        
        Call this after user has stared at a dot for ~1.5 seconds.
        
        Args:
            gaze_ratio_x (float): Raw gaze x from EyeExtractor
            gaze_ratio_y (float): Raw gaze y from EyeExtractor
            screen_x (int): X pixel coordinate of the dot being shown
            screen_y (int): Y pixel coordinate of the dot being shown
        """
        self.calibration_points.append((gaze_ratio_x, gaze_ratio_y, screen_x, screen_y))
        
        print(f"✓ Point {len(self.calibration_points)}/9: "
              f"Raw gaze ({gaze_ratio_x:.3f}, {gaze_ratio_y:.3f}) → "
              f"Screen ({screen_x}, {screen_y})")

    def finish_calibration(self):
        """
        Finish calibration and fit polynomial mapping.
        
        Call this after all 9 points have been recorded.
        
        Returns:
            bool: True if successful, False otherwise
        
        This saves calibration coefficients to JSON file.
        """
        if len(self.calibration_points) < 9:
            print(f"❌ Only {len(self.calibration_points)} points recorded. Need 9.")
            return False
        
        print("Computing calibration polynomial...")
        
        # Extract arrays from calibration points
        raw_x = np.array([p[0] for p in self.calibration_points])
        raw_y = np.array([p[1] for p in self.calibration_points])
        scr_x = np.array([p[2] for p in self.calibration_points])
        scr_y = np.array([p[3] for p in self.calibration_points])
        
        # Build feature matrix: [1, x, y, x^2, y^2, xy]
        # This allows a polynomial mapping with cross-terms
        F = np.column_stack([
            np.ones_like(raw_x),
            raw_x, raw_y,
            raw_x**2, raw_y**2,
            raw_x * raw_y
        ])
        
        # Fit least squares: find coefficients that map raw → screen
        # Solve separately for x and y coordinates
        try:
            self.calib_coef_x, _, _, _ = np.linalg.lstsq(F, scr_x, rcond=None)
            self.calib_coef_y, _, _, _ = np.linalg.lstsq(F, scr_y, rcond=None)
        except Exception as e:
            print(f"❌ Calibration fitting failed: {e}")
            return False
        
        # Save to JSON for persistence
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump({
                    "coef_x": self.calib_coef_x.tolist(),
                    "coef_y": self.calib_coef_y.tolist()
                }, f, indent=2)
            print(f"✓ Calibration saved to {self.calibration_file}")
        except Exception as e:
            print(f"❌ Failed to save calibration: {e}")
            return False
        
        return True

    def apply_calibration(self, raw_x, raw_y, frame_width, frame_height):
        """
        Convert raw gaze [0,1] to calibrated screen coordinates [0,1]
        using polynomial mapping learned from 9-point calibration.
        
        Args:
            raw_x (float): Raw gaze x [0, 1]
            raw_y (float): Raw gaze y [0, 1]
            frame_width (int): Video frame width
            frame_height (int): Video frame height
        
        Returns:
            (float, float): Calibrated (gaze_x, gaze_y) in [0, 1]
        """
        if self.calib_coef_x is None:
            # No calibration loaded, use raw values
            return raw_x, raw_y
        
        # Build feature vector: [1, x, y, x^2, y^2, xy]
        f = np.array([1, raw_x, raw_y, raw_x**2, raw_y**2, raw_x * raw_y])
        
        # Apply polynomial mapping
        screen_px_x = float(np.dot(self.calib_coef_x, f))
        screen_px_y = float(np.dot(self.calib_coef_y, f))
        
        # Convert pixels back to [0, 1]
        norm_x = max(0.0, min(1.0, screen_px_x / frame_width))
        norm_y = max(0.0, min(1.0, screen_px_y / frame_height))
        
        return norm_x, norm_y

    def load_calibration(self):
        """
        Load previously saved calibration coefficients from JSON file.
        
        Called automatically in __init__.
        If file doesn't exist, calibration will be None (no prior calibration).
        """
        if Path(self.calibration_file).exists():
            try:
                with open(self.calibration_file) as f:
                    data = json.load(f)
                    self.calib_coef_x = np.array(data.get("coef_x"))
                    self.calib_coef_y = np.array(data.get("coef_y"))
                    print(f"✓ Loaded calibration from {self.calibration_file}")
            except Exception as e:
                print(f"⚠ Failed to load calibration: {e}")
        else:
            print(f"⚠ No calibration file found at {self.calibration_file}")

    # ===== WEEK 2: Smoothing (Drift Correction) =====
    
    def smooth(self, gaze_x, gaze_y):
        """
        Apply exponential moving average to smooth noisy gaze data.
        
        Reduces jitter from small eye movements while maintaining responsiveness.
        
        Formula: smoothed = α × new + (1 - α) × previous
        - α = 0.3: smooth but laggy
        - α = 0.4: good balance (recommended)
        - α = 0.6: responsive but jittery
        
        Args:
            gaze_x (float): Current gaze x estimate
            gaze_y (float): Current gaze y estimate
        
        Returns:
            (float, float): Smoothed (gaze_x, gaze_y)
        """
        sx = self.alpha * gaze_x + (1 - self.alpha) * self.prev_x
        sy = self.alpha * gaze_y + (1 - self.alpha) * self.prev_y
        
        self.prev_x = sx
        self.prev_y = sy
        
        return sx, sy

    def set_smoothing_alpha(self, alpha):
        """
        Adjust smoothing strength.
        
        Args:
            alpha (float): Between 0.0 and 1.0
                - 0.1: very smooth, very laggy
                - 0.4: good balance (default)
                - 0.8: responsive but jittery
        """
        if not (0.0 <= alpha <= 1.0):
            print(f"⚠ Alpha must be between 0 and 1, got {alpha}")
            return
        self.alpha = alpha
        print(f"Smoothing alpha set to {alpha}")

    # ===== Testing & Debugging =====
    
    def get_calibration_stats(self):
        """
        Print calibration statistics (for debugging).
        
        Shows how well the polynomial fits the 9 calibration points.
        """
        if not self.calibration_points:
            print("No calibration data recorded yet.")
            return
        
        if self.calib_coef_x is None:
            print("Calibration not fitted yet.")
            return
        
        print("\nCalibration Statistics:")
        print("=" * 50)
        
        errors_px = []
        for i, (raw_x, raw_y, true_x, true_y) in enumerate(self.calibration_points):
            pred_x, pred_y = self.apply_calibration(raw_x, raw_y, 1920, 1080)
            # Convert back to pixels for error calculation
            pred_px_x = pred_x * 1920
            pred_px_y = pred_y * 1080
            
            error = np.sqrt((pred_px_x - true_x)**2 + (pred_px_y - true_y)**2)
            errors_px.append(error)
            
            print(f"Point {i+1}: Error = {error:.1f}px "
                  f"(predicted: ({pred_px_x:.0f}, {pred_px_y:.0f}), "
                  f"true: ({true_x}, {true_y}))")
        
        print(f"\nMean error: {np.mean(errors_px):.1f}px")
        print(f"Max error:  {np.max(errors_px):.1f}px")
        print("=" * 50)