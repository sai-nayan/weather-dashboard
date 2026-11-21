output "container_id" {
  description = "The ID of the deployed container"
  value       = docker_container.weather_dashboard.id
}

output "container_name" {
  description = "Name of the running container"
  value       = docker_container.weather_dashboard.name
}

output "network_name" {
  description = "Docker network name"
  value       = docker_network.weather_net.name
}

output "data_volume_name" {
  description = "Name of persistent data volume"
  value       = docker_volume.weather_data.name
}

output "application_url" {
  description = "Local endpoint URL for the application"
  value       = "http://localhost:${var.host_port}"
}

output "health_check_url" {
  description = "Application health check endpoint"
  value       = "http://localhost:${var.host_port}/health"
}
