"""
Training script for the GovGuide AI Random Forest recommender.

Run this script to generate synthetic data and train the model:
    cd backend
    python -m app.ml.train
"""

import logging
import sys
from pathlib import Path

# Ensure backend is on the path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ml.recommender import (
    GovGuideRecommender,
    generate_synthetic_profiles,
)
from app.ml.eligibility_engine import get_schemes

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("GovGuide AI – Model Training Script")
    logger.info("=" * 60)

    # 1. Load schemes
    schemes = get_schemes()
    logger.info(f"Loaded {len(schemes)} schemes")

    # 2. Generate synthetic profiles
    logger.info("Generating 3000 synthetic user profiles...")
    profiles = generate_synthetic_profiles(n=3000, seed=42)
    logger.info(f"Generated {len(profiles)} profiles")

    # 3. Save profiles as CSV for reference
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_profiles.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(profiles).to_csv(csv_path, index=False)
    logger.info(f"Saved synthetic profiles to {csv_path}")

    # 4. Train model
    recommender = GovGuideRecommender()
    logger.info("Training Random Forest model...")
    metrics = recommender.train(profiles, schemes)

    # 5. Display metrics
    logger.info("=" * 60)
    logger.info("Training Results:")
    logger.info(f"  Accuracy  : {metrics['accuracy']:.4f}")
    logger.info(f"  Precision : {metrics['precision']:.4f}")
    logger.info(f"  Recall    : {metrics['recall']:.4f}")
    logger.info("  Confusion Matrix:")
    for row in metrics["confusion_matrix"]:
        logger.info(f"    {row}")
    logger.info("  Classification Report:")
    for line in metrics["classification_report"].split("\n"):
        if line.strip():
            logger.info(f"    {line}")
    logger.info("=" * 60)

    # 6. Save model
    recommender.save()
    logger.info("✅ Model training complete!")

    return metrics


if __name__ == "__main__":
    main()
