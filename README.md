# EdgeX 

The following repository provides the scripts used by AnyLog to deploy EdgeX.

**Offical Links**
* [EdgeX Homepage](https://www.edgexfoundry.org/)
* [Github](https://github.com/edgexfoundry)
* [EdgeX Compose Files](https://github.com/edgexfoundry/edgex-compose)
* [Documentation](https://www.edgexfoundry.org/get-started/)
* [AnyLog Document](https://github.com/AnyLog-co/documentation)
  * [EdgeX Documentation](https://github.com/AnyLog-co/documentation/blob/master/using%20edgex.md)

## EdgeX Deployment
0. cd into Edgex directory
```shell
cd EdgeX
```

1. In [.env](.env) update MQTT related params for `app-service-mqtt` service.  
```dotenv
# Sample for sending data directly into the AnyLog Broker
MQTT_TOPIC=anylogedgex
MQTT_IP_ADDRESS=139.177.195.197
MQTT_PORT=32150
MQTT_USER=""
MQTT_PASSWORD=""

# Sample for sending data into a third-party MQTT broker (CloudMQTT)
MQTT_TOPIC=anylogedgex
MQTT_IP_ADDRESS=driver.cloudmqtt.com
MQTT_PORT=18785
MQTT_USER=ibglowct
MQTT_PASSWORD=MSY4e009J7ts
```

2. Deploy [docker-compose](docker-compose.yml) file 
```shell
docker-compose up -d 
```

3. Optional – In addition to the random data generator, there's an option to imitate modbus data using [setup.sh](setup.sh)
```shell
bash setup.sh 
```

## AnyLog
In order for AnyLog to interpret the data coming in via MQTT, user needs to run the `run mqtt client` process. 
The following is an example of the `run mqtt client` which is available via the configuration file(s) when deploying AnyLog for random data coming in via EdgeX. 
```anylog
# Local MQTT broker  
<run mqtt client where broker=139.177.195.197 and port=32150 and log=false and topic=(
    name=anylogedgex and 
    dbms=edgex and
    table=rand_data and 
    column.timestamp.timestamp=now 
    column.value=(type=float and value="bring [reading][][value]")
)> 

# Remote MQTT broker
<run mqtt client where broker=driver.cloudmqtt.com and port=18785 and user=ibglowct and password=MSY4e009J7ts and log=false and topic=(
    name=anylogedgex and 
    dbms=edgex and
    table=rand_data and 
    column.timestamp.timestamp=now 
    column.value=(type=float and value="bring [reading][][value]")
)>  
```