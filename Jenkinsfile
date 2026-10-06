//Initial Jenkinsfile
pipeline {
    agent any

    environment {
        MY_VAR = "My variable"
        APP_NAME = "my-python-app"
        APP_VERSION = "$BUILD_ID"
    }

    stages {
        stage('Stage one') {
            steps {
                sh '''
                    echo "Hello Jenkins"
                    echo "My variable: $MY_VAR"
                '''
            }
        }

        stage('Build Docker image') {
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

        stage('Deploy to local docker') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        echo "$QUAY_PASSWORD" | docker login quay.io -u "$QUAY_USERNAME" --password-stdin
                        docker pull quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION
                        docker stop my-python-app || true
                        docker rm my-python-app || true
                        docker run -d --name my-python-app -p 8000:8000 quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION
                    '''
                }
            }
        }
    }
}