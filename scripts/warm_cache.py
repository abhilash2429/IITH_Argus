"""
Cache warming script for Intelli-Credit research tools.
Pre-fetches live data from all research sources and saves to local cache.
Run this before a demo to ensure cached data is available.

Usage:
    python scripts/warm_cache.py --company "Sharma Textiles Pvt Ltd" --sector textile
    python scripts/warm_cache.py --company "ABC Corp" --sector nbfc --directors "John Doe" "Jane Smith"
"""

import os
import sys
import argparse
import logging

# Force live mode before any imports
os.environ["RESEARCH_MODE"] = "live"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("warm_cache")


def warm_cache(company_name: str, sector: str, directors: list) -> None:
    """
    Warm the research cache by calling all 5 research sources live.

    Args:
        company_name: Name of the company to research.
        sector: Industry sector.
        directors: List of director names to check.
    """
    from backend.agents.tools.research_fallback_chain import (
        fetch_company_news,
        fetch_promoter_background,
        fetch_mca_data,
        fetch_litigation,
        fetch_rbi_alerts,
    )

    print(f"\n{'='*60}")
    print(f"  INTELLI-CREDIT Cache Warmer")
    print(f"  Company: {company_name}")
    print(f"  Sector:  {sector}")
    print(f"  Directors: {', '.join(directors) if directors else 'None'}")
    print(f"{'='*60}\n")

    # 1. Company news
    print("📰 Fetching company news...")
    try:
        news = fetch_company_news(company_name, sector)
        print(f"   ✅ News cached ({len(str(news))} chars)")
    except Exception as e:
        print(f"   ❌ News failed: {e}")

    # 2. MCA data
    print("🏛️  Fetching MCA21 data...")
    try:
        mca = fetch_mca_data(company_name)
        print(f"   ✅ MCA data cached ({len(str(mca))} chars)")
    except Exception as e:
        print(f"   ❌ MCA failed: {e}")

    # 3. Litigation
    print("⚖️  Fetching litigation data...")
    try:
        lit = fetch_litigation(company_name)
        print(f"   ✅ Litigation cached ({len(lit)} cases)")
    except Exception as e:
        print(f"   ❌ Litigation failed: {e}")

    # 4. RBI alerts
    print("🏦 Fetching RBI alerts...")
    try:
        rbi = fetch_rbi_alerts(sector)
        print(f"   ✅ RBI alerts cached ({len(rbi)} alerts)")
    except Exception as e:
        print(f"   ❌ RBI alerts failed: {e}")

    # 5. Promoter background
    for director in directors:
        print(f"👤 Checking promoter: {director}...")
        try:
            bg = fetch_promoter_background(director, company_name)
            print(f"   ✅ {director} cached ({len(str(bg))} chars)")
        except Exception as e:
            print(f"   ❌ {director} failed: {e}")

    print(f"\n{'='*60}")
    print("  Cache warming complete! ✅")
    print(f"  Cache directory: {os.environ.get('CACHE_DIR', './cache')}")
    print(f"{'='*60}\n")


def main():
    """CLI entry point for cache warming."""
    parser = argparse.ArgumentParser(
        description="Warm the Intelli-Credit research cache"
    )
    parser.add_argument(
        "--company", required=True, help="Company name to research"
    )
    parser.add_argument(
        "--sector", default="textile", help="Industry sector (default: textile)"
    )
    parser.add_argument(
        "--directors", nargs="*", default=[], help="Director names to check"
    )

    args = parser.parse_args()
    warm_cache(args.company, args.sector, args.directors)


if __name__ == "__main__":
    main()
