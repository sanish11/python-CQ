node(){
    echo "Workspace cleaned. Checking contents:"
    sh "ls -la"
    properties([
        parameters([
            base64File(name: 'FILE', description: 'Upload a file'),
            string(name: 'Language', defaultValue: 'es', description: 'Country code')
            
        ])
    ])
    withFileParameter('FILE') {
    stage("Unzip"){
        sh """
            unzip -o "${FILE}" -d "${WORKSPACE}/unzipped"
        """
        }
    }

}
