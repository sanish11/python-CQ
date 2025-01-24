node(){
    environment{
        DIR = 'unzipped'
    }
    echo "Workspace cleaned. Checking contents:"
   
    properties([
        parameters([
            base64File(name: 'FILE', description: 'Upload a file'),
            string(name: 'Language', defaultValue: 'es', description: 'Country code')
            
        ])
    ])
    withFileParameter('FILE') {
    stage("Unzip"){
        sh """
            unzip -o "${FILE}" -d "${Unzipped}"
        """
        }
    }

}
