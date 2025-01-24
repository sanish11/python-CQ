node(){
    deleteDir()
    properties([
        parameters([
            base64File( description:'upload a file', name: 'FILE'),
            string(name: 'Language', defaultValue: 'es', description: 'Country code')
            
        ])
    ])
    

    
    withFileParameter('FILE') {
        
    stage('Clone and Execute Script') {
        echo "Cloning Python script from GitHub..."
        
        sh "git clone https://github.com/sanish11/python-CQ.git . "
        
    }
    stage("ada"){
        sh """
            unzip -o "${FILE}" -d "unzipped"
        """
        }
    
    
    
    stage("Python Script"){
        echo "ada"
        def stfFile = sh(script: 'find unzipped/ -name "*.stf" -print -quit', returnStdout: true).trim()
        sh """
        
            python3 stf.py "${stfFile}" output.stf "${params.Language}"
        """
    }
    
    stage('Archive Artifact') {
        echo "Archiving output_file.stf..."
        archiveArtifacts artifacts: 'output.stf', allowEmptyArchive: true
    }
    }

}
