""" use telemetry to measure ux key bindings """
import azure.cli.core.telemetry_upload as telemetry_core
import azure.cli.core.telemetry as telemetry

class Telemetry(telemetry.TelemetrySession):
    """ base telemetry sessions """
    keys = []

_session = Telemetry()

def key_bindings(key):
    """ measure key bindings """
    _session.keys.append(key)
