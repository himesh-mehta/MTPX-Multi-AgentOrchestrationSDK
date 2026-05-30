"""Tests for calculator.py — the standalone calculator module."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from calculator import (
    OPERATIONS,
    add,
    calculate,
    divide,
    floor_divide,
    modulo,
    multiply,
    power,
    subtract,
)


# ── Basic arithmetic ──────────────────────────────────────────────

class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -4) == -5

    def test_zero(self):
        assert add(0, 0) == 0

    def test_floats(self):
        assert add(1.5, 2.5) == 4.0


class TestSubtract:
    def test_basic(self):
        assert subtract(10, 4) == 6

    def test_negative_result(self):
        assert subtract(3, 7) == -4

    def test_zero(self):
        assert subtract(5, 5) == 0


class TestMultiply:
    def test_basic(self):
        assert multiply(3, 4) == 12

    def test_by_zero(self):
        assert multiply(99, 0) == 0

    def test_negative(self):
        assert multiply(-2, 5) == -10

    def test_floats(self):
        assert multiply(2.5, 4) == 10.0


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5.0

    def test_float_result(self):
        assert divide(7, 2) == 3.5

    def test_division_by_zero(self):
        assert divide(5, 0) == "Error: Division by zero!"

    def test_negative(self):
        assert divide(-10, 2) == -5.0


class TestPower:
    def test_basic(self):
        assert power(2, 3) == 8

    def test_zero_exponent(self):
        assert power(5, 0) == 1

    def test_negative_exponent(self):
        assert power(2, -1) == 0.5


class TestModulo:
    def test_basic(self):
        assert modulo(10, 3) == 1

    def test_even_division(self):
        assert modulo(10, 5) == 0

    def test_modulo_by_zero(self):
        assert modulo(5, 0) == "Error: Division by zero!"


class TestFloorDivide:
    def test_basic(self):
        assert floor_divide(7, 2) == 3

    def test_negative(self):
        assert floor_divide(-7, 2) == -4

    def test_floor_divide_by_zero(self):
        assert floor_divide(5, 0) == "Error: Division by zero!"


# ── OPERATIONS mapping ────────────────────────────────────────────

class TestOperationsMap:
    def test_all_operators_present(self):
        expected = {"+", "-", "*", "/", "**", "%", "//"}
        assert set(OPERATIONS.keys()) == expected

    def test_each_operator_maps_to_correct_function(self):
        assert OPERATIONS["+"] is add
        assert OPERATIONS["-"] is subtract
        assert OPERATIONS["*"] is multiply
        assert OPERATIONS["/"] is divide
        assert OPERATIONS["**"] is power
        assert OPERATIONS["%"] is modulo
        assert OPERATIONS["//"] is floor_divide


# ── calculate() dispatcher ────────────────────────────────────────

class TestCalculate:
    def test_addition(self):
        assert calculate(3, "+", 4) == 7

    def test_subtraction(self):
        assert calculate(10, "-", 3) == 7

    def test_multiplication(self):
        assert calculate(6, "*", 7) == 42

    def test_division(self):
        assert calculate(15, "/", 3) == 5.0

    def test_power(self):
        assert calculate(2, "**", 10) == 1024

    def test_modulo(self):
        assert calculate(17, "%", 5) == 2

    def test_floor_division(self):
        assert calculate(17, "//", 5) == 3

    def test_unknown_operator(self):
        result = calculate(1, "^", 2)
        assert "Error" in result
        assert "^" in result

    def test_division_by_zero_via_calculate(self):
        assert calculate(5, "/", 0) == "Error: Division by zero!"

    def test_modulo_by_zero_via_calculate(self):
        assert calculate(5, "%", 0) == "Error: Division by zero!"

    def test_floor_divide_by_zero_via_calculate(self):
        assert calculate(5, "//", 0) == "Error: Division by zero!"

    def test_float_inputs(self):
        assert calculate(1.5, "+", 2.5) == 4.0

    def test_large_numbers(self):
        assert calculate(10**10, "+", 10**10) == 2 * 10**10
