properties([
    parameters([
        string(name: 'Org_Alias', defaultValue: 'build.admin@cqv14.1.1.test.translation.com ', description: 'Alias or Username for Org'),
        base64File( description:'upload a file', name: 'FILE'),
        string(name: 'Language', defaultValue: 'es', description: 'Country code'),
        choice(
            name: 'ENVIRONMENT',
            choices: ['Translating_Exported_File','Renaming_Tabs_And_Labels'],
            description: 'Select which translation related task would you like to do.'
        )
    ])
])
node {
    stage('Preparation') {
        echo "Selected Task: ${params.ENVIRONMENT}"
        echo "Org Alias: ${params.Org_Alias}"
        echo "Language Code: ${params.Language_Code}"
        echo "Uploaded File: ${params.FILE}"
    }

    if (params.ENVIRONMENT == 'Translating_Exported_File'){
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
    else if (params.ENVIRONMENT == 'Renaming_Tabe_And_Labels') {
        // Execute steps for Translating exported file
        stage('Connect to Org') {
            withCredentials([file(credentialsId: 'SERVER_KEY', variable: 'jwt_key_file'), string(credentialsId: 'CLIENT_ID', variable: 'cq_consumer_secret')]) {
                sh """
                sfdx auth:jwt:grant --instanceurl https://test.salesforce.com --clientid ${cq_consumer_secret} --username ${params.Org_Alias} --jwtkeyfile ${jwt_key_file}
                """
            }
        }
        stage('Retrieve Translations') {
            sh "sf project generate --name ."
            sh """
                sf project retrieve start --metadata 'CustomObjectTranslation:*-${params.Language_Code}' -o ${params.Org_Alias} --ignore-conflicts
            """
            sh "rm -rf ada"
            sh "sf project convert source --root-dir force-app/main/default/objectTranslations --output-dir ada"
        }
        stage('Clone and Execute Script') {
            echo "Cloning Python script from GitHub..."
            sh """
                if [ ! -d "./ada/Python/.git" ]; then
                    echo "Cloning the repository..."
                    git clone https://github.com/sanish11/python-CQ.git ./ada/Python
                else
                    echo "Repository already exists. Pulling the latest changes..."
                    cd ./ada/Python
                    git pull
                fi
            """
            sh """
                python3 --version
                python3 ./ada/Python/renameTranslation.py
            """
        }
        stage('Deploy') {
            sh "sf project deploy start -o ${params.Org_Alias} --metadata-dir ada --ignore-conflicts --ignore-errors"
        }

    }
}