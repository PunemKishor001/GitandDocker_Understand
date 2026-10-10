
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'saucedemo-automation'
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                bat 'docker --version'
                bat 'docker info'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build --pull -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Run Playwright Tests') {
            steps {
                powershell '''
                    $image = "$env:IMAGE_NAME`:$env:BUILD_NUMBER"
                    $container = "playwright-tests-$env:BUILD_NUMBER"

                    New-Item -ItemType Directory -Force test-results | Out-Null

                    if (Test-Path "test-results/results.xml") {
                        Remove-Item "test-results/results.xml" -Force
                    }

                    docker run --name $container $image sh -c "mkdir -p /app/test-results && python -m pytest tests/ -v -s --tb=short --junitxml=/app/test-results/results.xml"
                    $testExitCode = $LASTEXITCODE

                    docker cp "${container}:/app/test-results/." test-results/
                    $copyExitCode = $LASTEXITCODE

                    docker rm -f $container
                    $cleanupExitCode = $LASTEXITCODE

                    if ($testExitCode -ne 0) {
                        exit $testExitCode
                    }

                    if ($copyExitCode -ne 0) {
                        exit $copyExitCode
                    }

                    if ($cleanupExitCode -ne 0) {
                        exit $cleanupExitCode
                    }
                '''
            }
        }
    }

    post {
        always {
            junit(
                testResults: 'test-results/results.xml',
                allowEmptyResults: true
            )

            archiveArtifacts(
                artifacts: 'test-results/**',
                allowEmptyArchive: true
            )

            powershell '''
                $container = "playwright-tests-$env:BUILD_NUMBER"
                docker rm -f $container 2>$null
                exit 0
            '''
        }

        success {
            echo 'Playwright automation completed successfully.'
        }

        failure {
            echo 'Automation failed. Check Console Output and test reports.'
        }

        cleanup {
            bat 'docker image prune -f'
        }
    }
}
