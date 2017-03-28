""" use telemetry to measure ux key bindings """
import logging
import datetime
import sys
import os

import azclishell.telemetry_upload as telemetry_core
# import azure.cli.core.telemetry as telemetry

from applicationinsights import TelemetryClient
from applicationinsights.logging import LoggingHandler

INSTRUMENTATION_KEY = '762871d5-45a2-4d67-bf47-e396caf53d9d'

PRODUCT_NAME = 'azureclishell'
TELEMETRY_VERSION = '0.0.1.1'


def my_context(tc):
    tc.context.application.id = 'Azure Shell'
    tc.context.application.ver = '0.1.1a20'
    tc.context.user.id = 't-cooka@microsoft.com'
    tc.track_trace('My trace with context')
    # tc.flush()

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
        self.track_event('Shell Specific Gesture', gesture, cmd)

    def track_key(self, key):
        """ tracks the special key bindings """
        self.keys.append(key)
        self.track_event('Key Press', key)

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
my_context(TC)

# set up logging
# handler = LoggingHandler(INSTRUMENTATION_KEY)
# handler.setLevel(logging.DEBUG)
# handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
# my_logger = logging.getLogger('simple_logger')
# my_logger.setLevel(logging.DEBUG)
# my_logger.addHandler(handler)

# # log something (this will be sent to the Application Insights service as a trace)
# my_logger.debug('This is a message')
# my_context(TC)
