output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "application_endpoint" {
  description = "Application access URL"
  value       = "http://${aws_lb.main.dns_name}"
}

output "health_endpoint" {
  description = "Application health check URL"
  value       = "http://${aws_lb.main.dns_name}/health"
}
