 #
 # FirmwareUpdater parse message from protocol layer and response
 # Copyright (c) 2017 Shenghua Su
 #

import config
import os
import sys
import getopt
import struct
import re
import ctypes

bin_file = config.BIN_FILE
version = ''
boardRevision = ''
target_des_file = ''

# parse args
try:
    opts, args = getopt.getopt(sys.argv[1:], "hv:r:b:", ["help", "version=", "boardRevision=" "binfile="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'python gen_description.py -v <version> -r <boardRevision> [-b <binfile>]'
            sys.exit()
        elif opt in ("-v", "--version"):
            if (not re.search(r'[^0-9\.]', arg)):
                version = str(arg)
            else:
                print "version value must be a version number"
                sys.exit()
        elif opt in ("-r", "--boardRevision"):
            if (not re.search(r'[^0-9\.]', arg)):
                boardRevision = str(arg)
            else:
                print "board revision value must be a version number"
                sys.exit()
        elif opt in ("-b", "--binfile"):
            bin_file = arg
            print arg
    if len(version) == 0 or len(boardRevision) == 0:
        print 'arg missed, use following:'
        print 'python gen_description.py -v <version> -r <boardRevision> [-b <binfile>]'
        sys.exit()
except getopt.GetoptError:
    print 'invalid format, use following:'
    print 'python gen_description.py -v <version> -r <boardRevision> [-b <binfile>]'
    sys.exit(2)


# generate descriptions
if os.path.exists(bin_file):
    file_stat = os.stat(bin_file)
    if file_stat.st_size == 0 :
        print('\x1b[6;30;41m Error: \x1b[0m firmware file empty: %s' %(bin_file))
        sys.exit()

    target_path = ''.join([config.FIRMWARE_FILE_FOLDER, '/', boardRevision])
    if not os.path.exists(target_path):
        os.system('mkdir' + ' -p ' + target_path)

    target_bin_file = ''.join([target_path, '/', config.BIN_FILE_NAME])
    os.system('cp ' + bin_file + ' ' + target_bin_file)

    target_des_file = ''.join([target_path, '/', config.DESCRIPTION_FILE_NAME])
    with open(target_des_file, mode = 'wb') as file:
        # data = 
        # cache = bytearray()
        # cache.append(version)
        # cache.append(file_stat.st_size)
        # file.write(cache)

        # file.write(struct.pack('H', version))
        # file.write(struct.pack('I', file_stat.st_size))
        file.write(struct.pack('=I{}s'.format(len(version)), file_stat.st_size, version))
        print "\x1b[6;30;42m Done \x1b[0m version: {}, size: {}".format(version, file_stat.st_size)

else:
    print('\x1b[6;30;41m Error: \x1b[0m firmware file not found: %s' %(bin_file))
    sys.exit()


def versionStrToVersionInt(versionStr):
    vs = versionStr.split('.')
    vs = reversed(vs)
    weight = 1
    version = 0
    for v in vs:
        version += int(v) * weight
        weight *= 100
    return version

def test():
    with open(target_des_file, 'rb') as f:
        b = bytearray(f.read())
        print 'content size:', len(b)
        print 'raw:', repr(b)
        content = struct.unpack('=I{}s'.format(len(b)-ctypes.sizeof(ctypes.c_int)), b)
        print content
        print 'version int:', versionStrToVersionInt(content[1])
        print 'board version:', boardRevision

test()
