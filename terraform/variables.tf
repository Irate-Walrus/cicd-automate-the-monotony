variable "resource_group_location" {
  default     = "Australia Southeast"
  description = "Location of the resource group"
  type        = string
}

variable "environment" {
  default     = "dev"
  description = "Name of azure environment"
  type        = string
}

variable "project_name" {
  default     = "todo"
  description = "Name of project."
  type        = string
}

variable "container_registry" {
  description = "Container registry url."
  type        = string
}

variable "container_registry_user" {
  description = "Container registry user."
  type        = string
  sensitive   = true
}

variable "container_registry_password" {
  description = "Password of container registry user."
  type        = string
  sensitive   = true
}