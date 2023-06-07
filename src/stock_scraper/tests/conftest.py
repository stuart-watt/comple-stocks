"""Conftest for stock_scraper tests."""

import pytest

@pytest.fixture
def asx_registry_url() -> str:
    """Fixture to return the ASX registry url"""
    return "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"
