import json
import os
import random
import requests

from paho.mqtt import client


def __dump_data(payloads:dict, indent:int=0, exception:bool=False)->str:
    """
    Given a dictionary convert to JSON-string
    :args:
        payloads:dict - content to convert into JSON-string
        indent:int - JSON formatting
        exception:bool - whether or not to print exception
    :return:
        payloads ad JSON-string
    """
    try:
        return json.dumps(payloads, indent=indent)
    except Exception as error:
        if exception is True:
            print(f'Failed to convert content to JSON dict (Error: {error})')


def print_data(payloads:dict, exception:bool=False):
    """
    Print data to screen
    :args:
        payloads:dict - content to convert into JSON-string
        exception:bool - whether or not to print exception
    :params:
        content:string - JSON-string of payloads
    """
    content = __dump_data(payloads=payloads, indent=4, exception=exception)
    if content is not None:
        print(content)
    else:
        print(payloads)


def file_store(payloads:dict, file_path:str, exception:bool=False):
    """
    Store payloads into file
    :args:
        payloads:dict - content to store
        file_path:str - directory where data would be stored
        exception:str - whether or not to print exceptions
    :params:
        file_name:str - file name
        full_path:str - file_path + file_name
        content:str - JSON string of payloads
    """
    file_name = f"{payloads['dbms']}.{payloads['table']}.0.json"
    full_path = os.path.join(os.path.expandvars(os.path.expanduser(file_path)), file_name)

    del payloads['dbms']
    del payloads['table']

    content = __dump_data(payloads=payloads, exception=exception)

    if not os.path.isfile(full_path):
        try:
            open(full_path, 'w').close()
        except Exception as error:
            if exception is True:
                print(f'Failed to create file {full_path} (Error: {error}')
    if content is not None:
        try:
            with open(full_path, 'a') as f:
                try:
                    f.write(content + "\n")
                except Exception as error:
                    if exception is True:
                        print(f'Failed to write content into {full_path}. (Error: {error}')
        except Exception as error:
            if exception is True:
                print(f'Failed to open file {full_path} to write content. (Error: {error})')


def put_data(payloads:dict, conn:str, auth:str=(), timeout:int=30, exception:bool=False):
    """
    Send data via PUT
    :args:
        payloads:dict - content to send into node
        conn:str - REST connection info (IP:PORT)
        auth:str - authentication information
        timeout:int - REST timeout
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST PUT header
        content:str - payloads as JSON string
        r:requests.PUT - results from REST request
    """
    headers = {
        'type': 'json',
        'dbms': payloads['dbms'],
        'table': payloads['table'],
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    del payloads['dbms']
    del payloads['table']
    content = __dump_data(payloads=payloads, exception=exception)

    if auth is not None:
        auth = tuple(auth.split(':'))
    else:
        auth=()
    try:
        r = requests.put(url=f'http://{content}', headers=headers, data=content, auth=auth, timeout=timeout)
    except Exception as error:
        if exception is True:
            print(f'Failed to send data via PUT against {conn} (Error: {error})')
    else:
        if exception is True and int(r.status_code) != 200:
            print(f'Failed to send data via PUT against {conn} (Network Error: {r.status_code})')


def post_data(payloads:dict, conn:str, topic:str, auth:str=(), timeout:int=30, exception:bool=False):
    """
    Send data via POST
    :args:
        payloads:dict - content to send into node
        conn:str - REST connection info (IP:PORT)
        auth:str - authentication information
        timeout:int - REST timeout
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST PUT header
        content:str - payloads as JSON string
        r:requests.PUT - results from REST request
    """
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }
    content = __dump_data(payloads=payloads, exception=exception)

    if auth is not None:
        auth = tuple(auth.split(':'))
    else:
        auth=()
    try:
        r = requests.post(url=f'http://{content}', headers=headers, data=content, auth=auth, timeout=timeout)
    except Exception as error:
        if exception is True:
            print(f'Failed to send data via POST against {conn} (Error: {error})')
    else:
        if exception is True and int(r.status_code) != 200:
            print(f'Failed to send data via POST against {conn} (Network Error: {r.status_code})')


def mqtt_data(payloads:dict, conn:str, topic:str, auth:str=(), timeout:int=30, exception:bool=False):
    mqtt_client_id = 'python-mqtt-%s' % random.randint(random.choice(range(0, 500)), random.choice(range(501, 1000)))
    broker, port = conn.split(':')
    user, password =  auth.split(':')
    try:
        mqtt_client = client.Client(mqtt_client_id)
    except Exception as error:
        print(f'Failed to set an MQTT client (Error: {error})')

    if mqtt_client is not None and auth != ():
        try:



def main(store_type:str, payloads:dict, conn_info:str, topic:str, auth:str, exception:bool=False):
    """
    Main for selecting storage type
    :args:
        store_type:str - Storage type (print, file, POST, PUT, MQTT)
        payloads:dict - content to store
        conn_info:str - either REST/MQTT connection info or path to storing data
        topic:str - REST POST / MQTT topic
        auth:str - REST / MQTT authentication information
        exception:bool - whether or nto to print exceptions
    """
    if store_type == 'print':
        print_data(payloads=payloads, exception=exception)
    elif store_type == 'file':
        file_store(payloads=payloads, file_path=conn_info, exception=exception)
    elif store_type == 'put':
        put_data(payloads=payloads, conn=conn_info, auth=auth, exception=exception)
    elif store_type == 'post':
        post_data(payloads=payloads, conn=conn_info, auth=auth, exception=exception)
    elif store_type == 'mqtt':
        mqtt_data(payloads=payloads, conn=conn_info, auth=auth, exception=exception)

