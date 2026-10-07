pipeline {
    agent any

    environment {
        JMETER    = 'C:\\apache-jmeter-5.6.3\\apache-jmeter-5.6.3\\bin\\jmeter.bat'
        TS_PREFIX = 'jmeter.jpetstore'
        PYTHON    = 'C:\\Program Files\\Python314\\python.exe'
    }

    stages {
        stage('1. Descargar codigo desde GitHub') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/EdwinIterante/xray-jmeter-demo.git'
            }
        }

        stage('2. Validar Java, JMeter y Python') {
            steps {
                bat 'java -version'
                bat '"%JMETER%" --version'
                bat '"%PYTHON%" --version'
            }
        }

        stage('3. Ejecutar pruebas JMeter') {
            steps {
                bat '''
                    if exist results.jtl del results.jtl
                    if exist report rmdir /s /q report
                    "%JMETER%" -n -t jpetstore_configurable_host.jmx -l results.jtl -e -o report
                '''
            }
        }

        stage('4. Convertir resultados a JUnit XML') {
            steps {
                bat '"%PYTHON%" jtl_to_junit.py results.jtl junit.xml %TS_PREFIX%'
                bat '''
                    if not exist junit.xml (
                        echo ERROR: no se genero junit.xml
                        exit /b 1
                    )
                '''
            }
        }

        stage('5. Publicar resultados en Xray') {
            steps {
                step([
                    $class: 'XrayImportBuilder',
                    serverInstance: '62e28f48-5a2e-46e8-a857-e0c539a4ae71',
                    endpointName: '/junit/multipart',
                    projectKey: 'DX',
                    testEnvironments: '',
                    testPlanKey: '',
                    fixVersion: '',
                    importFilePath: 'junit.xml',
                    testExecKey: '',
                    revision: '',
                    importInfo: """{
                        "fields": {
                            "project": { "key": "DX" },
                            "summary": "JMeter jpetstore - build #${env.BUILD_NUMBER}",
                            "description": "*Build Jenkins:* [Build #${env.BUILD_NUMBER}|${env.BUILD_URL}]\\n*Dashboard JMeter:* [Abrir dashboard|${env.BUILD_URL}artifact/report/index.html]",
                            "issuetype": { "name": "Test Execution" }
                        }
                    }""",
                    testImportInfo: '',
                    inputInfoSwitcher: 'fileContent',
                    inputTestInfoSwitcher: 'fileContent',
                    importToSameExecution: 'false',
                    credentialId: '',
                    importInParallel: 'false'
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'results.jtl, junit.xml, report/**', allowEmptyArchive: true
        }
    }
}
