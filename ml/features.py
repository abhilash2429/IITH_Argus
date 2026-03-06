"""
Feature engineering module for credit risk ML model.
Transforms raw DataFrame columns to match the extract_ml_features() logic
in the backend scoring module.
"""

import pandas as pd
import numpy as np

FEATURE_NAMES = [
    "dscr",                    # Debt Service Coverage Ratio — core repayment capacity metric
    "ebitda_margin_pct",       # EBITDA margin — operational profitability indicator
    "current_ratio",           # Current assets / current liabilities — liquidity measure
    "debt_to_equity",          # Total debt / net worth — leverage indicator
    "revenue_growth_yoy",      # Year-on-year revenue growth — business momentum
    "gst_bank_mismatch_pct",   # GST vs bank mismatch — revenue inflation signal
    "active_litigation_count", # Number of active court cases — legal risk proxy
    "promoter_red_flag",       # Binary: promoter has fraud/default history
    "factory_capacity_pct",    # Factory utilization — operational efficiency
    "auditor_qualified",       # Binary: auditor gave qualified/adverse opinion
    "charge_count",            # Number of MCA registered charges — asset pledging level
    "bounced_cheques_12m",     # Bounced cheques in 12 months — banking conduct
    "sector_risk_index",       # Sector-specific risk rating (0-10)
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw DataFrame to feature matrix for ML training.

    Args:
        df: Raw DataFrame with all columns.

    Returns:
        DataFrame with exactly the FEATURE_NAMES columns.
    """
    feature_df = pd.DataFrame()

    for name in FEATURE_NAMES:
        if name in df.columns:
            feature_df[name] = df[name].fillna(0).astype(float)
        else:
            feature_df[name] = 0.0

    return feature_df


def get_feature_names() -> list:
    """
    Return the ordered list of feature names.

    Returns:
        List of 13 feature name strings.
    """
    return FEATURE_NAMES.copy()
