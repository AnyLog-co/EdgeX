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
# AnyLog IP address 
MQTT_IP_ADDRESS=10.0.0.229 
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

To validate that data is coming in, users can execute cURL request against: [http://localhost:48080/api/v1/event](http://localhost:48080/api/v1/event). 
The output should be something like this: 
```json
# curl http://localhost:48080/api/v1/event 2> /dev/null  2> /dev/null | jq 
[{
  "id": "fb68440c-0dea-49be-b2b2-8e9003ab78c2",
  "pushed": 1656093207769,
  "device": "Random-Integer-Generator01",
  "created": 1656093207759,
  "modified": 1656093207771,
  "origin": 1656093207757297700,
  "readings": [
    {
      "id": "95fa6063-9c6d-4a31-8237-9732c51ec3f7",
      "created": 1656093207759,
      "origin": 1656093207757240800,
      "device": "Random-Integer-Generator01",
      "name": "RandomValue_Int16",
      "value": "-12830",
      "valueType": "Int16"
    }
  ]
},
{
  "id": "fc9e9640-66c3-424a-b572-9bd81126fcf8",
  "pushed": 1656092947759,
  "device": "Random-Integer-Generator01",
  "created": 1656092947754,
  "modified": 1656092947761,
  "origin": 1656092947752393700,
  "readings": [
    {
      "id": "a6fec012-7cc0-4a3b-adf1-6e64952ae46f",
      "created": 1656092947754,
      "origin": 1656092947752350200,
      "device": "Random-Integer-Generator01",
      "name": "RandomValue_Int8",
      "value": "8",
      "valueType": "Int8"
    }
  ]
},
{
  "id": "fcd6662c-893b-42c8-89eb-1d3963359256",
  "pushed": 1656092787767,
  "device": "Random-Integer-Generator01",
  "created": 1656092787757,
  "modified": 1656092787768,
  "origin": 1656092787752256300,
  "readings": [
    {
      "id": "28307823-8b07-42dd-8089-599e6cf339d4",
      "created": 1656092787757,
      "origin": 1656092787752201200,
      "device": "Random-Integer-Generator01",
      "name": "RandomValue_Int32",
      "value": "-1653714562",
      "valueType": "Int32"
    }
  ]
},
{
  "id": "ff2b6be0-890c-4e21-9bac-70bce9d27612",
  "pushed": 1656092885326,
  "device": "Modbus TCP test device",
  "created": 1656092885317,
  "modified": 1656092885327,
  "origin": 1656092885314563800,
  "readings": [
    {
      "id": "57a765d7-80ed-4dbc-b89a-866e35dda251",
      "created": 1656092885317,
      "origin": 1656092885313868000,
      "device": "Modbus TCP test device",
      "name": "Temperature",
      "value": "0.000000e+00",
      "valueType": "Float64",
      "floatEncoding": "eNotation"
    },
    {
      "id": "bde7a5c5-2d61-4f6f-98d8-93a7e2ce1316",
      "created": 1656092885317,
      "origin": 1656092885311935200,
      "device": "Modbus TCP test device",
      "name": "OperationMode",
      "value": "Cool",
      "valueType": "String"
    },
    {
      "id": "f2acb1fb-f785-4cf4-8c80-8b97ab7f6056",
      "created": 1656092885317,
      "origin": 1656092885312948700,
      "device": "Modbus TCP test device",
      "name": "FanSpeed",
      "value": "Low",
      "valueType": "String"
    }
  ]
}]
```

## AnyLog
The [AnyLog deployment](https://github.com/AnyLog-co/deployments) configuration files, users can specify a basic 
`timestamp`/`value` MQTT configurations. Howerver, they can also create more complex configurations either via REST or 
when the updating _local_script.al_ file. 

### Configuration File
When configuring an _Operator_ or _Publisher_ node, there's an MQTT section that when enabled & configured will run 
`run mqtt client` when starting AnyLog.

**Sample Configurations**
* Getting data from a third-party MQTT broker with everything but value hard-coded  
```dotenv
# MQTT parameters - the default recieves data from a remote MQTT broker
MQTT_ENABLE=true
BROKER=driver.cloudmqtt.com
MQTT_PORT=18785
MQTT_USER=ibglowct
MQTT_PASSWORD=MSY4e009J7ts
MQTT_LOG=false
MQTT_TOPIC_NAME=anylogedgex
MQTT_TOPIC_DBMS=test
# original value was "bring [device]" (Random-Integer-Generator01). howerver, due to a PSQL table name limit size is 65 chars, it's manually changeds to: rand_int 
MQTT_TOPIC_TABLE=rand_data
MQTT_COLUMN_TIMESTAMP=now
MQTT_COLUMN_VALUE_TYPE=float
MQTT_COLUMN_VALUE="bring [readings][][value]"
```

* Getting data from the AnyLog broker, where values provided by EdgeX will correlate to table name & values -- 
make sure that the `ANYLOG_BROKER_PORT` is set and **not** commented out  
```dotenv
# MQTT parameters - the default recieves data from a remote MQTT broker
MQTT_ENABLE=true
BROKER=local
MQTT_PORT=32150
#MQTT_USER=ibglowct
#MQTT_PASSWORD=MSY4e009J7ts
MQTT_LOG=false
MQTT_TOPIC_NAME=anylogedgex
MQTT_TOPIC_DBMS=test
# original value was "bring [device]" (Random-Integer-Generator01). howerver, due to a PSQL table name limit size is 65 chars, it's manually changeds to: rand_int 
MQTT_TOPIC_TABLE="bring [readings][][name]"
MQTT_COLUMN_TIMESTAMP=now
MQTT_COLUMN_VALUE_TYPE=float
MQTT_COLUMN_VALUE="bring [readings][][value]"
```

**Local Script**
To generate a more compplex `run mqtt client` (ie one that doesn't just use `timestamp` and `value` columns) require a few steps.
1. locate the `local_scripts` directory
```bash
docker volume inspect anylog-node_anylog-node-local-scripts 
[
    {
        "CreatedAt": "2022-06-24T17:42:57Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "anylog-node",
            "com.docker.compose.version": "1.29.2",
            "com.docker.compose.volume": "anylog-node-local-scripts"
        },
        "Mountpoint": "/var/lib/docker/volumes/anylog-node_anylog-node-local-scripts/_data",
        "Name": "anylog-node_anylog-node-local-scripts",
        "Options": null,
        "Scope": "local"
    }
]
```

2. vim into `/var/lib/docker/volumes/anylog-node_anylog-node-local-scripts/_data/local_script.al`
```bash 
vim /var/lib/docker/volumes/anylog-node_anylog-node-local-scripts/_data/local_script.al
```

3. Update file
```anylog
# The following file is intended as a placeholder for user implemented code. The file is automatically called by master,
# operator, publisher, query or single_node (operator / publisher) files. If not is written then nothing runs.
#
# Sample commands could include things like;
#   * complicated MQTT calls
#   * Kafka requests
#   * non-standard schedule processes, such as recording disk usage and automated queries
#
# Documentation: https://github.com/AnyLog-co/documentation
#-----------------------------------------------------------------------------------------------------------------------
# process !anylog_path/AnyLog-Network/scripts/local_script.al

# The following is what gets run when using the configuration file against a local MQTT broker    
<run mqtt client where broker=local and port=32150 and log=false and topic=(
  name=anylogedgex and 
  dbms=test and 
  table="bring [readings][][value]" and 
  column.timestamp.timestamp=now and 
  column.value=(type=str and value="bring [readings][][value]")
)> 
 
# The following is a mqtt client that uses more columns and is run against a third-party MQTT broker 
<run mqtt client where broker=driver.cloudmqtt.com and port=18785 and user=ibglowct and password=MSY4e009J7ts and log=false and topic=(
  name=anylogedgex and 
  dbms=test and 
  table="bring [readings][][value]" and 
  column.edgex_id=(type=str, value="bring [readings][][id]") and 
  column.timestamp.timestamp=now and 
  column.value=(type=str and value="bring [readings][][value]")
)>  
```

4. Execute `local_script.al` against AnyLog 
```bash 
# Within AnyLog CMD line
process  !anylog_path/AnyLog-Network/scripts/local_script.al

# via cURL 
curl -X POST ${IP}:${REST_PORT} -H "command: process /app/AnyLog-Network/scripts/local_script.al" -H "User-Agent: AnyLog/1.23"
```

5. Update configuration file to have `DEPLOY_LOCAL_SCRIPT` set to true so that in the future the script will run automatically.