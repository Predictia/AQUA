"""Tests for string unit conversion utilities"""

import pytest
from aqua.core.util.string import unit_to_latex

@pytest.mark.aqua
@pytest.mark.parametrize("input_str, expected", [
    # Basic cases
    ("m", "m"),
    ("kg", "kg"),
    ("s", "s"),
    
    # Simple exponents (explicit and implicit)
    ("m^2", "m^{2}"),
    ("m**2", "m^{2}"),
    ("m2", "m^{2}"),
    ("m-2", "m^{-2}"),
    ("m^-2", "m^{-2}"),
    ("m**-2", "m^{-2}"),
    
    # Division notation
    ("W/m^2", "W m^{-2}"),
    ("m/s", "m s^{-1}"),
    ("kg/m/s", "kg m^{-1} s^{-1}"),
    ("J/kg/K", "J kg^{-1} K^{-1}"),
    
    # Grouped division
    ("W/(m^2 s)", "W m^{-2} s^{-1}"),
    ("kg/(m s^2)", "kg m^{-1} s^{-2}"),
    
    # Mixed notation
    ("kg m-1 s-1", "kg m^{-1} s^{-1}"),
    ("kg m^-1 s^-1", "kg m^{-1} s^{-1}"),
    ("kg m**-1 s**-1", "kg m^{-1} s^{-1}"),
    
    # Special characters
    ("°C", "°C"),
    ("µg m^-3", "µg m^{-3}"),
    ("µg/m^3", "µg m^{-3}"),
    
    # Edge cases
    ("", ""),
    (None, None),
    ("   ", ""),
    ("m/s/s", "m s^{-1} s^{-1}"),  # Repeated division
    
    # Already LaTeX (should be preserved)
    ("$\\mathrm{km}^2$", "$\\mathrm{km}^2$"),
    ("10^6 $\\mathrm{km}^2$", "10^6 $\\mathrm{km}^2$"),
    (r"$\mathrm{W} \mathrm{m}^{-2}$", r"$\mathrm{W} \mathrm{m}^{-2}$"),
    ("m^{2}", "m^{2}"), # Partial LaTeX
])
def test_unit_to_latex(input_str, expected):
    """Test unit_to_latex with various input formats"""
    assert unit_to_latex(input_str) == expected

@pytest.mark.aqua
def test_unit_to_latex_complex():
    """Test more complex combinations"""
    # Test complex mixed format
    assert unit_to_latex("W m-2 K-1") == "W m^{-2} K^{-1}"
    
    # Test complex division with implicit exponents
    assert unit_to_latex("kg/m3") == "kg m^{-3}"
    
    # Test with extra spaces
    assert unit_to_latex(" W /  m^2 ") == "W m^{-2}"

