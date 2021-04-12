response=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:9200/)
if [ $response -eq 200 ]; 
then 
    echo 'done'
else
    echo 'pending'
fi
