"""
Synthetic data generator for Indian corporate credit training data.
Generates 500 realistic cases with features matching the ML calibrator.
Uses numpy seed=42 for reproducibility.

Label: 1 (stress) if DSCR < 1.2 OR has_recovery_suit OR gst_mismatch > 30 OR promoter_red_flag
"""

import os
import numpy as np
import pandas as pd


def generate_synthetic_data(n_samples: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic Indian corporate credit data.

    Args:
        n_samples: Number of samples to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with all features and binary stress label.
    """
    np.random.seed(seed)

    data = {
        "dscr": np.clip(np.random.normal(1.5, 0.6, n_samples), 0.3, 4.0),
        "ebitda_margin_pct": np.clip(np.random.normal(12, 6, n_samples), -5, 35),
        "current_ratio": np.clip(np.random.normal(1.5, 0.5, n_samples), 0.3, 4.0),
        "debt_to_equity": np.clip(np.random.exponential(1.5, n_samples), 0.1, 10.0),
        "revenue_growth_yoy": np.random.normal(0.05, 0.15, n_samples),
        "gst_bank_mismatch_pct": np.clip(np.random.exponential(10, n_samples), 0, 80),
        "active_litigation_count": np.random.poisson(1.0, n_samples),
        "promoter_red_flag": np.random.binomial(1, 0.12, n_samples),
        "factory_capacity_pct": np.clip(np.random.normal(70, 15, n_samples), 20, 100),
        "auditor_qualified": np.random.binomial(1, 0.15, n_samples),
        "charge_count": np.random.poisson(2.5, n_samples),
        "bounced_cheques_12m": np.random.poisson(1.0, n_samples),
        "sector_risk_index": np.random.choice([2, 3, 4, 5, 6, 7, 8, 9], n_samples,
                                              p=[0.08, 0.12, 0.15, 0.20, 0.15, 0.12, 0.10, 0.08]),
    }

    df = pd.DataFrame(data)

    # Generate has_recovery_suit (correlated with litigation count)
    df["has_recovery_suit"] = ((df["active_litigation_count"] >= 2) &
                               (np.random.random(n_samples) > 0.6)).astype(int)

    # Label: stress = 1 if any critical condition met
    df["stress_label"] = (
        (df["dscr"] < 1.2) |
        (df["has_recovery_suit"] == 1) |
        (df["gst_bank_mismatch_pct"] > 30) |
        (df["promoter_red_flag"] == 1)
    ).astype(int)

    return df


def main():
    """Generate and save synthetic credit data."""
    df = generate_synthetic_data(500)

    # Save to CSV
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "synthetic_credit_data.csv")
    df.to_csv(output_path, index=False)

    # Print statistics
    print(f"✅ Generated {len(df)} synthetic credit cases")
    print(f"   Saved to: {output_path}")
    print(f"\n   Class balance:")
    print(f"   - Healthy (0): {(df['stress_label'] == 0).sum()} ({(df['stress_label'] == 0).mean():.1%})")
    print(f"   - Stress  (1): {(df['stress_label'] == 1).sum()} ({(df['stress_label'] == 1).mean():.1%})")
    print(f"\n   Feature stats:")
    print(df.describe().round(2).to_string())


if __name__ == "__main__":
    main()
