""" use telemetry to measure ux key bindings """
import logging
import datetime
import sys
import os

import azclishell.telemetry_upload as telemetry_core
from azclishell.telemetry_upload import INSTRUMENTATION_KEY
# import azure.cli.core.telemetry as telemetry

from applicationinsights import TelemetryClient
from applicationinsights.logging import LoggingHandler
from applicationinsights.exceptions import enable

PRODUCT_NAME = 'azureclishell'
TELEMETRY_VERSION = '0.0.1.1'


def my_context(tc):
    tc.context.application.id = 'Azure Shell'
    tc.context.application.ver = '0.1.1a'
    tc.context.user.id = 't-cooka@microsoft.com'
    tc.context.instrumentation_key = INSTRUMENTATION_KEY

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
        TC.track_event('Shell Specific Gesture', {gesture : cmd})
        TC.flush()


    def track_key(self, key):
        """ tracks the special key bindings """
        self.keys.append(key)
        TC.track_event('Key Press', {"key": key})
        TC.flush()

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
        TC.flush()


TC = Telemetry(INSTRUMENTATION_KEY)
enable(INSTRUMENTATION_KEY)
my_context(TC)
TC.track_trace()
# TC.flush()

