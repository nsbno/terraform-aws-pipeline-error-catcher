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


def get_error_objects(obj):
    """Recursively scan a dictionary or a list and return a list of objects that look like AWS Step Functions error objects.

    An object is considered an error object iff it contains only an `Error` key, or both an `Error` and `Cause` key.

    """
    results = []
    if isinstance(obj, list):
        for item in obj:
            results += get_error_objects(item)
    elif isinstance(obj, dict):
        if ("Error" in obj and "Cause" in obj and len(obj) == 2) or (
            "Error" in obj and len(obj) == 1
        ):
            error_obj = {
                "Error": obj["Error"],
                "Cause": obj.get("Cause", "Unknown cause"),
            }
            if all(isinstance(val, str) for key, val in error_obj.items()):
                results.append(
                    {
                        "Error": obj["Error"],
                        "Cause": obj.get("Cause", "Unknown cause"),
                    }
                )
        else:
            for key, val in obj.items():
                results += get_error_objects(val)
    return results


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
