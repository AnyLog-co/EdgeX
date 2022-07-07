#-----------------------------------------------------------------------------------------------------------------------
# The following demonstrate receiving data from 2 different assets coming from FLEDGE, each with its own topic.
# For demonstration, FLEDGE is running Random data generator (topic: fledge-random) and OpenWeather data
# (topic: fledge-weather).
#
#   - Documentation: https://github.com/AnyLog-co/documentation/blob/master/mapping%20data%20to%20tables.md
#   - Deploying FLEDGE: https://github.com/AnyLog-co/lfedge-code/tree/main/fledges
#-----------------------------------------------------------------------------------------------------------------------
# process !local_scripts/fledge.al
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

if $MQTT_TOPIC_DBMS then mqtt_topic_dbms = $MQTT_TOPIC_DBMS

:mqtt-call:
on error goto mqtt-error
if !broker == rest and !mqtt_user and !mqtt_password then
<do run mqtt client where broker=!broker and port=!port and user=!mqtt_user and password=!mqtt_password and user-agent=anylog and log=!mqtt_log and topic=(
    name=fledge-random and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.random=(type=float and value="bring [readings][random]" and optional=true)
) and topic=(
    name=fledge-weather and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.city=(type=str and value="bring [readings][city]" and optional=true) and
    column.clouds=(type=float and value="bring [readings][clouds]" and optional=true) and
    column.humidity=(type=float and value="bring [readings][humidity]" and optional=true) and
    column.pressure=(type=float and value="bring [readings][pressure]" and optional=true) and
    column.temperature=(type=float and value="bring [readings][temperature]" and optional=true) and
    column.visibility=(type=float and value="bring [readings][visibility]" and optional=true) and
    column.wind_speed=(type=float and value="bring [readings][wind_speed]" and optional=true)
)>
else if !broker == rest and not !mqtt_user and not !mqtt_password then
<do run mqtt client where broker=!broker and port=!port and user-agent=anylog and log=!mqtt_log and topic=(
    name=fledge-random and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.random=(type=float and value="bring [readings][random]" and optional=true)
) and topic=(
    name=fledge-weather and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.city=(type=str and value="bring [readings][city]" and optional=true) and
    column.clouds=(type=float and value="bring [readings][clouds]" and optional=true) and
    column.humidity=(type=float and value="bring [readings][humidity]" and optional=true) and
    column.pressure=(type=float and value="bring [readings][pressure]" and optional=true) and
    column.temperature=(type=float and value="bring [readings][temperature]" and optional=true) and
    column.visibility=(type=float and value="bring [readings][visibility]" and optional=true) and
    column.wind_speed=(type=float and value="bring [readings][wind_speed]" and optional=true)
)>
else if !broker != rest and !mqtt_user and !mqtt_password then
<do run mqtt client where broker=!broker and port=!port and user=!mqtt_user and password=!mqtt_password and log=!mqtt_log and topic=(
    name=fledge-random and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.random=(type=float and value="bring [readings][random]" and optional=true)
) and topic=(
    name=fledge-weather and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.city=(type=str and value="bring [readings][city]" and optional=true) and
    column.clouds=(type=float and value="bring [readings][clouds]" and optional=true) and
    column.humidity=(type=float and value="bring [readings][humidity]" and optional=true) and
    column.pressure=(type=float and value="bring [readings][pressure]" and optional=true) and
    column.temperature=(type=float and value="bring [readings][temperature]" and optional=true) and
    column.visibility=(type=float and value="bring [readings][visibility]" and optional=true) and
    column.wind_speed=(type=float and value="bring [readings][wind_speed]" and optional=true)
)>
else if !broker != rest and not !mqtt_user and not !mqtt_password then
<do run mqtt client where broker=!broker and port=!port and log=!mqtt_log and topic=(
    name=fledge-random and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.random=(type=float and value="bring [readings][random]" and optional=true)
) and topic=(
    name=fledge-weather and
    dbms=!mqtt_topic_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.city=(type=str and value="bring [readings][city]" and optional=true) and
    column.clouds=(type=float and value="bring [readings][clouds]" and optional=true) and
    column.humidity=(type=float and value="bring [readings][humidity]" and optional=true) and
    column.pressure=(type=float and value="bring [readings][pressure]" and optional=true) and
    column.temperature=(type=float and value="bring [readings][temperature]" and optional=true) and
    column.visibility=(type=float and value="bring [readings][visibility]" and optional=true) and
    column.wind_speed=(type=float and value="bring [readings][wind_speed]" and optional=true)
)>

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

:mqtt-error:
echo "Failed to deploy MQTT process"
goto end-script
