# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import json
import six
import azure.cli.core.decorators as decorators

DIAGNOSTICS_TELEMETRY_ENV_NAME = 'AZURE_CLI_SHELL_DIAGNOSTICS_TELEMETRY'
INSTRUMENTATION_KEY = '762871d5-45a2-4d67-bf47-e396caf53d9d'

def in_diagnostic_mode():
    """
    When the telemetry runs in the diagnostic mode, exception are not suppressed and telemetry
    traces are dumped to the stdout.
    """
    return bool(os.environ.get(DIAGNOSTICS_TELEMETRY_ENV_NAME, False))


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def upload(data_to_save):
    from applicationinsights import TelemetryClient
    from applicationinsights.exceptions import enable

    client = TelemetryClient(INSTRUMENTATION_KEY)
    enable(INSTRUMENTATION_KEY)

    if in_diagnostic_mode():
        sys.stdout.write('Telemetry upload begins\n')

    try:
        data_to_save = json.loads(data_to_save.replace("'", '"'))
    except Exception as err:  # pylint: disable=broad-except
        if in_diagnostic_mode():
            sys.stdout.write('{}/n'.format(str(err)))
            sys.stdout.write('Raw [{}]/n'.format(data_to_save))

    for record in data_to_save:
        name = record['name']
        raw_properties = record['properties']
        properties = {}
        measurements = {}
        for k in raw_properties:
            v = raw_properties[k]
            if isinstance(v, six.string_types):
                properties[k] = v
            else:
                measurements[k] = v
        client.track_event(record['name'], properties, measurements)

        if in_diagnostic_mode():
            sys.stdout.write('\nTrack Event: {}\nProperties: {}\nMeasurements: {}'.format(
                name, json.dumps(properties), json.dumps(measurements)))

    client.flush()

    if in_diagnostic_mode():
        sys.stdout.write('\nTelemetry upload completes\n')


if __name__ == '__main__':
    # If user doesn't agree to upload telemetry, this scripts won't be executed. The caller should
    # control.
    decorators.is_diagnostics_mode = in_diagnostic_mode
    upload(sys.argv[1])
