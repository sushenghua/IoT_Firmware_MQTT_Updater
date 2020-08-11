 #
 # FirmwareUpdater parse message from protocol layer and response
 # Copyright (c) 2017 Shenghua Su
 #

import config
import os
import sys
import struct
import json
import hashlib
import paho.mqtt.client as paho
from struct import *
from ctypes import *

class FirmwareUpdater:

    def __init__(self):
        self._load_firmwares()
        self._create_tx_buffer()
        self._setup_mqtt()

    def _versionStrToVersionInt(self, versionStr):
        vs = versionStr.split('.')
        vs = reversed(vs)
        weight = 1
        version = 0
        for v in vs:
            version += int(v) * weight
            weight *= 100
        return version

    def _load_firmwares(self):
        firmwares = {}
        for board_ver in os.listdir(config.FIRMWARE_FILE_FOLDER):

            # combined file
            des_file = ''.join([config.FIRMWARE_FILE_FOLDER, '/', board_ver, '/', config.DESCRIPTION_FILE_NAME])
            bin_file = ''.join([config.FIRMWARE_FILE_FOLDER, '/', board_ver, '/', config.BIN_FILE_NAME])

            # file existence test
            if not os.path.exists(des_file):
                print('\x1b[6;30;41m Error: \x1b[0m description file not found: %s' %(des_file))
                sys.exit("program stopped")

            if not os.path.exists(bin_file):
                print('\x1b[6;30;41m Error: \x1b[0m firmware file not found: %s' %(bin_file))
                sys.exit("program stopped")

            # firmware dictionary
            firmware_dict = {}

            # description file
            with open (des_file, mode = 'rb') as file:
                file_description_bytes = bytearray(file.read())
                if len(file_description_bytes) == 0 :
                    print('\x1b[6;30;41m Error: \x1b[0m firmware description file empty: %s' %(des_file))
                    sys.exit("program stopped")
                size, versionStr = struct.unpack('I{}s'.format(len(file_description_bytes)-sizeof(c_int)), file_description_bytes)
                versionInt = self._versionStrToVersionInt(versionStr)
                description = struct.pack('=II', versionInt, size)

                # print "version: {}, versionInt: {}, size: {}".format(versionStr, versionInt, size)
                firmware_dict['size'] = size
                firmware_dict['version_int'] = versionInt
                firmware_dict['version_str'] = versionStr
                firmware_dict['description'] = description

            # print 'board version: {}, firmware: {}'.format(board_ver, firmware_dict)

            # binary file
            with open (bin_file, mode = 'rb') as file:
                file_content = bytearray(file.read())
                file_size = len(file_content)
                # print "cached file size: {}".format(file_size)
                if file_size == 0 :
                    print('\x1b[6;30;41m Error: \x1b[0m firmware file empty: %s' %(bin_file))
                    sys.exit("program stopped")
                if file_size != size:
                    print('\x1b[6;30;41m Error: \x1b[0m firmware file size: %s mismatch with description size: %s' %(file_size, size))
                    sys.exit("program stopped")
                firmware_dict['file_content'] = file_content

            # md5
            md5 = hashlib.md5()
            md5.update(file_content)
            md5_digest = md5.digest()
            md5_size = md5.digest_size
            firmware_dict['md5_digest'] = md5_digest
            firmware_dict['md5_size'] = md5_size

            # save firmware to dict
            firmwares[board_ver] = firmware_dict

        self._firmwares = firmwares

    def _create_tx_buffer(self):
        self._tx_buffer = create_string_buffer(config.TX_BUFFER_SIZE)

    def _setup_mqtt(self):
        self._client = paho.Client(client_id='FirmwareUpdater', clean_session=True, userdata=None, protocol=paho.MQTTv31)
        self._client.tls_set(ca_certs = config.CA_FILE)
        self._client.username_pw_set('username', 'pass')
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_subscribe = self._on_subscribe        
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        # print("Connected with result code " + str(rc))
        print "connection to broker established, start subscribing topics"
        self._client.subscribe(config.APP_UPDATE_TOPIC_RET_STR, qos = 1)
        self._client.subscribe(config.APP_UPDATE_TOPIC, qos = 1)
        self._client.subscribe(config.APP_UPDATE_TOPIC_HEAD + '+' + config.APP_UPDATE_TOPIC_DTX + '/+', qos = 1)
        self._subAckCount = 0;

    def _on_disconnect(self, client, userdata, rc):
        print("disconnection from broker")
        self._subAckCount = 0;

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        # print("Subscribed: " + str(mid) + " " + str(granted_qos))
        self._subAckCount += 1
        if (self._subAckCount == config.FIRMWARE_UPDATER_LISTENING_TOPIC_COUNT):
            print "topic subscription done"
            print "\x1b[6;30;42m Running \x1b[0m start listening ..."

    def _on_message(self, client, userdata, msg):
        # print msg.topic + " " + str(msg.payload)
        if msg.topic == config.APP_UPDATE_TOPIC_RET_STR:
            # print "require version description from mobile app {}".format(msg.payload)
            try:
                payload = json.loads(msg.payload)
                topic = config.APP_UPDATE_TOPIC_RET_STR + payload['uid']
                bdv = payload['bdv']
                if self._firmwares.has_key(bdv):
                    ret = json.dumps({'ver': self._firmwares[bdv]['version_str'], 'sz': self._firmwares[bdv]['size']})
                else:
                    ret = json.dumps({'err': 'unsupported'})
                self._client.publish(topic, ret, qos = 1)
            except ValueError, e:
                # ret = json.dumps({'err': 'this App outdated'})
                # self._client.publish(topic, ret, qos = 1)
                pass

        elif msg.topic == config.APP_UPDATE_TOPIC:
            # print "require binary description"
            payload = json.loads(msg.payload)
            bdv = payload['bdv']
            topic = ''.join([config.APP_UPDATE_TOPIC_HEAD, payload['uid'], config.APP_UPDATE_TOPIC_DRX, '/', bdv])
            # pack_into('HI', self._tx_buffer, 0, 101, self._file_size)
            if self._firmwares.has_key(bdv):
                self._client.publish(topic, self._firmwares[bdv]['description'], qos = 1)

        elif msg.topic.startswith(config.APP_UPDATE_TOPIC_HEAD):
            # print "require bin data block"
            bdv = msg.topic[msg.topic.rfind('/')+1:]
            if len(bdv) == 0 or not self._firmwares.has_key(bdv):
                return

            topic = msg.topic.replace(config.APP_UPDATE_TOPIC_DTX, config.APP_UPDATE_TOPIC_DRX)
            block = unpack('II', msg.payload)
            # print block
            if block[0] < config.VERIFY_CMD:
                ret_bytesarray = bytearray([(block[0] >> i & 0xff) for i in (0,8,16,24)])
                # print unpack('I', ret_bytesarray)
                ret_bytesarray = ret_bytesarray + self._firmwares[bdv]['file_content'][block[0] : block[0]+block[1]]
                # segment = slice(block[0], block[0] + block[1])
                # print 'ret size', len(self._firmwares[bdv]['file_content'][block[0] : block[0]+block[1]])
                self._client.publish(topic, ret_bytesarray, qos = 1)
            else:
                # print 'require verify bytes'
                self._client.publish(topic, self._firmwares[bdv]['md5_digest'], qos = 1)

    def connect_loop(self):
        self._client.connect(config.MQTT_BROKER, config.MQTT_BROKER_PORT)
        self._client.loop_forever()


application = FirmwareUpdater()
application.connect_loop()

