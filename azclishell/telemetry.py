""" use telemetry to measure ux key bindings """
import logging
import datetime
import sys
import os

# import azclishell.telemetry_upload as telemetry_core
# from azclishell.telemetry_upload import INSTRUMENTATION_KEY

from azure.cli.core import __version__ as core_version

from applicationinsights import TelemetryClient
from applicationinsights.exceptions import enable

INSTRUMENTATION_KEY = '762871d5-45a2-4d67-bf47-e396caf53d9d'
UA_AGENT = "AZURECLI/{}/{}".format(core_version, 'SHELL')
# ENV_ADDITIONAL_USER_AGENT = 'SHELL'

PRODUCT_NAME = 'azureclishell'
TELEMETRY_VERSION = '0.0.1.1'

def my_context(tel_client):
    """ context for the application """
    tel_client.context.application.id = 'Azure Shell'
    tel_client.context.application.ver = '0.1.1a'
    tel_client.context.user.id = 't-cooka@microsoft.com'
    tel_client.context.instrumentation_key = INSTRUMENTATION_KEY

def generate_data():
    """ gets the data to return """
    return ' '.join(TC.keys)

class Telemetry(TelemetryClient):
    """ base telemetry sessions """

    keys = []
    start_time = None
    end_time = None

    def track_ssg(self, gesture, cmd):
        """ track shell specific gestures """
        self.track_event('Shell Specific Gesture', {gesture : cmd})
        # self.flush()


    def track_key(self, key):
        """ tracks the special key bindings """
        self.keys.append(key)
        self.track_event('Key Press', {"key": key})
        # self.flush()

    def start(self):
        """ starts recording stuff """
        self.start_time = datetime.datetime.now()

    def conclude(self):
        """ concludings recording stuff """
        self.end_time = datetime.datetime.now()
        payload = generate_data()
        # if payload:
        #     import subprocess
        #     subprocess.Popen([sys.executable, os.path.realpath(telemetry_core.__file__), payload])
        self.flush()


TC = Telemetry(INSTRUMENTATION_KEY)
enable(INSTRUMENTATION_KEY)
my_context(TC)
# TC.track_trace('Context')
# TC.flush()

