data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  current_account_id = data.aws_caller_identity.current.account_id
  current_region     = data.aws_region.current.name
}

data "archive_file" "this" {
  type        = "zip"
  source_file = "${path.module}/src/main.py"
  output_path = "${path.module}/src/main.zip"
}

resource "aws_lambda_function" "this" {
  function_name    = "${var.name_prefix}-pipeline-error-catcher"
  handler          = "main.lambda_handler"
  role             = aws_iam_role.this.arn
  runtime          = "python3.7"
  filename         = data.archive_file.this.output_path
  source_code_hash = filebase64sha256(data.archive_file.this.output_path)
  tags             = var.tags
}

resource "aws_iam_role" "this" {
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy" "logs_to_lambda" {
  policy = data.aws_iam_policy_document.logs_for_lambda.json
  role   = aws_iam_role.this.id
}

resource "aws_iam_role_policy" "task_status_to_lambda" {
  policy = data.aws_iam_policy_document.task_status_for_lambda.json
  role   = aws_iam_role.this.id
}
