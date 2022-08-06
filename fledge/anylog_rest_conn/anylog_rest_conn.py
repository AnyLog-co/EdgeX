# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge-iot.readthedocs.io/
# FLEDGE_END

""" HTTP North plugin"""

import aiohttp
import asyncio
import json
import os
import logging
import base64

import random
import numpy as np

from fledge.common import logger
from fledge.plugins.north.common.common import *

FILE_PATH=os.path.expandvars(os.path.expanduser('$HOME/data.json'))

__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2022 AnyLog Co."
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)

# https://fledge-iot.s3.amazonaws.com/1.9.2/ubuntu2004/x86_64/fledge-1.9.2_x86_64_ubuntu2004.tgz
http_north = None
config = ""

_CONFIG_CATEGORY_NAME = "AnyLog-Conn"
_CONFIG_CATEGORY_DESCRIPTION = "Send Data via REST into AnyLog"

_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'HTTP North Plugin',
         'type': 'string',
         'default': 'anylog_rest_conn',
         'readonly': 'true'
    },
    'url': {
        'description': 'AnyLog REST connection information (IP:Port)',
        'type': 'string',
        'default': '',
        'order': '1',
        'displayName': 'URL'
    },
    "source": {
         "description": "Source of data to be sent on the stream. May be either readings or statistics.",
         "type": "enumeration",
         "default": "readings",
         "options": [ "readings", "statistics" ],
         'order': '2',
         'displayName': 'Source'
    },
    "verifySSL": {
        "description": "Verify SSL certificate",
        "type": "boolean",
        "default": "false",
        'order': '3',
        'displayName': 'Verify SSL'
    },
    "applyFilter": {
        "description": "Should filter be applied before processing data",
        "type": "boolean",
        "default": "false",
        'order': '4',
        'displayName': 'Apply Filter'
    },
    "filterRule": {
        "description": "JQ formatted filter to apply (only applicable if applyFilter is True)",
        "type": "string",
        "default": ".[]",
        'order': '5',
        'displayName': 'Filter Rule',
        "validity": "applyFilter == \"true\""
    },
    "topicName": {
        "description": "Topic to send data to",
        "type": "string",
        "default": "foglamp",
        "order": "6",
        "displayName": "REST Topic Name"
    },
    "assetList": {
        "description": "Comma separatedd assets to use with this topic",
        "type": "string",
        "default": "",
        "order": "7",
        "displayName": "Asset List"
    },
    "dbName": {
        "description": "Logical database name",
        "type": "string",
        "default": "foglamp",
        "order": "8",
        "displayName": "Database Name"
    }
}


def plugin_info():
    return {
        'name': 'http',
        'version': '1.9.2',
        'type': 'north',
        'mode': 'none',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(data):
    global http_north, config
    http_north = HttpNorthPlugin()
    config = data
    return config


async def plugin_send(data, payload, stream_id):
    # stream_id (log?)
    asset_list = config['assetList']['value'].split(",")
    payloads = [] 
    for p in payload: 
        if p['asset_code'] in asset_list or asset_list is []:
            payloads.append(p) 
    if payloads is not []: 
        try:
            is_data_sent, new_last_object_id, num_sent = await http_north.send_payloads(payloads)
        except asyncio.CancelledError:
            pass
        else:
            return is_data_sent, new_last_object_id, num_sent


def plugin_shutdown(data):
    pass


# TODO: North plugin can not be reconfigured? (per callback mechanism)
def plugin_reconfigure():
    pass


# https://stackoverflow.com/questions/3488934/simplejson-and-numpy-array/24375113#24375113

class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data
        """
        if isinstance(obj, np.ndarray):
            obj_data = np.ascontiguousarray(obj).data
            data_list = obj_data.tolist()
            return dict(__ndarray__=data_list,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        super(NumpyEncoder, self).default(obj)

class NumpyEncoderBase64(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data
        """
        if isinstance(obj, np.ndarray):
            obj_data = np.ascontiguousarray(obj).data
            data_list = base64.b64encode(obj_data)
            if isinstance(data_list, bytes):
                data_list = data_list.decode(encoding='UTF-8')
            return dict(__ndarray__=data_list,
                        dtype=str(obj.dtype),
                        shape=obj.shape)

        # Let the base class default method raise the TypeError
        super(NumpyEncoderBase64, self).default(obj)


class HttpNorthPlugin(object):
    """ North HTTP Plugin """

    def __init__(self):
        self.event_loop = asyncio.get_event_loop()

    async def send_payloads(self, payloads):
        is_data_sent = False
        last_object_id = 0
        num_sent = 0
        try:
            payload_block = list()

            for p in payloads:
                last_object_id = p["id"]
                read = dict()
                read["dbms"] = config['dbName']['value']
                read["asset"] = p['asset_code'].replace(' ','_').replace('/', '_')
                read["readings"] = p['reading']
                for k,v in read['readings'].items():
                    if isinstance(v, np.ndarray):
                        serialized_data_base64 = json.dumps(v, cls=NumpyEncoderBase64)
                        read['readings'][k] = serialized_data_base64

                read["timestamp"] = p['user_ts']
                payload_block.append(read)

            num_sent = await self._send_payloads(payload_block)
            is_data_sent = True
        except Exception as ex:
            _LOGGER.exception("Data could not be sent, %s", str(ex))

        return is_data_sent, last_object_id, num_sent

    async def _send_payloads(self, payload_block):
        """ send a list of block payloads"""

        num_count = 0
        try:
            verify_ssl = False if config["verifySSL"]['value'] == 'false' else True
            connector = aiohttp.TCPConnector(verify_ssl=verify_ssl)
            async with aiohttp.ClientSession(connector=connector) as session:
                result = await self._send(payload_block, session)
        except:
            pass
        else: 
            num_count += len(payload_block)
        return num_count

    async def _send(self,  payload, session):
        """ Send the payload, using provided socket session """
        headers = {
            'command': 'data',
            'topic': config['topicName']['value'],
            'User-Agent': 'AnyLog/1.23',
            'content-type': 'text/plain'
        }
        url = random.choice(config['url']['value'].split(',')).strip() 
        async with session.post(f'http://{url}', data=json.dumps(payload), headers=headers) as resp:
            result = await resp.text()
            status_code = resp.status
            if status_code in range(400, 500):
                _LOGGER.error("Bad request error code: %d, reason: %s", status_code, resp.reason)
                raise Exception
            if status_code in range(500, 600):
                _LOGGER.error("Server error code: %d, reason: %s", status_code, resp.reason)
                raise Exception
            return result
