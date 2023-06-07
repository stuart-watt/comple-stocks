"""Unit tests for the stock scraper service"""

import pytest

from stock_scraper.main import get_listed_companies

def test_get_listed_companies(asx_registry_url: str):
    """Test that the function returns a dataframe with more than 0 rows"""
    df = get_listed_companies(asx_registry_url)

    assert len(df) > 0
