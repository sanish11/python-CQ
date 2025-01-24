node(){
    deleteDir()
    properties([
        parameters([
            // base64File(name: 'FILE', description: 'Upload a file'),
            string(name: 'Language', defaultValue: 'es', description: 'Country code')
            
        ])
    ])
    
    stage('Clone and Execute Script') {
        echo "Cloning Python script from GitHub..."
        sh "git clone https://github.com/sanish11/python-CQ.git . "
        
    }
    
    withFileParameter('FILE') {
    stage("ada"){
        sh """
            unzip -o "${FILE}" -d "unzipped"
        """
        }
    }

}
