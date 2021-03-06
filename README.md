## terraform-aws-pipeline-error-catcher
A Terraform module that creates a Lambda function that can be used inside an AWS Step Function to check if any errors occured in one or more previous states. The Lambda function scans JSON input for AWS Step Functions error objects -- objects containing only an `Error` key or both an `Error` and `Cause` key.

One of the inputs to the Lambda, `fail_on_errors`, determines if the Lambda should stop the Step Function execution if an error has occured, or if it simply should return a boolean.

## Lambda inputs

#### `input` (required)
A JSON list or object that contains outputs from previous states. This is where the Lambda will look for error objects.

#### `token` (required)
A Step Function token used to report back success or failure.

#### `fail_on_errors` (optional)
By default, the error catching state will fail if any errors are found in the `input` variable. This can be disabled by setting `fail_on_errors` to `false`, in which the state will report success and output a boolean reflecting if errors were found or not.

## Example
Add the module to your Terraform code:
```terraform
module "error_catcher" {
  source             = "github.com/nsbno/terraform-aws-pipeline-error-catcher"
  state_machine_arns = ["<state-machine-arn>"]
  name_prefix        = "<name-prefix>"
}
```
A minimal example of a state machine definition that uses the Lambda function created by the module:

```json
{
  "Comment": "Example of error catching for parallel states",
  "StartAt": "Parallel State",
  "States": {
    "Parallel State": {
      "Comment": "A parallel state",
      "Type": "Parallel",
      "Next": "Check for Errors",
      "ResultPath": "$.result",
      "Branches": [
        {
          "StartAt": "Do Stuff (Branch 1)",
          "States": {
            "Do Stuff (Branch 1)": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
              "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "Catch Errors (Branch 1)"
              }],
              "Parameters": {
                "FunctionName": "name-of-a-lambda-function",
                "Payload": {}
              },
              "End": true
            },
            "Catch Errors (Branch 1)": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "Do Stuff (Branch 2)",
          "States": {
            "Do Stuff (Branch 2)": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
              "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "Catch Errors (Branch 2)"
              }],
              "Parameters": {
                "FunctionName": "name-of-a-lambda-function",
                "Payload": {}
              },
              "End": true
            },
            "Catch Errors (Branch 2)": {
              "Type": "Pass",
              "End": true
            }
          }
        }
      ]
    },
    "Check for Errors":{
      "Comment": "Check if previous any errors were catched in a previous state",
      "Type": "Task",
      "ResultPath": "$.errors_found",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "pipeline-error-catcher",
        "Payload":  {
          "token.$": "$$.Task.Token",
          "input.$": "$.result",
          "fail_on_errors": true
        }
      },
      "End": true
    }
  }
}
```
