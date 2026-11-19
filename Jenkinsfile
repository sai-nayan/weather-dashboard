pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE   = 'weather-dashboard'
        DOCKER_TAG     = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'weather-dashboard'
        APP_PORT       = '5050'
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                echo 'Stage 1: Checking out source code from GitHub repository'
                checkout scm
            }
        }

        stage('Python Environment Verification') {
            steps {
                echo 'Stage 2: Verifying Python and pip installation'
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Stage 3: Installing required Python dependencies'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Automated Testing using pytest') {
            steps {
                echo 'Stage 4: Executing automated test suite with pytest'
                bat 'if not exist reports mkdir reports'
                bat 'python -m pytest -v --junitxml=reports/pytest-results.xml tests/'
            }
        }

        stage('Test Reports Generation') {
            steps {
                echo 'Stage 5: Publishing JUnit test results'
                junit testResults: 'reports/pytest-results.xml',
                      allowEmptyResults: true
            }
        }

        stage('Docker Image Build') {
            steps {
                echo 'Stage 6: Building Docker image'
                bat 'docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% -t %DOCKER_IMAGE%:latest .'
            }
        }

        stage('Docker Container Deployment') {
            steps {
                echo 'Stage 7: Deploying containerized application'
                bat 'docker stop %CONTAINER_NAME% 2>nul || ver >nul'
                bat 'docker rm -f %CONTAINER_NAME% 2>nul || ver >nul'
                bat 'docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:%APP_PORT% -e FLASK_ENV=production -e SECRET_KEY=jenkins-ci-production-key -e DATABASE_URL=sqlite:////home/appuser/app/instance/weather.db -e PORT=%APP_PORT% %DOCKER_IMAGE%:latest'
            }
        }

        stage('Container Health Verification') {
            steps {
                echo 'Stage 8: Verifying container health status and application accessibility'
                // Wait for Gunicorn workers to boot and health check to respond
                bat 'ping -n 16 127.0.0.1 >nul'
                bat 'docker ps --filter name=%CONTAINER_NAME%'
                bat 'docker logs --tail 30 %CONTAINER_NAME%'
                bat 'curl.exe -f -s http://localhost:%APP_PORT%/health || (echo Container health check failed && exit /b 1)'
                echo 'Application health check passed successfully!'
            }
        }

        stage('Archive Build Artifacts') {
            steps {
                echo 'Stage 9: Archiving build artifacts'
                bat 'python -m zipfile -c weather-dashboard-build.zip app config.py run.py requirements.txt Dockerfile docker-compose.yml .dockerignore'
                archiveArtifacts artifacts: 'weather-dashboard-build.zip',
                                 fingerprint: true
                archiveArtifacts artifacts: 'reports/**',
                                 allowEmptyArchive: true,
                                 fingerprint: true
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/pytest-results.xml',
                  allowEmptyResults: true
        }

        success {
            echo '====================================================='
            echo '  Weather Dashboard CI/CD Pipeline Completed Successfully!'
            echo "  Image:       ${DOCKER_IMAGE}:${DOCKER_TAG}"
            echo "  Container:   ${CONTAINER_NAME}"
            echo "  URL:         http://localhost:${APP_PORT}"
            echo '====================================================='
        }

        failure {
            echo 'CI/CD Pipeline failed. Check console output for diagnostic details.'
        }
    }
}
