trap "kill 0" EXIT

# this may need to be changed to suit your setup (This is default mac)
export ES_JAVA_HOME=$(/usr/libexec/java_home) 

npm run dev&
echo $! > recent_start_script_npm
if [ $? -eq 0 ];
then
    cd ./elasticsearch-7.12.0/bin/
    ./elasticsearch &> elastic.log&
    echo $! > recent_start_script_elastic
        if [ $? -eq 0 ];
        then
        response=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:9200/)
            while [ $response -ne 200 ];
            do echo 'waiting for elasticsearch...'
                sleep 5
                response=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:9200/)
            done
            echo 'Lauched successsfully'
        else
            echo "Elasticsearch terminated unsuccessfully"
        fi
else
    echo "Terminated unsuccessfully"
fi

wait
