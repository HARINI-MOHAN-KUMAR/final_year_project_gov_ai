"""
Random Forest Recommendation Model for GovGuide AI.

This module handles:
1. Generating synthetic training profiles
2. Training the Random Forest model
3. Predicting match scores for user-scheme pairs
4. Providing SHAP-style feature importance

The model learns to rank schemes beyond simple rule matching,
capturing soft preferences from training data patterns.
"""

import json
import logging
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import LabelEncoder

from app.ml.eligibility_engine import get_schemes, check_scheme_eligibility

logger = logging.getLogger(__name__)

# ── Feature Engineering ──────────────────────────────────────────────────────

CATEGORY_MAP = {"SC": 0, "ST": 1, "OBC": 2, "EWS": 3, "General": 4}
GENDER_MAP = {"male": 0, "female": 1, "other": 2}
EDUCATION_MAP = {
    "illiterate": 0, "class_8_pass": 1, "class_9": 2, "class_10": 3,
    "class_11": 4, "class_12": 5, "diploma": 6, "graduate": 7,
    "postgraduate": 8, "mphil": 9, "phd": 10, "dropout": 2,
}
OCCUPATION_MAP = {
    "farmer": 0, "laborer": 1, "employee": 2, "self_employed": 3,
    "entrepreneur": 4, "student": 5, "unorganized_worker": 6, "artisan": 7,
    "craftsperson": 8, "small_business": 9, "retired": 10, "unemployed": 11,
    "housewife": 12,
}
RESIDENCE_MAP = {"rural": 0, "urban": 1}
MARITAL_MAP = {"single": 0, "married": 1, "widow": 2, "widower": 3, "divorced": 4, "separated": 5}

FEATURE_NAMES = [
    "age", "gender_enc", "income_log", "education_enc", "occupation_enc",
    "category_enc", "disability", "marital_enc", "residence_enc",
    "land_holding", "bank_account", "disability_pct",
]


def profile_to_features(profile: Dict) -> np.ndarray:
    """Convert a profile dict to a fixed-length numeric feature vector."""
    age = profile.get("age") or 30
    gender = GENDER_MAP.get(profile.get("gender", "male"), 0)
    income = profile.get("annual_income") or 100000
    income_log = np.log1p(income)
    education = EDUCATION_MAP.get(profile.get("education", "class_10"), 3)
    occupation = OCCUPATION_MAP.get(profile.get("occupation", "laborer"), 1)
    category = CATEGORY_MAP.get(profile.get("category", "General"), 4)
    disability = int(profile.get("disability") or False)
    marital = MARITAL_MAP.get(profile.get("marital_status", "single"), 0)
    residence = RESIDENCE_MAP.get(profile.get("residence", "rural"), 0)
    land = int(profile.get("land_holding") or False)
    bank = int(profile.get("bank_account") or True)
    dis_pct = profile.get("disability_percentage") or 0

    return np.array([
        age, gender, income_log, education, occupation, category,
        disability, marital, residence, land, bank, dis_pct,
    ], dtype=float)


# ── Synthetic Data Generation ─────────────────────────────────────────────────

def generate_synthetic_profiles(n: int = 5000, seed: int = 42) -> List[Dict]:
    """Generate diverse synthetic user profiles for training."""
    random.seed(seed)
    np.random.seed(seed)

    profiles = []
    states = [
        "Tamil Nadu", "Maharashtra", "Karnataka", "Uttar Pradesh",
        "Bihar", "West Bengal", "Rajasthan", "Madhya Pradesh", "Gujarat", "All India",
    ]
    for _ in range(n):
        profile = {
            "age": int(np.random.randint(14, 80)),
            "gender": random.choice(["male", "female", "other"]),
            "annual_income": float(np.random.lognormal(mean=11.0, sigma=0.8)),
            "education": random.choice(list(EDUCATION_MAP.keys())),
            "occupation": random.choice(list(OCCUPATION_MAP.keys())),
            "category": random.choice(["SC", "ST", "OBC", "EWS", "General"]),
            "state": random.choice(states),
            "disability": random.random() < 0.08,
            "disability_percentage": int(np.random.randint(0, 100)),
            "marital_status": random.choice(["single", "married", "widow", "divorced"]),
            "residence": random.choice(["rural", "urban"]),
            "land_holding": random.random() < 0.3,
            "bank_account": random.random() < 0.85,
            "family_head": random.random() < 0.4,
        }
        profile["annual_income"] = round(min(profile["annual_income"], 5000000), 2)
        profiles.append(profile)

    return profiles


