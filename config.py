# This Python file uses the following encoding: utf-8
#
# config
# Copyright (c) 2016 Shenghua Su
#

# -------------------------------------------------------------------------------------
# working env
WORKING_PATH                               = 'fullPahtOfThisDirectory'

# -------------------------------------------------------------------------------------
# mqtt
CA_FILE                                    = ''.join([WORKING_PATH, 'ca/ca.crt'])
MQTT_BROKER                                = 'someserver.com'
MQTT_BROKER_PORT                           = 8883

# -------------------------------------------------------------------------------------
# mqtt firmware updater
DESCRIPTION_FILE_NAME                      = 'SensorApp.des'
BIN_FILE_NAME                              = 'SensorApp.bin'
FIRMWARE_FILE_FOLDER                       = ''.join([WORKING_PATH, 'firmware'])
DESCRIPTION_FILE                           = ''.join([WORKING_PATH, DESCRIPTION_FILE_NAME])
BIN_FILE                                   = ''.join([WORKING_PATH, BIN_FILE_NAME])

FIRMWARE_UPDATER_LISTENING_TOPIC_COUNT     = 2
APP_UPDATE_TOPIC                           = 'api/update'
APP_UPDATE_TOPIC_HEAD                      = ''.join([APP_UPDATE_TOPIC, '/'])
APP_UPDATE_TOPIC_DTX                       = '/dtx'
APP_UPDATE_TOPIC_DRX                       = '/drx'
APP_UPDATE_TOPIC_RET_STR                   = 'api/updaters'

VERIFY_CMD                                 = 0xFFFFFFFF
TX_BUFFER_SIZE                             = 8192
