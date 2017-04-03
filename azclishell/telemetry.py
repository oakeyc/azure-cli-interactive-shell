""" use telemetry to measure ux key bindings """

import datetime

from applicationinsights import TelemetryClient
from applicationinsights.exceptions import enable

from azure.cli.core import __version__ as core_version


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


class Telemetry(TelemetryClient):
    """ base telemetry sessions """

    start_time = None
    end_time = None

    def track_ssg(self, gesture, cmd):
        """ track shell specific gestures """
        self.track_event('Shell Specific Gesture', {gesture : cmd})

    def track_key(self, key):
        """ tracks the special key bindings """
        self.track_event('Key Press', {"key": key})

    def start(self):
        """ starts recording stuff """
        self.start_time = str(datetime.datetime.now())

    def conclude(self):
        """ concludings recording stuff """
        self.end_time = str(datetime.datetime.now())
        self.track_event('Run', {'start time' : self.start_time,
                                 'end time' : self.end_time})
        self.flush()


TC = Telemetry(INSTRUMENTATION_KEY)
enable(INSTRUMENTATION_KEY)
my_context(TC)
