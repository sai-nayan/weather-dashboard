
pipeline {
    agent any

    options {
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Check Python') {
            steps {
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Automated Testing') {
            steps {
                bat 'if not exist reports mkdir reports'
                bat 'python -m pytest -v --junitxml=reports/pytest-results.xml'
            }
        }

        stage('Build & Package') {
            steps {
                bat 'python -m zipfile -c weather-dashboard-build.zip app config.py run.py requirements.txt'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'weather-dashboard-build.zip',
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
            echo 'Weather Dashboard CI Pipeline completed successfully!'
        }

        failure {
            echo 'CI Pipeline failed. Check the Jenkins console output.'
        }
    }
}
