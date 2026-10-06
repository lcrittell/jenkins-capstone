//Initial Jenkinsfile
pipeline {
    agent any

    environment {
        MY_VAR = "My variable"
        APP_NAME = "my-python-app"
        APP_VERSION = "$BUILD_ID"
    }

    stages {

        stage('Build Staging image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        echo "$QUAY_PASSWORD" | docker login quay.io -u "$QUAY_USERNAME" --password-stdin
                        docker build --build-arg APP_VERSION="$APP_VERSION" -t quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION .
                        docker push quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION
                        docker logout quay.io
                    '''
                }
            }
        }

        stage('Pre Staging Tests') {
            parallel {
                stage('Testing') {
                    steps {
                        sh '''
                            echo "Testing..."
                        '''
                    }
                }

                stage('Linting') {
                    steps {
                        sh '''
                            echo "Linting code..."
                        '''
                    }
                }
            }
        }

        stage('Deploy Staging') {
            steps {
                script {
                    env.STAGING_URL = sh(
                        script: '''
                            echo "https://google.com"
                        ''',
                        returnStdout: true
                    ).trim()
                    echo "Staging URL: ${env.STAGING_URL}"
                }
            }
        }

        stage('Approval') {
            steps {
                script {
                    currentBuild.description = """
                        <h3>Review Staging Deployment</h3>
                        <p>Please review the application before deploying to prod.</p>
                        <p>
                            <a href="${env.STAGING_URL}" target="_blank">
                                Open Staging Application
                            </a>
                        </p>
                    """
                    
                timeout(time: 1, unit: 'HOURS') {
                    input(
                        message: """
                        Review Staging Deployment
   
                        Please review the application before deploying to prod

                        ${env.STAGING_URL}
                        """, 
                        ok: 'Yes I am sure I want to deploy')
                }
            }
        }

        stage('Deploy Production') {
            steps {
                sh '''
                    echo "deploy production!"
                '''
            }
        }
    }
}