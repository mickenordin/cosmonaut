#!/usr/bin/env python3

import os
import re

import json2table
import yaml


class CosmosParser:
    def __init__(self, project: str) -> None:
        """__init__.

        :param project:
        :type project: str
        :rtype: None
        """
        self.project: str = project
        self.common_dirs: list[str] = discover_common_dirs(self.project)
        self.global_dir: str = "global"
        self.hiera_file_names: list[str] = [
            'common.yaml', 'group.yaml', 'local.yaml', 'cosmos-rules.yaml'
        ]
        self.hiera_data_path: str = "overlay/etc/hiera/data"
        self.hosts: list[str] = discover_hosts(self.project)

    def get_common_dirs(self) -> list[str]:
        """get_common_dirs.

        :rtype: list[str]
        """

        return self.common_dirs

    def get_dict_for_dir(self,
                         directory: str,
                         override_hiera_path=False) -> dict:
        """get_dict_for_dir.

        :param directory:
        :type directory: str
        :param override_hiera_path:
        :rtype: dict
        """

        if override_hiera_path:
            full_dir_path: str = os.path.join(self.project, directory)
        else:
            full_dir_path: str = os.path.join(
                os.path.join(self.project, directory), self.hiera_data_path)
        pyobj: dict = dict()

        if os.path.isdir(full_dir_path):
            for yamlfile in os.listdir(full_dir_path):
                full_file_path: str = os.path.join(full_dir_path, yamlfile)

                if os.path.isfile(full_file_path) and (
                        yamlfile in self.hiera_file_names):
                    pyobj: dict = yaml2dict(full_file_path)

        return pyobj

    def get_hosts(self) -> list[str]:
        """get_hosts.

        :rtype: list[str]
        """

        return self.hosts


def discover_common_dirs(project: str) -> list[str]:
    """discover_common_dirs.

    :param project:
    :type project: str
    :rtype: list[str]
    """
    common_regex: re.Pattern[str] = re.compile(
        r'^(\w{1,})(-common)(-?\w{0,})$')
    common_dirs: list[str] = list()

    if os.path.isdir(project):
        for directory in os.listdir(path=project):
            if common_regex.match(directory):
                if os.path.isdir(os.path.join(project, directory)):
                    common_dirs.append(directory)
        common_dirs.sort()

    return common_dirs


def discover_hosts(project) -> list[str]:
    """discover_hosts.

    :param project:
    :rtype: list[str]
    """
    fqdn_regex: re.Pattern[str] = re.compile(
        r'^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$'
    )
    hosts: list[str] = list()

    if os.path.isdir(project):
        for directory in os.listdir(path=project):
            if fqdn_regex.match(directory):
                if os.path.isdir(os.path.join(project, directory)):
                    hosts.append(directory)
        hosts.sort()

    return hosts


def yaml2dict(path) -> dict:
    """yaml2dict.

    :param path:
    :rtype: dict
    """
    with open(path, 'r') as yaml_doc:
        pyobj: dict = yaml.safe_load(yaml_doc.read())

    return pyobj


def dict2table(pyobj: dict) -> str:
    """dict2table.

    :param pyobj:
    :type pyobj: dict
    :rtype: str
    """

    build_direction: str = "LEFT_TO_RIGHT"
    table_attributes: dict = {"width": "100%"}
    table: str = json2table.convert(pyobj,
                                    build_direction=build_direction,
                                    table_attributes=table_attributes)

    return table
