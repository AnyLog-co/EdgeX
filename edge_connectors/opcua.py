import argparse 
import datetime
import opcua
import os
import sys
import time 


def connect_opcua(conn:str, exception:bool=False)->opcua.client.client.Client:
    """
    Connect to OPCUA client
    :args: 
        conn:str - OPCUA connection info 
    :param: 
        client:opcua.client.client.Client - connection to OPCUA 
        start:time.time.time - process start time 
        boolean:bool - whether to exit while 
        error_msg:list - record of error messages 
    :return:
        client 
    """
    client = None
    start = time.time() 
    boolean = False 

    while boolean is False:
        try:
            client = opcua.Client("opc.tcp://%s/" % conn)
            client.connect()
        except Exception as error:
            if exception is True:
                print(f'Failed to connect to OPCUA {conn} (Error: {error})')
        else:
            if time.time() > (start * 3605) and conn is None:
                boolean = True
                if exception is True:
                    print(f'Failed to connect to OPCUA {conn} (Error: Connection over 1 hour)')
            elif conn is None:
                time.sleep(30)
            else:
                boolean = True

    return client


def disconnect_opcua(conn:str, client:opcua.client.client.Client, exception:bool=False)->bool:
    """
    Disconnect from OPCUA
    :args:
        client:opcua.client.client.Client - connection to OPCUA
    :param: 
        status:bool 
    :return:
        status 
    """
    status = True 
    try:
        client.disconnect()
    except Exception as error:
        if exception is True:
            print(f'Failed to disconnect from OPCUA {conn} (Error: {error}))')
        status = False

    return status


def get_opcua_data(client:opcua.client.client.Client, tag:str, exception:bool=False)->dict:
    """
    Extract data from logger
    :args: 
        client:opcua.client.client.Client - connection to OPCUA
        tag:str - OPCUA tag to get data for
        tag:str - tag to get data from OCPUA
        exception:bool - whether or not to print error messages
    :param:
        output - content from OPCUA device
    :return: 
        OPCUA content for a given tag
    """
    try:
        output = client.get_node("ns=4;s=%s" % tag)
    except Exception as e:
        if exception is True:
            print('Failed to get data for %s (Error: %s)' % (tag, e))
    else:
        try:
            return output.get_value()
        except Exception as e:
            if exception is True:
                print('Failed to get value for %s data (Error: %s)' % (tag, e))



def main(): 
    """
    The following is an example of how to pull data from an OPCUA. Tested against the Ai-Ops krt-DataLogger.service 
    :links: 
    --> Test Tools: https://opcfoundation.org/developer-tools/certification-test-tools/opc-ua-compliance-test-tool-uactt/
    --> OPCUA documentation: https://python-opcua.readthedocs.io/en/latest/
    --> Sample code: https://github.com/FreeOpcUa/python-opcua/tree/master/examples
    :args: 
        conn    OPCUA connection info   [default: 192.168.50.19:4840]
        tags    OPCUA list of tags      [sample list: FIC11_FB.fActualValue,FIC11_FB.fActualValue,FIC11_FB.fSetpointValue,FIC11_FB.FIC11.fOut]
   :param: 
        client:opcua.client.client.Client - connection to the OPCUA 
        tags:list - list of tags based based on user input 
        data:dict - data from DataLogger 
        timestamp:str - timestamp for data from DataLogger 
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('conn', type=str, help='OPCUA connection info [default: 192.168.50.19:4840]')
    parser.add_argument('store_format', type=str, choices=['print', 'file', 'put', 'post', 'mqtt'])
    parser.add_argument('--tags', type=str, default=None,help='List of OPCUA tag names')
    parser.add_argument('--db-name', type=str, default='test', help='logical database to store data in')
    parser.add_argument('--table-name', type=str, default=None, help='table to store data in')
    parser.add_argument('--generate-timestamp', type=bool, const=True, nargs='?', default=False, help='Whether or not to include UTC timestamp in generated data')
    parser.add_argument('--storage-conn', type=str, default=None, help='Connection information (IP:Port) or file path to store data in')
    parser.add_argument('--topic', type=str, default=None, help='POST & MQTT topic')
    parser.add_argument('--auth', type=str, default=None, help='Authentication information for sending data out (user:passwd)')
    parser.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Whether or not to print exceptions')
    args = parser.parse_args() 

    if args.tags is None:
        print('Tags cannot be an empty string') 
        exit(1)

    try: 
        tags = list(args.tags.split(','))
    except Exception as e:
        print('Failed to convert tags into a list of tags (Error: %s)' % e)
        exit(1) 

    if args.timestamp is True:
        utc_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    client = connect_opcua(args.conn)
    for tag in tags:
        data = get_opcua_data(client, tag)
        data['timestamp'] = utc_timestamp
        data['dbms'] = args.dbms
        data['table'] = args.table_name
        if data['table'] is None:
            data['table'] = tag
        # send data
    disconnect_opcua(client)

    # send data



if __name__ == '__main__': 
    main()
