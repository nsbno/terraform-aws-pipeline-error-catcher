#!/usr/bin/env python
#
# Copyright (C) 2020 Vy
#
# Distributed under terms of the MIT license.

"""
Unit tests for error-catcher Lambda
"""

from src import main


def test_should_find_error_object():
    payload = {"Error": "An error", "Cause": "Cause"}
    errors = main.get_error_objects(payload)
    assert len(errors) == 1


def test_should_find_error_object_in_list():
    payload = [{"Error": "An error", "Cause": "Cause"}]
    errors = main.get_error_objects(payload)
    assert len(errors) == len(payload)


def test_should_find_multiple_error_objects_in_list():
    payload = [{"Error": "An error", "Cause": "Cause"}, {"Error": "hello"}]
    errors = main.get_error_objects(payload)
    assert len(errors) == len(payload)


def test_should_find_error_objects_in_nested_list():
    payload = {"key": [{"Error": "An error", "Cause": "Cause"}]}
    errors = main.get_error_objects(payload)
    assert len(errors) == 1


def test_should_find_nested_error_object():
    payload = {"key": {"Error": "An error", "Cause": "Cause"}}
    errors = main.get_error_objects(payload)
    assert len(errors) == 1


def test_should_find_deeply_nested_error_object():
    payload = {
        "key": {"key": {"key": {"Error": "An error", "Cause": "Cause"}}}
    }
    errors = main.get_error_objects(payload)
    assert len(errors) == 1


def test_should_return_correct_format():
    payload = {
        "key": {"key": {"key": {"Error": "An error", "Cause": "Cause"}}}
    }
    errors = main.get_error_objects(payload)
    assert len(errors) == 1
    assert (
        len(errors[0]) == 2 and "Error" in errors[0] and "Cause" in errors[0]
    )


def test_should_find_error_object_without_cause():
    payload = {"Error": "An error"}
    errors = main.get_error_objects(payload)
    assert len(errors) == 1


def test_should_ignore_invalid_error_object():
    payload = {"Errors": ""}
    errors = main.get_error_objects(payload)
    assert len(errors) == 0


def test_should_ignore_error_object_with_invalid_types():
    payload = {"Error": 1234}
    errors = main.get_error_objects(payload)
    assert len(errors) == 0
