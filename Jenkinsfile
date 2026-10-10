
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t myfirst-docker .'
            }
        }

        stage('Run Playwright Tests') {
            steps {
                powershell '''
                    docker rm -f playwright-tests 2>$null
                    $LASTEXITCODE = 0

                    docker run --name playwright-tests myfirst-docker sh -c "mkdir -p /app/test-results && pytest -v -s --tb=long --junitxml=/app/test-results/results.xml"

                    $testExitCode = $LASTEXITCODE

                    New-Item -ItemType Directory -Force test-results | Out-Null

                    docker cp playwright-tests:/app/test-results/. test-results/

                    if ($testExitCode -ne 0) {
                        exit $testExitCode
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
                docker rm -f playwright-tests 2>$null
                exit 0
            '''
        }
    }
}
