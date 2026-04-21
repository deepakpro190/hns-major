import torch
import torch.nn as nn
import numpy as np
import joblib

# =========================
# 🟡 LOAD XGBOOST MODELS
# =========================
xgb_storage = joblib.load("services/xgb_storage.pkl")
xgb_transport = joblib.load("services/xgb_transport.pkl")


def predict_storage(features):
    """
    features shape: [[temp_avg, temp_max, temp_min, temp_var,
                      humidity_avg, door_open_count,
                      excursion_time, thermal_stress]]
    """
    features = np.array(features)
    probs = xgb_storage.predict_proba(features)
    return float(probs[0][2])  # class 2 = CRITICAL


def predict_transport(features):
    """
    transport-level features
    """
    features = np.array(features)
    probs = xgb_transport.predict_proba(features)
    return float(probs[0][2])


# =========================
# 🔵 LSTM MODEL (TRANSPORT TREND)
# =========================
class LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(3, 64, 2, batch_first=True)
        self.fc = nn.Linear(64, 3)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


# Load LSTM
lstm_model = LSTM()
lstm_model.load_state_dict(
    torch.load("services/lstm_storage.pth", map_location="cpu")
)
lstm_model.eval()


def predict_lstm(sequence):
    """
    sequence shape: [[temp, humidity, door] x 12 timesteps]
    """
    x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        out = lstm_model(x)
        probs = torch.softmax(out, dim=1)

    return float(torch.max(probs))


# =========================
# 🧠 EXPLAINABILITY (XGB BASED)
# =========================
def explain_prediction(features):
    """
    simple feature importance using XGB feature importance
    """
    importances = xgb_storage.feature_importances_

    names = [
        "temp_avg", "temp_max", "temp_min", "temp_var",
        "humidity", "door", "excursion", "stress"
    ]

    explanation = {
        names[i]: float(importances[i])
        for i in range(len(names))
    }

    return explanation