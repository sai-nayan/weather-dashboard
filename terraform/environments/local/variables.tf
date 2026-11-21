variable "docker_host" {
  description = "Docker daemon socket address"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "weather-dashboard"
}

variable "environment" {
  description = "Target deployment environment (local, dev, staging, prod)"
  type        = string
  default     = "local"
}

variable "container_image_tag" {
  description = "Tag for the application image"
  type        = string
  default     = "terraform-latest"
}

variable "host_port" {
  description = "Port on host to expose the application"
  type        = number
  default     = 5053
}

variable "container_port" {
  description = "Port the application listens on inside the container"
  type        = number
  default     = 5050
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  default     = "terraform-local-super-secret-key"
  sensitive   = true
}

variable "restart_policy" {
  description = "Docker container restart policy"
  type        = string
  default     = "unless-stopped"
}
