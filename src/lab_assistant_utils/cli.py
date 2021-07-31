#!/usr/bin/env python


import os
from collections import namedtuple
from pathlib import Path
import configparser
from typing import Dict

import click


workspace = os.environ['WORKSPACE']
workspace_data = os.path.join(workspace, 'data')

script_path = os.path.realpath(__file__)
lab_folder = Path(os.path.relpath(script_path, workspace)).parts[0]
lab_workspace = os.path.join(workspace, lab_folder)


base_env = {
    'WORKSPACE': workspace,
    'WORKSPACE_DATA': workspace_data
}


@click.group()
def lab():
    pass


WorkspaceEntryPointMetadata = namedtuple('WorkspaceEntryPointMetadata', ['name', 'value', 'script_name', 'absolute_script_path'])


class WorkspaceCommands(click.MultiCommand):

    def list_commands(self, ctx):
        found_cli_plugins = self._cli_plugin_search()
        plugin_names = []
        if found_cli_plugins:
            plugin_names = list(found_cli_plugins.keys())
            plugin_names.sort()
        return plugin_names

    def get_command(self, ctx, folder):
        found_cli_plugins = self._cli_plugin_search()
        cli_plugin_script_path = found_cli_plugins[folder].absolute_script_path
        with open(cli_plugin_script_path) as f:
            code = compile(f.read(), cli_plugin_script_path, 'exec')
            try:
                ns = {}
                eval(code, ns, ns)
                return ns[found_cli_plugins[folder].script_name]
            except Exception:
                return None

    @classmethod
    def _cli_plugin_search(cls) -> Dict[str, WorkspaceEntryPointMetadata]:
        cli_plugins = {}
        for folder in os.listdir(workspace):
            project_path = os.path.join(workspace, folder)
            setup_cfg_path = os.path.join(project_path, 'setup.cfg')
            if not os.path.exists(setup_cfg_path):
                continue

            setup_cfg = configparser.ConfigParser()
            setup_cfg.read(setup_cfg_path)
            if 'options.entry_points' not in setup_cfg or 'lab_assistant.cli_plugins' not in setup_cfg['options.entry_points']:
                continue

            entry_point = setup_cfg['options.entry_points']['lab_assistant.cli_plugins']
            entry_point_name, entry_point_value = map(lambda x: x.strip('\n '), entry_point.split('='))
            script_path, function_name = entry_point_value.split(':')
            script_path_parts = script_path.split('.')
            script_name = script_path_parts[-1]
            absolute_script_path = cls._find_absolute_script_path(project_path, script_name)
            if not absolute_script_path:
                click.echo(f'Error: project "{folder}" supplies a lab assistant CLI plugin but script "{script_name}" could not be loaded')
                continue

            cli_plugins[entry_point_name] = WorkspaceEntryPointMetadata(
                name=entry_point_name,
                value=entry_point_value,
                script_name=script_name,
                absolute_script_path=absolute_script_path)
        return cli_plugins

    @staticmethod
    def _find_absolute_script_path(project_path: str, script_name: str) -> str:
        script_filename = f'{script_name}.py'
        exclude = {'.git', '.idea', '.ipynb_checkpoints', '__pycache__', '.pytest_cache', 'data'}
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            absolute_script_path = os.path.join(root, script_filename)
            if script_filename in files and os.path.exists(absolute_script_path):
                return absolute_script_path


workspace_commands = WorkspaceCommands(help='Workspace commands')
cli = click.CommandCollection(sources=[lab, workspace_commands])


if __name__ == '__main__':
    cli()
