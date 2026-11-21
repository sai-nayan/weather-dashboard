# Terraform Infrastructure as Code for Weather Dashboard (Local Docker Environment)

# Custom Docker network for the stack
resource "docker_network" "weather_net" {
  name   = "${var.app_name}-${var.environment}-net"
  driver = "bridge"
}

# Persistent volume for SQLite database storage
resource "docker_volume" "weather_data" {
  name = "${var.app_name}-${var.environment}-data"
}

# Persistent volume for application logs
resource "docker_volume" "weather_logs" {
  name = "${var.app_name}-${var.environment}-logs"
}

# Build/manage Docker image
resource "docker_image" "weather_app" {
  name = "${var.app_name}:${var.container_image_tag}"
  build {
    context    = "${path.module}/../../.."
    dockerfile = "Dockerfile"
  }
  triggers = {
    dockerfile_sha = filesha1("${path.module}/../../../Dockerfile")
    requirements   = filesha1("${path.module}/../../../requirements.txt")
    run_py         = filesha1("${path.module}/../../../run.py")
    config_py      = filesha1("${path.module}/../../../config.py")
  }
}

# Application Container
resource "docker_container" "weather_dashboard" {
  name  = "${var.app_name}-${var.environment}"
  image = docker_image.weather_app.image_id

  restart = var.restart_policy

  ports {
    internal = var.container_port
    external = var.host_port
  }

  env = [
    "FLASK_ENV=production",
    "PORT=${var.container_port}",
    "SECRET_KEY=${var.secret_key}",
    "DATABASE_URL=sqlite:////app/instance/weather.db",
    "GUNICORN_WORKERS=2",
    "GUNICORN_THREADS=4"
  ]

  networks_advanced {
    name = docker_network.weather_net.name
  }

  volumes {
    volume_name    = docker_volume.weather_data.name
    container_path = "/app/instance"
  }

  volumes {
    volume_name    = docker_volume.weather_logs.name
    container_path = "/app/logs"
  }
}
