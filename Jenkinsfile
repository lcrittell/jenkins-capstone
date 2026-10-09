//Initial Jenkinsfile
pipeline {
    agent any

    environment {
        APP_NAME = "my-python-app"
        APP_VERSION = "$BUILD_ID"
        AWS_ECS_CLUSTER = 'JenkinsCapstone-Cluster'
        AWS_ECS_SERVICE_PROD = 'JenkinsCapstone-Service-Prod'
        AWS_ECS_SERVICE_STAGING = 'JenkinsCapstone-Service-Staging'
        QUAY_ORG = "jenkinscapstone"
    }

    stages {

        stage('Build Staging Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        echo "$QUAY_PASSWORD" | docker login quay.io -u "$QUAY_USERNAME" --password-stdin
                        docker build --build-arg APP_VERSION="$APP_VERSION" -t quay.io/$QUAY_ORG/$APP_NAME:$APP_VERSION .
                        docker push quay.io/$QUAY_ORG/$APP_NAME:$APP_VERSION
                        docker logout quay.io
                    '''
                }
            }
        }

        stage('Pre Staging Tests') {
            parallel {
                stage('Testing') {
                    agent {
                        docker {
                            image 'python:3.12-slim'
                            reuseNode true
                            args '-u root'
                        }
                    }
                    steps {
                        sh '''
                            pip install pytest
                            PYTHONPATH=. pytest tests/ --junitxml=test-results.xml
                        '''
                    }
                    post {
                        always {
                            junit 'test-results.xml'
                        }
                    }
                }

                stage('Python Lint') {
                    agent {
                        docker {
                            image 'python:3.12-slim'
                            reuseNode true
                            args '-u root'
                        }
                    }
                    steps {
                        sh '''
                            pip install ruff
                            ruff check app.py
                        '''
                    }
                }

                stage('HTML Lint') {
                    agent {
                        docker {
                            image 'node:22-alpine'
                            reuseNode true
                            args '-u root'
                        }
                    }
                    steps {
                        sh '''
                            npm install -g htmlhint
                            htmlhint index.html
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
                withCredentials([usernamePassword(credentialsId: 'my-aws', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                        sh '''
                            aws configure set region us-east-2
                            aws --version
                            sed -i "s/#APP_VERSION#/$APP_VERSION/g" aws/task-definition-staging.json
                            sed -i "s/#QUAY_USERNAME#/$QUAY_ORG/g" aws/task-definition-staging.json
                            sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-staging.json
                            echo "=== Registering task definition ==="
                            date
                            LATEST_TD_REVISION=$(aws ecs register-task-definition --cli-input-json file://aws/task-definition-staging.json | jq '.taskDefinition.revision')
                            echo "=== Updating ECS service ==="
                            date
                            aws ecs update-service --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_STAGING --task-definition JenkinsCapstone-TaskDefinition-Staging:$LATEST_TD_REVISION
                            echo "=== Waiting for ECS service to become stable ==="
                            date
                            aws ecs wait services-stable --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_STAGING
                            echo "=== ECS service is stable ==="
                            date
                        '''
                        script {
                            env.STAGING_URL = sh(
                                script: '''
                                    TASK_ARN=$(aws ecs list-tasks \
                                        --cluster "$AWS_ECS_CLUSTER" \
                                        --service-name "$AWS_ECS_SERVICE_STAGING" \
                                        --desired-status RUNNING \
                                        --query 'taskArns[0]' \
                                        --output text)

                                    ENI_ID=$(aws ecs describe-tasks \
                                        --cluster "$AWS_ECS_CLUSTER" \
                                        --tasks "$TASK_ARN" \
                                        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
                                        --output text)

                                    PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                                        --network-interface-ids "$ENI_ID" \
                                        --query 'NetworkInterfaces[0].Association.PublicIp' \
                                        --output text)

                                    echo "http://$PUBLIC_IP:8000"
                                ''',
                                returnStdout: true
                            ).trim()
                            
                            echo "Staging URL: ${env.STAGING_URL}"
                        }
                    }
                }
            }
        }

        stage('Staging E2E Testing') {
            agent {
                docker {
                    image 'mcr.microsoft.com/playwright:v1.64.0-noble'
                    reuseNode true
                }
            }

            environment {
                BASE_URL = "$STAGING_URL"
            }

            steps {
                sh '''
                    npm ci
                    npx playwright test
                '''
            }

            post {
                always {
                    junit 'playwright-results.xml'
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

        stage('Deploy Prod') {
            agent {
                docker {
                    image 'amazon/aws-cli'
                    reuseNode true
                    args "-u root --entrypoint=''"
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-aws', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                        sh '''
                            aws configure set region us-east-2
                            aws --version
                            cp aws/task-definition-prod.json aws/task-definition-prod-deploy.json
                            sed -i "s/#APP_VERSION#/$APP_VERSION/g" aws/task-definition-prod-deploy.json
                            sed -i "s/#QUAY_USERNAME#/$QUAY_ORG/g" aws/task-definition-prod-deploy.json
                            sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-prod-deploy.json
                            LATEST_TD_REVISION=$(aws ecs register-task-definition --cli-input-json file://aws/task-definition-prod-deploy.json | jq '.taskDefinition.revision')
                            aws ecs update-service --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD --task-definition JenkinsCapstone-TaskDefinition-Prod:$LATEST_TD_REVISION
                            aws ecs wait services-stable --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD
                        '''
                    }
                }
            }
        }

        stage('Prod E2E Testing') {
            agent {
                docker {
                    image 'mcr.microsoft.com/playwright:v1.64.0-noble'
                    reuseNode true
                }
            }

            environment {
                BASE_URL = "http://jenkins-capstone-prod-alb-1107757812.us-east-2.elb.amazonaws.com"
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        try {
                            sh '''
                                npm ci
                                npx playwright test
                            '''
                        } catch (err) {
                            env.PROD_E2E_FAILED = 'true'
                            throw err
                        }
                    }
                }
            }

            post {
                always {
                    junit 'playwright-results.xml'
                }
            }
        }

        stage('Rollback Prod') {
            when {
                expression {
                    env.PROD_E2E_FAILED == 'true'
                }
            }
            agent {
                docker {
                    image 'amazon/aws-cli'
                    reuseNode true
                    args "-u root --entrypoint=''"
                }
            }
            steps {
                echo "Prod E2E failed. Starting automatic rollback"
                script {
                    env.CURRENT_PROD = sh(
                        script: '''
                            curl -s "https://quay.io/api/v1/repository/$QUAY_ORG/$APP_NAME/tag/?onlyActiveTags=true" \
                                | jq -r '.tags[].name | select(startswith("prod-"))' \
                                | sort -Vr \
                                | head -n 1
                        ''',
                        returnStdout: true
                    ).trim()
                    if (!env.CURRENT_PROD || !env.CURRENT_PROD.startsWith('prod-')) {
                        error('Rollback aborted: no valid previous production tag was found.')
                    }

                    env.CURRENT_PROD_NO = env.CURRENT_PROD.replaceFirst('^prod-', '')
                }
                echo "Rolling back to $CURRENT_PROD_NO"
                withCredentials([usernamePassword(credentialsId: 'my-aws', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                        sh '''
                            aws configure set region us-east-2
                            pwd
                            sed -i "s/#APP_VERSION#/$CURRENT_PROD_NO/g" aws/task-definition-prod.json
                            sed -i "s/#QUAY_USERNAME#/$QUAY_ORG/g" aws/task-definition-prod.json
                            sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-prod.json
                            LATEST_TD_REVISION=$(aws ecs register-task-definition --cli-input-json file://aws/task-definition-prod.json | jq '.taskDefinition.revision')
                            aws ecs update-service --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD --task-definition JenkinsCapstone-TaskDefinition-Prod:$LATEST_TD_REVISION
                            aws ecs wait services-stable --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD
                        '''
                    }
                }
            }
        }

        stage('Tag Prod') {
            when {
                expression {
                    env.PROD_E2E_FAILED != 'true'
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        echo "$QUAY_PASSWORD" | docker login quay.io -u "$QUAY_USERNAME" --password-stdin
                        docker pull quay.io/$QUAY_ORG/$APP_NAME:$APP_VERSION
                        docker tag quay.io/$QUAY_ORG/$APP_NAME:$APP_VERSION quay.io/$QUAY_ORG/$APP_NAME:prod-$APP_VERSION
                        docker push quay.io/$QUAY_ORG/$APP_NAME:prod-$APP_VERSION
                        docker tag quay.io/$QUAY_ORG/$APP_NAME:$APP_VERSION quay.io/$QUAY_ORG/$APP_NAME:stable
                        docker push quay.io/$QUAY_ORG/$APP_NAME:stable
                        docker logout quay.io
                    '''
                }
            }
        }
    }
    post {
        success {
            emailext(
                to: 'lcrittell@515tech.com',
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Jenkins pipeline completed successfully.

                    Job: ${env.JOB_NAME}
                    Build: #${env.BUILD_NUMBER}
                    Application version: ${env.APP_VERSION}
                    Status: SUCCESS

                    Production E2E tests and prod tagging completed.
                """
            )
        }
        failure {
            emailext(
                to: 'you@example.com',
                subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Jenkins pipeline failed.

                    Job: ${env.JOB_NAME}
                    Build: #${env.BUILD_NUMBER}
                    Application version: ${env.APP_VERSION}
                    Status: FAILURE

                    Check the console output to identify the failed stage.
                    If production E2E tests failed, the rollback stage may have run.

                    Console output:
                    ${env.BUILD_URL}console
                """
            )
        }
        aborted {
            emailext(
                to: 'you@example.com',
                subject: "ABORTED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Jenkins pipeline was aborted.

                    Job: ${env.JOB_NAME}
                    Build: #${env.BUILD_NUMBER}
                    Status: ABORTED

                    Build details:
                    ${env.BUILD_URL}
                """
            )
        } 
    }
}