//Initial Jenkinsfile
pipeline {
    agent any

    environment {
        MY_VAR = "My variable"
    }

    stages {
        stage('Stage one') {
            steps {
                sh '''
                    echo "Hello Jenkins"
                '''
            }
        }
    }
}