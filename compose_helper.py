#!/usr/bin/env python3
import argparse
import configparser
import os
import shlex

import sys

import subprocess

COMPOSE_SERVICE_SPECIFIC = (
    'exec', 'run', 'scale',
)

COMPOSE_CHOICES = (
    'build', 'bundle', 'config', 'create', 'down', 'events', 'exec', 'help', 'kill', 'logs', 'pause', 'port', 'ps',
    'pull', 'push', 'restart', 'rm', 'run', 'scale', 'start', 'stop', 'unpause', 'up', 'version',
)

COMMAND_CHOICES = COMPOSE_CHOICES + (
    'migrate', 'ssh',
)

DEFAULT_CMD = 'up'

CONFIG_DIR = os.path.expanduser('~/.compose_helper')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, 'config')


class ComposeHelper:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("command", help="Command to run on given app",
                                 default=DEFAULT_CMD, type=str)
        self.parser.add_argument("--compose", help="Path to docker-compose file")
        self.parser.add_argument("-s", "--service", dest='service', type=str,
                                 help="Compose service to target. Defaults to 'default_service' at the config file")
        self.parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments for running command")
        self.args = self.parser.parse_args()

        self.app = os.path.split(sys.argv[0])[1]
        if not os.path.exists(CONFIG_FILE_PATH):
            raise FileNotFoundError("Config file {} not found.".format(CONFIG_FILE_PATH))

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH)

        self.project_dir = self.config[self.app].get('project_dir', os.getcwd())
        self.default_service = self.config[self.app].get('default_service', None)

    def get_app_path(self, app: str) -> str:
        """
        Gets the base directory to app, using config file at ~/.compose_helper/config
        :param app: app to lookup
        :return: full path of the app directory.
        """
        if 'project_dir' not in self.config[self.app]:
            raise KeyError("'project_dir' not defined at {}.".format(CONFIG_FILE_PATH))

        app_dir = os.path.abspath(self.config[app]['project_dir'])
        if not os.path.exists(app_dir):
            raise FileNotFoundError("Application '{}' could not be found at {}.".format(app, app_dir))

        return app_dir

    def get_docker_compose(self):
        if self.args.compose:
            return self.args.compose
        else:
            return os.path.join(self.get_app_path(self.app), "docker-compose.yml")

    def migrate(self):
        cmd = shlex.split("docker-compose -f {} run migrate".format(self.get_docker_compose()))
        cmd.extend(self.args.args)
        return cmd

    def shell(self):
        cmd = shlex.split("docker-compose -f {} run app shell".format(self.get_docker_compose()))
        cmd.extend(self.args.args)
        return cmd

    def docker_compose(self, compose_command):
        cmd = shlex.split("docker-compose -f {} {}".format(self.get_docker_compose(), compose_command))

        if self.args.service:
            service = self.args.service
        elif self.default_service:
            service = self.default_service
        else:
            service = None

        if service:
            if compose_command in COMPOSE_SERVICE_SPECIFIC:
                cmd.append(service)
                cmd.extend(self.args.args)
            else:
                cmd.extend(self.args.args)
                cmd.append(service)

        return cmd

    def not_found(self):
        """
        Helper function when command is not found.
        :return:
        """
        print("Error: Command {} is not supported.".format(self.args.command))
        return -1

    def start(self):
        """
        Main method of the CLI. Executes the related command function on app and returns the exit code of the
        instruction.

        :return:
        """
        cmd = self.args.command

        if cmd in COMPOSE_CHOICES:
            shell_commands = self.docker_compose(cmd)
        elif cmd in COMMAND_CHOICES:
            command_f = getattr(self, cmd, None)
            shell_commands = command_f()
        else:
            return self.not_found()

        print("[DEBUG] Running: {}".format(shell_commands))
        # Run command
        p = subprocess.Popen(args=shell_commands)
        while p.returncode is None:
            try:
                p.wait()
            except KeyboardInterrupt:
                pass
        return p.returncode


if __name__ == '__main__':
    cli = ComposeHelper()
    sys.exit(cli.start())
