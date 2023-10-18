#!groovy
node('docker') {
  timestamps {
    wrap([$class: 'AnsiColorBuildWrapper']) {
      stage('Make sure to run only on deploy branch') {
        if (env.BRANCH_NAME != 'deploy') {
          return 0
        }
      }
      stage('Checkout source') {
        checkout scm
      }
      stage('Publish site') {
        sh 'echo "Deploying to s3://shiny.rstudio.com/py/ ..."'
        sh 'aws s3 sync --region us-east-1 --delete _build/ s3://shiny.rstudio.com/py/ --acl public-read --cache-control "public,max-age=300"'
      }
    }
  }
}
