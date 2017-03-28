""" use telemetry to measure ux key bindings """
import logging

import azure.cli.core.telemetry_upload as telemetry_core
import azure.cli.core.telemetry as telemetry

from applicationinsights import TelemetryClient
from applicationinsights.logging import LoggingHandler

INSTRUMENTATION_KEY = 'cc625aa7-58b2-40ad-97f7-5fef9395643b'

PRODUCT_NAME = 'azureclishell'
TELEMETRY_VERSION = '0.0.1.1'
# AZURE_CLI_PREFIX = 'Context.Default.AzureCLI.'

TC = TelemetryClient(INSTRUMENTATION_KEY)
TC.track_event('Event', {'foo': 'bar'})
TC.flush()


# set up logging
handler = LoggingHandler(INSTRUMENTATION_KEY)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
my_logger = logging.getLogger('simple_logger')
my_logger.setLevel(logging.DEBUG)
my_logger.addHandler(handler)

# log something (this will be sent to the Application Insights service as a trace)
my_logger.debug('This is a message')

def my_context(tc):
    tc.context.application.id = 'Azure Shell'
    tc.context.application.ver = '0.1.1a20'
    tc.context.user.id = 't-cooka@microsoft.com'
    tc.track_trace('My trace with context')
    tc.flush()

my_context(TC)

# class Telemetry(telemetry.TelemetrySession):
#     """ base telemetry sessions """
#     keys = []

# _session = Telemetry()

# def key_bindings(key):
#     """ measure key bindings """
#     _session.keys.append(key)
