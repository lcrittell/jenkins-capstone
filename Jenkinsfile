//Initial Jenkinsfile
pipeline {
    agent any

    environment {
        MY_VAR = "My variable"
        APP_NAME = "my-python-app"
        APP_VERSION = "$BUILD_ID"
        AWS_ECS_CLUSTER = 'JenkinsCapstone-Cluster'
        AWS_ECS_SERVICE_PROD = 'JenkinsCapstone-Service-Prod'
        AWS_ECS_SERVICE_STAGING = 'JenkinsCapstone-Service-Staging'
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
                withCredentials([usernamePassword(credentialsId: 'my-aws', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                        sh '''
                            aws configure set region us-east-2
                            aws --version
                            sed -i "s/#APP_VERSION#/$APP_VERSION/g" aws/task-definition-staging.json
                            sed -i "s/#QUAY_USERNAME#/$QUAY_USERNAME/g" aws/task-definition-staging.json
                            sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-staging.json
                            cat aws/task-definition-staging.json
                            LATEST_TD_REVISION=$(aws ecs register-task-definition --cli-input-json file://aws/task-definition-staging.json | jq '.taskDefinition.revision')
                            echo $LATEST_TD_REVISION
                            aws ecs update-service --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_STAGING --task-definition JenkinsCapstone-TaskDefinition-Staging:$LATEST_TD_REVISION
                            aws ecs wait services-stable --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_STAGING
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
                            sed -i "s/#APP_VERSION#/$APP_VERSION/g" aws/task-definition-prod.json
                            sed -i "s/#QUAY_USERNAME#/$QUAY_USERNAME/g" aws/task-definition-prod.json
                            sed -i "s/#APP_NAME#/$APP_NAME/g" aws/task-definition-prod.json
                            cat aws/task-definition-prod.json
                            LATEST_TD_REVISION=$(aws ecs register-task-definition --cli-input-json file://aws/task-definition-prod.json | jq '.taskDefinition.revision')
                            echo $LATEST_TD_REVISION
                            aws ecs update-service --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD --task-definition JenkinsCapstone-TaskDefinition-Prod:$LATEST_TD_REVISION
                            aws ecs wait services-stable --cluster $AWS_ECS_CLUSTER --service $AWS_ECS_SERVICE_PROD
                        '''
                    }
                }
            }
        }
        stage('Tag Prod') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-quay', passwordVariable: 'QUAY_PASSWORD', usernameVariable: 'QUAY_USERNAME')]) {
                    sh '''
                        echo "$QUAY_PASSWORD" | docker login quay.io -u "$QUAY_USERNAME" --password-stdin
                        docker pull quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION
                        docker tag quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION quay.io/$QUAY_USERNAME/$APP_NAME:prod-$APP_VERSION
                        docker push quay.io/$QUAY_USERNAME/$APP_NAME:prod-$APP_VERSION
                        docker tag quay.io/$QUAY_USERNAME/$APP_NAME:$APP_VERSION quay.io/$QUAY_USERNAME/$APP_NAME:stable
                        docker push quay.io/$QUAY_USERNAME/$APP_NAME:stable
                        curl -s "https://quay.io/api/v1/repository/$QUAY_USERNAME/$APP_NAME/tag/" | jq -r '.tags[].name' | sort -u
                        docker logout quay.io
                    '''
                }
            }
        }
    }
}