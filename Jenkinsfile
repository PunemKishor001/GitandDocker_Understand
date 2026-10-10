
stage('Run Playwright Tests') {
    steps {
        withCredentials([
            string(
                credentialsId: 'betterstack-source-token',
                variable: 'BETTERSTACK_SOURCE_TOKEN'
            )
        ]) {
            powershell '''
                $image = "$env:IMAGE_NAME`:$env:BUILD_NUMBER"
                $container = "playwright-tests-$env:BUILD_NUMBER"

                New-Item -ItemType Directory -Force test-results |
                    Out-Null

                if (Test-Path "test-results/results.xml") {
                    Remove-Item "test-results/results.xml" -Force
                }

                docker run --name $container `
                    -e BETTERSTACK_SOURCE_TOKEN `
                    -e BUILD_NUMBER `
                    -e TEST_ENV=jenkins `
                    $image sh -c "mkdir -p /app/test-results && python -m pytest tests/ -v -s --tb=short --junitxml=/app/test-results/results.xml"

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
