#-----------------------------------------------------------------------------------------------------------------------
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


<run mqtt client where broker=rest and port=32149 and user-agent=anylog and log=false and topic=(
    name=fledge and
    dbms=!default_dbms and
    table="bring [asset]" and
    column.timestamp.timestamp="bring [timestamp]" and
    column.random=(type=float and value="bring [readings][random]" and optional=true)  and
    column.city=(type=str and value="bring [readings][city]" and optional=true) and
    column.clouds=(type=float and value="bring [readings][clouds]" and optional=true) and
    column.humidity=(type=float and value="bring [readings][humidity]" and optional=true) and
    column.pressure=(type=float and value="bring [readings][pressure]" and optional=true) and
    column.temperature=(type=float and value="bring [readings][temperature]" and optional=true) and
    column.visibility=(type=float and value="bring [readings][visibility]" and optional=true) and
    column.wind_speed=(type=float and value="bring [readings][wind_speed]" and optional=true)
)>

