pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    docker.build('my-flask-app')
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    docker.image('my-flask-app').run('-p 5000:5000')
                }
            }
        }
    }
}
