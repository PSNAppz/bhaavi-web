import sys
import os
import time
from random import randint
from .TokenBuilder import RtcTokenBuilder


def buildToken(appID, appCertificate, channelName, UID, expireTimeInSeconds):
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds
    token = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, UID, 1, privilegeExpiredTs)
    return token