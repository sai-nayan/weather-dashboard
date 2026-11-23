def execCmd(String unixCmd, String winCmd = null) {
    if (isUnix()) {
        sh unixCmd
    } else {
        bat (winCmd != null ? winCmd : unixCmd)
    }
}

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
                echo 'Stage 1: Checking out source code'
                checkout scm
            }
        }

        stage('Python Environment Verification') {
            steps {
                echo 'Stage 2: Verifying Python environment'
                script {
                    execCmd('python3 --version || python --version', 'python --version')
                    execCmd('python3 -m pip --version || python -m pip --version', 'python -m pip --version')
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Stage 3: Installing dependencies'
                script {
                    execCmd('python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt',
                            'python -m pip install -r requirements.txt')
                }
            }
        }

        stage('Automated Testing') {
            steps {
                echo 'Stage 4: Running automated tests (Phase 2)'
                script {
                    execCmd('mkdir -p reports && (pytest -v --junitxml=reports/pytest-results.xml tests/ || python3 -m pytest -v --junitxml=reports/pytest-results.xml tests/)',
                            'if not exist reports mkdir reports && python -m pytest -v --junitxml=reports/pytest-results.xml tests/')
                }
            }
        }

        stage('Publish Test Reports') {
            steps {
                echo 'Stage 5: Publishing test reports'
                junit testResults: 'reports/pytest-results.xml',
                      allowEmptyResults: false
            }
        }

        stage('Security Code Analysis (SAST - Phase 9)') {
            steps {
                echo 'Stage 6: Running Static Application Security Testing (Bandit / Flake8)'
                script {
                    execCmd('mkdir -p reports && (bandit -r app -ll -f json -o reports/bandit-report.json || python3 -m bandit -r app -ll || echo "SAST audit logged warnings (non-blocking)")',
                            'if not exist reports mkdir reports && (bandit -r app -ll -f json -o reports/bandit-report.json 2>nul || echo SAST audit logged warnings)')
                }
            }
        }

        stage('Docker Image Build') {
            steps {
                echo 'Stage 7: Building Docker image (Phase 3)'
                script {
                    execCmd("docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest .",
                            "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% -t %DOCKER_IMAGE%:latest .")
                }
            }
        }

        stage('Image Vulnerability Scanning (Trivy - Phase 9)') {
            steps {
                echo 'Stage 8: Scanning Docker image for CVE vulnerabilities (Trivy)'
                script {
                    execCmd("""
                        if command -v trivy >/dev/null 2>&1; then
                            trivy image --severity HIGH,CRITICAL --exit-code 0 ${DOCKER_IMAGE}:${DOCKER_TAG}
                        else
                            echo "Trivy CLI not installed on agent; skipping image vulnerability scan."
                        fi
                    """,
                    """
                        where trivy >nul 2>&1 && (trivy image --severity HIGH,CRITICAL --exit-code 0 %DOCKER_IMAGE%:%DOCKER_TAG%) || (echo Trivy not installed on agent)
                    """)
                }
            }
        }

        stage('Docker Container Deployment') {
            steps {
                echo 'Stage 9: Deploying application container'
                script {
                    execCmd("""
                        docker stop ${CONTAINER_NAME} 2>/dev/null || true
                        docker rm -f ${CONTAINER_NAME} 2>/dev/null || true
                        docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} \
                          -v weather_data:/app/instance \
                          -e FLASK_ENV=production \
                          -e SECRET_KEY=jenkins-ci-production-key \
                          -e DATABASE_URL=sqlite:////app/instance/weather.db \
                          -e PORT=${APP_PORT} \
                          ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """,
                    """
                        docker stop %CONTAINER_NAME% 2>nul || ver >nul
                        docker rm -f %CONTAINER_NAME% 2>nul || ver >nul
                        docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:%APP_PORT% -v weather_data:/app/instance -e FLASK_ENV=production -e SECRET_KEY=jenkins-ci-production-key -e DATABASE_URL=sqlite:////app/instance/weather.db -e PORT=%APP_PORT% %DOCKER_IMAGE%:%DOCKER_TAG%
                    """)
                }
            }
        }

        stage('Container Health Verification') {
            steps {
                echo 'Stage 10: Checking application health'
                script {
                    execCmd("""
                        sleep 10
                        docker ps --filter name=${CONTAINER_NAME}
                        docker logs --tail 30 ${CONTAINER_NAME}
                        curl -f -s http://localhost:${APP_PORT}/health || (echo "Health check failed" && exit 1)
                    """,
                    """
                        ping -n 16 127.0.0.1 >nul
                        docker ps --filter name=%CONTAINER_NAME%
                        docker logs --tail 30 %CONTAINER_NAME%
                        curl.exe -f -s http://localhost:%APP_PORT%/health || (echo Health check failed && exit /b 1)
                    """)
                }
                echo 'Application health check passed!'
            }
        }

        stage('Archive Build Artifacts') {
            steps {
                echo 'Stage 11: Archiving build artifacts'
                script {
                    execCmd("python3 -m zipfile -c weather-dashboard-build.zip app config.py run.py requirements.txt Dockerfile docker-compose.yml .dockerignore Jenkinsfile || python -m zipfile -c weather-dashboard-build.zip app config.py run.py requirements.txt Dockerfile docker-compose.yml .dockerignore Jenkinsfile",
                            "python -m zipfile -c weather-dashboard-build.zip app config.py run.py requirements.txt Dockerfile docker-compose.yml .dockerignore Jenkinsfile")
                }

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
            echo '=============================================='
            echo 'Weather Dashboard CI/CD Pipeline Successful!'
            echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
            echo "Container: ${CONTAINER_NAME}"
            echo "Application: http://localhost:${APP_PORT}"
            echo '=============================================='
        }

        failure {
            echo 'CI/CD Pipeline failed. Check Jenkins Console Output.'
        }
    }
}
