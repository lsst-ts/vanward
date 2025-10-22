#!/usr/bin/env groovy

pipeline {

    agent {
        // Use the docker to assign the Python version.
        // Use the label to assign the node to run the test.
        // It is recommended by SQUARE to not add the label
        docker {
            alwaysPull true
            image 'lsstts/develop-env:develop'
            args "--entrypoint=''"
        }
    }

    environment {
        user_ci = credentials('lsst-io')
        LTD_USERNAME="${user_ci_USR}"
        LTD_PASSWORD="${user_ci_PSW}"
    }

    stages {
        stage('Build and Upload Documentation') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh """
                    source /home/saluser/.setup_dev.sh || echo loading env failed. Continuing...
                    pip install --no-deps .
                    sphinx-build -b html doc doc/_build/html
                    ltd upload --product vanward --git-ref ${GIT_BRANCH} --dir doc/_build/html
                    """
                }
            }
        }
    }

    post {
        cleanup {
            // clean up the workspace
            deleteDir()
        }
    }
}
