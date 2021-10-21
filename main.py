#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from pathlib import Path

from cosmos_parser import CosmosParser, dict2table

stylesheet = "vanilla.css"


def depth(d):
    if (not isinstance(d, dict) or not d):
        return 0
    else:
        return max(depth(v) for _, v in d.items()) + 1


def get_html_recursive(pyobj: dict, recursion_level=0) -> str:
    """get_html_recursive.

    :param pyobj:
    :type pyobj: dict
    :param html:
    :type html: str
    :param recursion_level:
    :rtype: str
    """
    max_depth = 4
    odepth = depth(pyobj)

    if odepth < max_depth:
        html = dict2table(pyobj)
    else:
        html = str()

        for key, value in pyobj.items():

            if isinstance(value, dict):
                hlevel: str = str(recursion_level + 1)
                html += "<h" + hlevel + ">" + key + "</h" + hlevel + ">" + "\n"
                html += get_html_recursive(value, recursion_level + 1)
            else:
                html += get_html_recursive({key: value}, recursion_level + 1)

    return html


def get_html(pyobj: dict) -> str:
    go_back = '<a href="../index.html">Go back...</a>'
    start = '<html><head><link rel="stylesheet" href="../' + stylesheet + '"></head><body>' + go_back
    end = go_back + '</body></html>'

    return start + get_html_recursive(pyobj) + end


def main() -> int:
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument('--project',
                            help="Project to work on",
                            required=True)
    argsparser.add_argument('--output',
                            help="Output directory to work on",
                            required=True)
    args = argsparser.parse_args()
    project = args.project
    output = args.output
    should_link: dict[str, bool] = {'global': True, 'cosmos-rules': True, 'sites': True}
    index_links: dict[str, list[str]] = {'global': ['cosmos-rules', 'global'], 'sites': ['sites']}

    def mkdir(path: str) -> None:
        pathlib_path = Path(os.path.join(output, path))
        pathlib_path.mkdir(parents=True, exist_ok=True)

    def print_index(pyobj: dict, path: str):
        full_path = os.path.join(output, path)
        with open(os.path.join(full_path, 'index.html'), 'w') as html_file:
            html_file.write(get_html(pyobj))

    cosmosparser = CosmosParser(project)

    if not os.path.isdir(output):
        if os.path.isfile(output):
            print("{} is a file rather than a directory, bailing out.".format(
                output))

            return 1
        mkdir('')
    shutil.copyfile("./vanilla.css", os.path.join(output, "vanilla.css"))

    index_links['hosts'] = list()

    for host in cosmosparser.get_hosts():
        host_dict = cosmosparser.get_dict_for_dir(host)
        should_link[host] = False

        if host_dict:
            should_link[host] = True
            mkdir(host)
            print_index(host_dict, host)
        index_links['hosts'].append(host)

    index_links['common'] = list()

    for common in cosmosparser.get_common_dirs():
        common_dict = cosmosparser.get_dict_for_dir(common)
        should_link[common] = False

        if common_dict:
            should_link[common] = True
            mkdir(common)
            print_index(common_dict, common)
        index_links['common'].append(common)

    for global_dir in [cosmosparser.global_dir, "cosmos-rules", 'sites']:
        mkdir(global_dir)

    print_index(cosmosparser.get_dict_for_dir(cosmosparser.global_dir),
                cosmosparser.global_dir)
    cosmos_rules = cosmosparser.get_dict_for_dir("global/overlay/etc/puppet",
                                                 override_hiera_path=True)
    sites:list[str] = list()
    for key, value in cosmos_rules.items():
        for inner_key, inner_value in value.items():
            if inner_key == "sunet::frontend::register_sites":
                for site, _ in inner_value['sites'].items():
                    link = '<a href="https://{0}">{0}</a>'.format(site)
                    if link not in sites:
                        sites.append(link)

            elif inner_key == "sunet::frontend::register_sites_array":
                for site, in inner_value['sites']:
                    link = '<a href="https://{0}">{0}</a>'.format(site)
                    if link not in sites:
                        sites.append(link)

    sites.sort()
    print_index(cosmos_rules, "cosmos-rules")
    print_index({'Manged sites':sites}, "sites")

    html = '<html><head><link rel="stylesheet" href="' + stylesheet + '"></head><body><h1>Welcome</h1><p>Welcome Cosmonaut, please go ahead and explore the Cosmos</p>'
    keys = list(index_links.keys())
    keys.sort()
    for key in keys:
        html += "<h2>" + key.capitalize() + "</h2><ul>"

        for value in index_links[key]:
            if should_link[value]:
                html += '<li><a href="' + value + '/index.html">' + value + '</a></li>'
            else:
                html += '<li>' + value + '</li>'
        html += "</ul>"
    html += "</body></html>"

    with open(os.path.join(output, 'index.html'), 'w') as main_index:
        main_index.write(html)

    return 0


if __name__ == "__main__":
    sys.exit(main())