def build_training_dataset(profiles: List[Dict], schemes: List[Dict]) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Build (X, y) for training.
    Each row = (profile_features + scheme_category_enc), label = 1 if eligible else 0.
    """
    X_rows, y_rows = [], []

    scheme_cat_map = {}
    scheme_cats = list(set(s["category"] for s in schemes))
    for i, cat in enumerate(scheme_cats):
        scheme_cat_map[cat] = i

    for profile in profiles:
        p_features = profile_to_features(profile)
        for scheme in schemes:
            _, criteria = check_scheme_eligibility(profile, scheme)
            label = int(all(c["passed"] for c in criteria.values()))
            scheme_cat_enc = scheme_cat_map.get(scheme["category"], 0)
            # Append scheme category as extra feature
            row = np.append(p_features, scheme_cat_enc)
            X_rows.append(row)
            y_rows.append(label)

    feature_names_ext = FEATURE_NAMES + ["scheme_category_enc"]
    X = pd.DataFrame(X_rows, columns=feature_names_ext)
    y = pd.Series(y_rows, name="eligible")
    return X, y


# ── Model Training ────────────────────────────────────────────────────────────

class GovGuideRecommender:
    """Random Forest-based scheme recommender with explainability."""

    def __init__(self):
        self.model: Optional[RandomForestClassifier] = None
        self.scheme_cat_map: Dict[str, int] = {}
        self.feature_names: List[str] = FEATURE_NAMES + ["scheme_category_enc"]
        self._model_path = Path(os.environ.get("ML_MODEL_PATH", "./data/rf_model.joblib"))

    def train(self, profiles: List[Dict], schemes: List[Dict]) -> Dict:
        """Train Random Forest and return metrics."""
        logger.info("Building training dataset...")
        X, y = build_training_dataset(profiles, schemes)

        # Build scheme category map
        self.scheme_cat_map = {
            cat: i for i, cat in enumerate(set(s["category"] for s in schemes))
        }

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...")

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        logger.info(f"Training complete. Accuracy={metrics['accuracy']:.4f}")
        return metrics

    def predict_score(self, profile: Dict, scheme: Dict) -> float:
        """Return probability of eligibility (0–1) for a profile-scheme pair."""
        if self.model is None:
            return 0.5  # fallback

        p_features = profile_to_features(profile)
        cat_enc = self.scheme_cat_map.get(scheme.get("category", ""), 0)
        row = np.append(p_features, cat_enc).reshape(1, -1)
        proba = self.model.predict_proba(row)[0]
        # proba[1] = probability of class 1 (eligible)
        return float(proba[1]) if len(proba) > 1 else float(proba[0])

    def get_feature_importance(self, profile: Dict, scheme: Dict) -> Dict[str, float]:
        """Return SHAP-style feature importance for this prediction."""
        if self.model is None:
            return {}

        importances = self.model.feature_importances_
        return {
            name: round(float(imp), 4)
            for name, imp in zip(self.feature_names, importances)
        }

    def save(self):
        """Persist model to disk."""
        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "scheme_cat_map": self.scheme_cat_map}, self._model_path)
        logger.info(f"Model saved to {self._model_path}")

    def load(self) -> bool:
        """Load model from disk. Returns True if successful."""
        if not self._model_path.exists():
            logger.warning(f"Model file not found at {self._model_path}. Using rule-only mode.")
            return False
        data = joblib.load(self._model_path)
        self.model = data["model"]
        self.scheme_cat_map = data["scheme_cat_map"]
        logger.info(f"Model loaded from {self._model_path}")
        return True


# ── Singleton Recommender ─────────────────────────────────────────────────────

_recommender: Optional[GovGuideRecommender] = None


def get_recommender() -> GovGuideRecommender:
    """Return (or lazily initialize) the singleton recommender."""
    global _recommender
    if _recommender is None:
        _recommender = GovGuideRecommender()
        _recommender.load()  # Load pre-trained model if available
    return _recommender
