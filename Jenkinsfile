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
            agent {
                docker {
                    image 'amazon/aws-cli'
                    reuseNode true
                    args "-u root --entrypoint=''"
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        aws --version
                        sed -i "s/#APP_VERSION/$APP_VERSION/g" aws/task-definition-prod.json
                        sed -i "s/#QUAY_USERNAME#/$QUAY_USERNAME/g" aws/task-definition-prod.json
                        sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-prod.json
                        cat aws/task-definition-prod.json
                    '''
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
        }

        stage('Approval') {
            steps {
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

        stage('Deploy to AWS') {
            agent {
                docker {
                    image 'amazon/aws-cli'
                    reuseNode true
                    args "-u root --entrypoint=''"
                }
            }
            steps {
                sh '''
                    aws --version
                '''
            }
        }
    }
}