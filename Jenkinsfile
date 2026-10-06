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
                        docker build -t quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION .
                        docker push quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION
                        docker logout quay.io
                    '''
                }
            }
        }
    }
}