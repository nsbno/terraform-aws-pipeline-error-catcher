## terraform-aws-pipeline-error-catcher
A Terraform module that creates a Lambda function that can be used inside an AWS Step Function to check if any errors occured in a previous parallel state. One of the inputs to the Lambda, `fail_on_errors`, determines if the Lambda should stop the Step Function execution if an error has occured, or if it simply should return a boolean.

## Lambda inputs

#### `input` (required)
A list of outputs from a set of branches in a parallel state.

#### `token` (required)
A Step Function token used to report back success or failure.

#### `error_key` (optional)
If `error_key` is set, the Lambda expects each element in the `input` list to expose its error object under the given key. If no such key is provided, the Lambda expects each list element to be an error object.

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
                "ResultPath": "$.errors",
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
                "ResultPath": "$.errors",
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
      "Comment": "Check if previous any errors were catched in a previous parallel state",
      "Type": "Task",
      "ResultPath": "$.errors_found",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "pipeline-error-catcher",
        "Payload":  {
          "token.$": "$$.Task.Token",
          "input.$": "$.result",
          "fail_on_errors": true,
          "error_key": "errors"
        }
      },
      "End": true
    }
  }
}
```
