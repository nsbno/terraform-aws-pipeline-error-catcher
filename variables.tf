variable "name_prefix" {
  description = "A prefix used for naming resources."
  type        = string
}

variable "state_machine_arns" {
  description = "ARNs of state machines to report metrics on"
  type        = list(string)
}

variable "tags" {
  description = "A map of tags (key-value pairs) passed to resources."
  type        = map(string)
  default     = {}
}
