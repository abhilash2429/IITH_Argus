"""
Mock response functions for all research tools.
Returns realistic hardcoded data for demo/testing without network calls.
Based on the fictional company "Sharma Textiles Pvt Ltd".
"""

from typing import Any


def mock_serper_news(query: str) -> str:
    """
    Mock Google Search news results for company research.

    Args:
        query: Search query string.

    Returns:
        Formatted news results string.
    """
    return (
        "Title: Sharma Textiles Pvt Ltd classified as NPA by HDFC Bank\n"
        "Snippet: Sharma Textiles Pvt Ltd, a mid-size textile manufacturer based in Surat, "
        "was classified as a Non-Performing Asset (NPA) by HDFC Bank in Q3 FY2023 after "
        "defaulting on a ₹4.2 Crore working capital facility.\n"
        "Link: https://economictimes.com/sharma-textiles-npa\n\n"
        "Title: DRT orders recovery proceedings against Sharma Textiles\n"
        "Snippet: The Debt Recovery Tribunal (DRT), Ahmedabad bench, has initiated recovery "
        "proceedings against Sharma Textiles Pvt Ltd following a petition by HDFC Bank. "
        "The outstanding dues including interest amount to ₹5.1 Crore.\n"
        "Link: https://livemint.com/sharma-textiles-drt\n\n"
        "Title: Textile sector faces headwinds as cotton prices surge 30%\n"
        "Snippet: Indian textile manufacturers are under severe margin pressure as raw "
        "cotton prices have surged 30% year-on-year. Industry body CITI warns of "
        "widespread working capital stress among small and mid-size players.\n"
        "Link: https://business-standard.com/textile-sector-headwinds"
    )


def mock_serper_promoter(name: str) -> str:
    """
    Mock promoter background check results.

    Args:
        name: Director/promoter name.

    Returns:
        Formatted promoter check results string.
    """
    promoter_data = {
        "Rajesh Sharma": (
            "Title: Rajesh Sharma — Clean Record\n"
            "Snippet: No adverse findings. Rajesh Sharma has been associated with "
            "Sharma Textiles since 2005. No fraud, default, or SEBI actions found.\n"
            "Status: CLEAR"
        ),
        "Priya Sharma": (
            "Title: Priya Sharma — No adverse news\n"
            "Snippet: Priya Sharma, Director at Sharma Textiles, has no fraud or "
            "default history. Active in textile industry associations.\n"
            "Status: CLEAR"
        ),
    }
    default = (
        f"Title: {name} — Background Check\n"
        f"Snippet: No significant adverse news found for {name} in Indian business databases.\n"
        "Status: CLEAR"
    )
    return promoter_data.get(name, default)


def mock_mca21(company_name: str) -> dict:
    """
    Mock MCA21 company registration data.

    Args:
        company_name: Name of the company.

    Returns:
        Dict with MCA registration details.
    """
    return {
        "cin": "U17111GJ2005PTC045678",
        "company_status": "ACTIVE",
        "incorporation_date": "2005-03-15",
        "authorized_capital_lakh": 500,
        "paid_up_capital_lakh": 350,
        "directors": [
            {"name": "Rajesh Sharma", "din": "00123456", "designation": "Managing Director"},
            {"name": "Priya Sharma", "din": "00789012", "designation": "Director"},
        ],
        "charges": [
            {"holder": "HDFC Bank", "amount_crore": 8.0, "status": "open", "date": "2020-06-15"},
            {"holder": "SBI", "amount_crore": 5.0, "status": "satisfied", "date": "2018-01-10"},
            {"holder": "ICICI Bank", "amount_crore": 3.5, "status": "open", "date": "2021-09-20"},
            {"holder": "Bajaj Finance", "amount_crore": 2.0, "status": "open", "date": "2022-03-01"},
        ],
        "charge_count": 4,
        "din_disqualified": False,
        "roc_compliance_status": "COMPLIANT",
    }


def mock_ecourts(company_name: str) -> list:
    """
    Mock eCourts litigation data.

    Args:
        company_name: Name of the company.

    Returns:
        List of case dicts.
    """
    return [
        {
            "case_number": "OA/123/2023",
            "court": "DRT Ahmedabad",
            "type": "recovery",
            "status": "pending",
            "year": 2023,
            "parties": f"HDFC Bank vs {company_name}",
            "amount_crore": 5.1,
        },
        {
            "case_number": "CS/456/2022",
            "court": "Civil Court Surat",
            "type": "civil",
            "status": "disposed",
            "year": 2022,
            "parties": f"Supplier XYZ vs {company_name}",
            "amount_crore": 0.8,
        },
    ]


def mock_rbi_alerts(sector: str) -> list:
    """
    Mock RBI/SEBI regulatory alerts for a sector.

    Args:
        sector: Industry sector name.

    Returns:
        List of regulatory alert strings.
    """
    sector_alerts = {
        "textile": [
            "RBI Circular: Banks advised to exercise caution in textile sector lending "
            "due to elevated NPAs (NPA ratio: 8.2% as of Sept 2025)",
            "CITI (Confederation of Indian Textile Industry) reports 15% capacity "
            "underutilization across mid-size textile units",
        ],
        "nbfc": [
            "RBI: Enhanced regulatory framework for NBFCs with asset size > ₹1000 Crore",
            "RBI: Scale-based regulation — upper layer NBFCs to maintain additional capital buffers",
        ],
        "real_estate": [
            "RBI: Increased risk weights on commercial real estate lending by 25%",
        ],
    }
    return sector_alerts.get(sector.lower(), [
        f"No specific RBI/SEBI alerts for {sector} sector at this time"
    ])
