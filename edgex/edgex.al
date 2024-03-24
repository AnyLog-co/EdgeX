#-----------------------------------------------------------------------------------------------------------------------
# The following demonstrate receiving data from EdgeX against a single topic with multiple types of data, using
# policies function. For the demonstrating we are using both the Random-Integer-Generator01  & Modbus TCP test device.
#
#   - Documentation: https://github.com/AnyLog-co/documentation/blob/master/mapping%20data%20to%20tables.md
#   - Deploying EdgeX: https://github.com/AnyLog-co/lfedge-code/tree/main/edgex
#-----------------------------------------------------------------------------------------------------------------------
# process !local_scripts/edgex.al

:params:
on error ignore
param_error = false
broker = $BROKER
if not !broker then call broker-param-error
port = $MQTT_PORT
if not !port then call port-param-error
if param_error == true then
do echo "Unable to deploy MQTT client"
do goto end-script

set mqtt_log = false
if $MQTT_LOG then mqtt_log = $MQTT_LOG
if $MQTT_USER then mqtt_user = $MQTT_USER
if $MQTT_PASSWORD then mqtt_password = $MQTT_PASSWORD

set mqtt_topic_name = *
if $MQTT_TOPIC_NAME then mqtt_topic_name = $MQTT_TOPIC_NAME

if $MQTT_TOPIC_DBMS then mqtt_topic_dbms = $MQTT_TOPIC_DBMS

:declare-mapping:
on error goto declare-mapping-error
# random data
policy_id1 = rnd_val
policy = blockchain get mapping where id = !policy_id1
if not !policy then
<do mapping1 = {"mapping" : {
    "condition" : "if [device] == 'Random-Integer-Generator01'",
    "id" : !policy_id1,
    "dbms" : !mqtt_topic_dbms,
    "table" : "rand_data",
    "readings" : "readings",
    "schema" : {
        "timestamp" : {
            "default" : "now()",
            "type" : "timestamp"
        },
        "value" : {
            "bring" : "[value]",
            "type" : "decimal"
        }
    }
}}>


# sample PLC data
policy_id2 = device
policy = blockchain get mapping where id = !policy_id2
if not !policy then
<do mapping2 = {"mapping" : {
    "condition" : "if [device] == 'Modbus TCP test device'",
    "id" : !policy_id2,
    "dbms" : !mqtt_topic_dbms,
    "table" : "plc_device",
    "readings" : "readings",
    "schema" : {
        "timestamp" : {
            "default" : "now()",
            "type" : "timestamp"
        },
        "Temperature" : {
            "condition" : "if [name] == Temperature",
            "bring" : "[value]",
            "type" : "decimal"
        },
        "mode" : {
            "condition" : "if [name] == OperationMode",
            "bring" : "[value]",
            "type" : "string"
        },
        "speed" : {
            "condition" : "if [name] == FanSpeed",
            "bring" : "[value]",
            "type" : "string"
        }
    }
}}>

:declare-policy:
on error call declare-policy-error
if !mapping1 then
do blockchain prepare policy !mapping1
do blockchain insert where policy=!mapping1 and local=true and master=!ledger_conn

if !mapping2 then 
do blockchain prepare policy !mapping2
do blockchain insert where policy=!mapping2 and local=true and master=!ledger_conn

:mqtt-call:
on error goto mqtt-error
if !broker == rest and !mqtt_user and !mqtt_password and !mqtt_topic_dbms then
<do run mqtt client where broker=!broker and port=!port and user-agent=anylog and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(
    name=!mqtt_topic_name and
    policy=!policy_id1 and
    policy=!policy_id2
)>
else if !broker == rest and !mqtt_topic_dbms then
<do run mqtt client where broker=!broker and port=!port and user-agent=anylog and log=!mqtt_log and topic=(
    name=!mqtt_topic_name and
    policy=!policy_id1 and
    policy=!policy_id2
)>
else if !broker == rest then run mqtt client where broker=!broker and port=!port and user-agent=anylog and log=!mqtt_log and topic=(name=!mqtt_topic_name)
else if !broker != rest and !mqtt_user and !mqtt_password and !mqtt_topic_dbms then
<do run mqtt client where broker=!broker and port=!port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(
    name=!mqtt_topic_name and
    policy=!policy_id1 and
    policy=!policy_id2
)>
else if !broker != rest and !mqtt_topic_dbms then
<do run mqtt client where broker=!broker and port=!port and log=!mqtt_log and topic=(
    name=!mqtt_topic_name and
    policy=!policy_id1 and
    policy=!policy_id2
)>
else if !broker != rest then run mqtt client where broker=!broker and port=!port and log=!mqtt_log and topic=(name=!mqtt_topic_name)


:end-script:
end script

:broker-param-error:
echo "Missing broker value, cannot deploy MQTT client"
param_error = true
return

:port-param-error:
echo "Missing port value, cannot deploy MQTT client"
param_error = true
return

:declare-mapping-error:
echo "Failed to mapping policy"
goto end-script

:declare-policy-error:
echo "Failed to declare policy on blockchain"
return

:get-policy-id:
echo "Failed to extract policy ID"
return

:mqtt-error:
echo "Failed to deploy MQTT process"
goto end-script
