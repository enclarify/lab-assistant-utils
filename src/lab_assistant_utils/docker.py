import os
import json


class DockerRunOptionsBuilder(object):
    def __init__(self):
        self.workspace = '/workspace'
        self.options = set()

    def with_gpu(self) -> 'DockerRunOptionsBuilder':
        self.options.add('--gpus all')
        return self

    def with_privileged(self) -> 'DockerRunOptionsBuilder':
        self.options.add('--privileged')
        return self

    def with_add_devices(self) -> 'DockerRunOptionsBuilder':
        self.options.add('-v /dev:/dev')
        self.with_privileged()
        return self

    def with_display(self, display) -> 'DockerRunOptionsBuilder':
        self.options.add(f'-e DISPLAY={display}')
        self.options.add('-e QT_X11_NO_MITSHM=1')
        self.options.add('-v /tmp/.X11-unix:/tmp/.X11-unix:ro')
        return self

    def with_shared_memory(self) -> 'DockerRunOptionsBuilder':
        self.options.add(f'--ipc=host')
        self.with_add_devices()
        return self

    def with_network(self, network_name: str) -> 'DockerRunOptionsBuilder':
        self.options.add(f'--network={network_name}')
        return self

    def with_tracing(self, tracing_host: str, tracing_port: str) -> 'DockerRunOptionsBuilder':
        self.options.add(f'-e OTEL_EXPORTER_JAEGER_AGENT_HOST={tracing_host}')
        self.options.add(f'-e OTEL_EXPORTER_JAEGER_AGENT_PORT={tracing_port}')
        return self

    def with_kernel_ports(self, connection: str) -> 'DockerRunOptionsBuilder':
        with open(connection, 'r') as cxn_fp:
            connection_params = json.load(cxn_fp)
            connection_params['ip'] = '0.0.0.0'

            control_port = connection_params['control_port']
            shell_port = connection_params['shell_port']
            stdin_port = connection_params['stdin_port']
            hb_port = connection_params['hb_port']
            iopub_port = connection_params['iopub_port']

        with open(connection, 'w') as cxn_fp:
            updated_connection = json.dumps(connection_params)
            cxn_fp.write(updated_connection)

        self.options.add(f'-p {control_port}:{control_port}')
        self.options.add(f'-p {shell_port}:{shell_port}')
        self.options.add(f'-p {stdin_port}:{stdin_port}')
        self.options.add(f'-p {hb_port}:{hb_port}')
        self.options.add(f'-p {iopub_port}:{iopub_port}')
        self.options.add(f'-v {connection}:{connection}')
        return self

    def with_project_volumes(self, project_name) -> 'DockerRunOptionsBuilder':
        self.options.add(f'-v {os.path.join(self.workspace, project_name, "data")}:/data')
        self.options.add(f'-v {os.path.join(self.workspace, project_name)}:/{project_name}')
        return self

    def with_user(self, uid: int, gid: int) -> 'DockerRunOptionsBuilder':
        self.options.add(f'--user {uid}:{gid}')
        return self

    def build(self):
        return ' '.join(self.options)

