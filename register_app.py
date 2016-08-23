#!/usr/bin/env python3
import argparse
import configparser
import os

import sys


class RegisterApp:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("app", type=str, help="Application to run")
        self.parser.add_argument("path", type=str, default=".", help="path to project directory. Defaults to '.'")
        self.parser.add_argument("--default", dest="default_service", type=str, default="app", help="default service for run and exec commands")
        self.args = self.parser.parse_args()

    def _mkbinary(self, name, bin_path="/usr/local/bin"):
        """
        Creates a new binary in the system with given "name" by creating a symlink to this file.

        :param app: name of the binary
        :param bin_path: path where to create the binary
        """
        target_file = os.path.join(bin_path, name)
        if os.access(bin_path, os.W_OK):
            if not os.path.exists(target_file):
                os.symlink(os.path.abspath('./compose_helper.py'), target_file)
            else:
                print("Binary already found at {}. Skipping...".format(target_file))
        else:
            raise PermissionError("Permission denied: can't write to {}".format(bin_path))

    def _create_config(self, name, project_dir):
        config_dir = os.path.expanduser("~/.compose_helper")
        config_file = "config"
        config_path = os.path.join(config_dir, config_file)

        if not os.path.exists(config_dir):
            print("Config directory was not found. Creating at {}".format(config_dir))
            os.mkdir(config_dir)

        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)

        if name not in config.sections():
            config.add_section(name)

        config[name]['project_dir'] = project_dir
        config[name]['default_service'] = self.args.default_service

        print("Setting configuration for {}: \n{}".format(
            self.args.app, "\n".join(["{} = {}".format(k, config[name][k]) for k in config[name]])))

        with open(config_path, 'w') as f:
            config.write(f)

    def register(self):
        app = self.args.app
        project_dir = os.path.join(self.args.path)

        # Creating binary link
        self._mkbinary(app)

        # Adding entry to compose_helper config
        self._create_config(app, project_dir)

        return 0


if __name__ == '__main__':
    sys.exit(RegisterApp().register())
