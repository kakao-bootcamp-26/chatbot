pipeline {
    agent any

    stages {
        stage('Clone or Update Repository') {
            steps {
                script {
                    // 레포지토리가 이미 클론되어 있는지 확인
                    if (fileExists('chatbot')) {
                        dir('chatbot') {
                            // 이미 클론된 레포지토리의 브랜치 변경 및 최신 상태로 업데이트
                            sh 'git fetch origin'
                            sh 'git checkout main'
                            sh 'git pull origin main'
                        }
                    } else {
                        sh 'pwd'
                        // 레포지토리가 없으면 새로 클론
                        sh 'git clone https://github.com/kakao-bootcamp-26/chatbot.git'
                    }
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    sh 'pwd'
                    // .env 파일을 복사하여 레포지토리 내의 frontend/react-app/ 디렉토리로 이동
                    sh 'cp /.env ${WORKSPACE}/chatbot/.env'
                }
            }
        }
        stage('Build') {
            steps {
                dir('chatbot') {
                    script {
                        // 도커 빌드
                        sh 'docker build --no-cache -t ai-test .'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // 기존 컨테이너 중지 및 제거
                    sh 'docker stop ai-test || true'
                    sh 'docker rm ai-test || true'

                    // 도커 컨테이너 실행
                    sh 'docker run -d --name ai-test -p 5000:5000 ai-test'
                }
            }
        }
    }
}

