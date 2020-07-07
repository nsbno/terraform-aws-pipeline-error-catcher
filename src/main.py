#!/usr/bin/env python
#
# Copyright (C) 2020 Erlend Ekern <dev@ekern.me>
#
# Distributed under terms of the MIT license.

"""

"""
import logging
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_errors(json_input, error_key):
    errors = []
    for element in json_input:
        if error_key and all(key in element.get(error_key, {}) for key in ["Error", "Cause"]):
            error = element[error_key]
        elif all(key in element for key in ["Error", "Cause"]):
            error = element
        else:
            continue
        errors.append(error)
    return errors


def lambda_handler(event, context):
    logger.info("Lambda triggered with event '%s'", event)
    token = event["token"]
    fail_on_errors = event.get("fail_on_errors", True)
    error_key = event.get("error_key", "")
    json_input = event["input"]

    client = boto3.client("stepfunctions")
    if not isinstance(json_input, list):
        raise ValueError(
            f"Expected the input to be a list containing the outputs of each branch in a parallel state, but got type '{type(json_input)}'"
        )

    errors = get_errors(json_input, error_key)
    logger.info("Found errors %s", errors)

    if fail_on_errors and len(errors):
        error_codes = "|".join(error["Error"] for error in errors)
        cause = (
            "Multiple states failed" if len(errors) > 1 else errors[0]["Cause"]
        )
        client.send_task_failure(
            error=error_codes, cause=cause, taskToken=token,
        )
    else:
        output = True if len(errors) else False
        client.send_task_success(taskToken=token, output=json.dumps(output))
