#
#  MIT License
#
#  (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#
""" cfs - Configuration Framework Service

This module generates the CLI from the OpenAPI specification, but customizes the
target section of the spec so that multiple groups with individual names and
member lists can be specified on the command line for the create subcommand.

This is accomplished by removing the autogenerated target-groups-members and
target-groups-name options and replacing them with a single target-group
option. A custom callback is provided to gather data from this new option into
a payload for passing on to the API.
"""

# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=line-too-long
import json
import urllib.parse
from collections import defaultdict

import click

from cray.constants import FROM_FILE_TAG
from cray.core import option
from cray.generator import _opt_callback
from cray.generator import generate

CURRENT_VERSION = 'v2'
PRESERVE_VERSIONS = True
SWAGGER_OPTS = {
    'vocabulary': {
        'deleteall': 'deleteall'
    }
}

cli = generate(__file__, condense=False, swagger_opts=SWAGGER_OPTS)

if PRESERVE_VERSIONS:
    cli.commands.update(cli.commands[CURRENT_VERSION].commands)
else:
    cli.commands = cli.commands[CURRENT_VERSION].commands


def setup(cfs_cli):
    """ Sets up all cfs overrides """
    setup_configurations_update(cfs_cli, "v2")
    setup_sessions_create(cfs_cli, "v2")
    remove_sessions_update(cfs_cli, "v2")
    setup_components_update(cfs_cli, "v2")
    setup_many_components_update(cfs_cli, "v2")
    setup_configurations_update(cfs_cli, "v3")
    setup_sessions_create(cfs_cli, "v3")
    remove_sessions_update(cfs_cli, "v3")
    setup_components_update(cfs_cli, "v3")
    setup_many_components_update(cfs_cli, "v3")
    setup_sources(cfs_cli)


# CONFIGURATIONS #

def create_configurations_update_shim(update_callback, patch_callback):
    """ Callback function to custom create our own payload """

    def _decorator(configuration_id, file, update_branches, **kwargs):
        file_name = file['value']
        if file_name:  # pylint: disable=no-else-return
            with open(file['value'], 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
            payload = data
            # Hack to tell the CLI we are passing our own payload; don't generate
            kwargs[FROM_FILE_TAG] = {"value": payload, "name": FROM_FILE_TAG}
            return update_callback(configuration_id=configuration_id, **kwargs)
        elif update_branches['value']:
            return patch_callback(configuration_id=configuration_id, **kwargs)
        else:
            raise Exception(
                'Either --file or --update-branches must be set for updates'
            )

    return _decorator


def setup_configurations_update(cfs_cli, version):
    """ Adds the --file and --update-branches parameters for configuration updates """
    tmp_swagger_opts = {
        'vocabulary': {
            'patch': 'patch'
        }
    }
    tmp_cli = generate(__file__, condense=False, swagger_opts=tmp_swagger_opts)

    update_command = tmp_cli.commands[version].commands['configurations'].commands['update']
    patch_command = tmp_cli.commands[version].commands['configurations'].commands['patch']

    option(
        '--file', callback=_opt_callback, type=str, metavar='TEXT',
        help="A file containing the JSON for a configuration"
             " (Required unless updating branches)"
    )(update_command)
    option(
        '--update-branches', callback=_opt_callback, is_flag=True,
        help="Updates the commit IDs for all configuration layers with branches"
    )(update_command)
    new_params = update_command.params[-2:]
    for param in update_command.params[:-2]:
        if not param.name.startswith('layers_'):
            new_params.append(param)
    update_command.params = new_params
    update_command.callback = create_configurations_update_shim(
        update_command.callback,
        patch_command.callback
    )

    cfs_cli.commands[version].commands['configurations'].commands['update'] = update_command


# SESSIONS #

def remove_sessions_update(cfs_cli, version):
    """
    Update session should only be in the api as it is not user friendly and
    is only used by CFS to update session status.
    """
    del cfs_cli.commands[version].commands['sessions'].commands['update']



def _target_groups_callback(cb):
    """
    Coerce the targets/group members from a comma-separated list to a list of
    mappings. Callback function for the target-groups option.
    """

    def _cb(ctx, param, value):
        groups = []
        for group, members in value:
            members = [m.strip() for m in members.split(',')]
            groups.append({"name": group, "members": members})
        if cb:
            return cb(ctx, param, groups)
        return groups

    return _cb


def _target_images_callback(cb):
    """
    Coerce the targets/group members from a comma-separated list to a list of
    mappings. Callback function for the target-groups option.
    """

    def _cb(ctx, param, value):
        images = []
        for source, result in value:
            images.append({"source_id": source, "result_name": result})
        if cb:
            return cb(ctx, param, images)
        return images

    return _cb


def create_sessions_create_shim(func):
    """ Callback function to custom create our own payload """

    def _decorator(
            target_definition,
            target_group,
            target_image_map,
            tags,
            **kwargs
    ):
        payload = {v['name']: v['value'] for _, v in kwargs.items() if
                   v['value'] is not None}
        payload['target'] = {
            'definition': target_definition["value"],
            'groups': target_group['value'],
            'image_map': target_image_map['value']
        }

        if tags['value']:
            payload['tags'] = {
                tag.split('=')[0].strip(): tag.split('=')[1].strip()
                for tag in tags['value'].split(',')}

        # Hack to tell the CLI we are passing our own payload; don't generate
        kwargs[FROM_FILE_TAG] = {'value': payload, 'name': FROM_FILE_TAG}
        return func(**kwargs)

    return _decorator


GROUP_MEMBERS_PAYLOAD = 'target-groups-members'
GROUP_NAME_PAYLOAD = 'target-groups-name'
GROUPS_PAYLOAD = 'target-group'

IMAGE_MAP_SOURCE_PAYLOAD = 'target-image_map-source_id'
IMAGE_MAP_RESULT_PAYLOAD = 'target-image_map-result_name'
IMAGE_MAP_PAYLOAD = 'target-image-map'


def setup_sessions_create(cfs_cli, version):
    """ Adds the --tags and --target-group parameters for session creates """
    command = cfs_cli.commands[version].commands['sessions'].commands['create']

    # Create a new option which can handle multiple groups with individual names
    # and member lists. `option` acts as a decorator here.
    option(
        '--' + GROUPS_PAYLOAD,
        nargs=2,
        type=click.Tuple([str, str]),
        multiple=True,
        payload_name=GROUPS_PAYLOAD,
        callback=_target_groups_callback(_opt_callback),
        metavar='GROUPNAME MEMBER1[,MEMBER2,MEMBER3,...]',
        help="Group members for the inventory. "
             "Multiple groups can be specified by providing this parameter more than once."
             ""
    )(command)
    option(
        '--' + IMAGE_MAP_PAYLOAD,
        nargs=2,
        type=click.Tuple([str, str]),
        multiple=True,
        payload_name=IMAGE_MAP_PAYLOAD,
        callback=_target_images_callback(_opt_callback),
        metavar='SOURCE_IMAGE_ID RESULTING_IMAGE_NAME',
        help="Mapping of source image IDs to resulting image names for image customization. "
             "Multiple sources and results can be specified by providing this parameter more "
             "than once."
    )(command)
    option(
        '--tags',
        callback=_opt_callback,
        required=False,
        type=str,
        metavar='TEXT',
        help="User-defined tags.  A comma-separated list of key=value"
    )(command)

    # Remove the generated params for the group names and group member lists.
    # Add the new target-groups option.
    new_params = command.params[-3:]
    for param in command.params[:-3]:
        if param.payload_name not in (
                GROUP_MEMBERS_PAYLOAD, GROUP_NAME_PAYLOAD,
                IMAGE_MAP_SOURCE_PAYLOAD, IMAGE_MAP_RESULT_PAYLOAD):
            new_params.append(param)
    # Update the command with the new params
    command.params = new_params
    command.callback = create_sessions_create_shim(command.callback)

def updatemany_data_handler(args):
    """ Handler to override the api action taken for updatemany """
    _, path, data = args
    return "PATCH", path, data

# Many Components
def create_components_updatemany_shim_outer(version: str):
    """ Outer function to pass api version to custom create the payload """
    def create_components_updatemany_shim(func):
        """ Callback function to custom create our own payload """

        def _decorator(filter_ids, filter_status, filter_enabled,
                       filter_config_name, filter_tags, patch,
                       state, tags, enabled, retry_policy,
                       error_count, desired_config, **kwargs):

            payload = defaultdict(dict)
            filters = {
                "ids": filter_ids["value"],
                "status": filter_status["value"],
                "tags": filter_tags["value"],
                "enabled": filter_enabled["value"],
                "config_name": filter_config_name["value"]
            }
            if not any(filters.values()):
                # Need to check as "--filter-enabled false" will reach here
                if not filters["enabled"] in [True, False]:
                    raise Exception('At least one filter must be set for updates.')

            # Add filters to payload
            payload['filters'] = {k: v for k, v in filters.items() if v}

            # Add patch to payload
            payload['patch'] = json.loads(patch["value"]) if patch["value"] else {}
            if enabled["value"] is not None:
                payload['patch']['enabled'] = enabled["value"]
            if state["value"] is not None:
                payload['patch']['state'] = json.loads(state["value"])
            if tags["value"] is not None:
                payload['patch']['tags'] = dict(tag.split('=') for tag in tags["value"].split(','))
            # Add retry_policy, error_count, and desired_config to payload based on api version
            if version == "v2":
                if retry_policy["value"] is not None:
                    payload['patch']['retryPolicy'] = retry_policy["value"]
                if error_count["value"] is not None:
                    payload['patch']['errorCount'] = error_count["value"]
                if desired_config["value"] is not None:
                    payload['patch']['desiredConfig'] = desired_config["value"]
            else:
                if retry_policy["value"] is not None:
                    payload['patch']['retry_policy'] = retry_policy["value"]
                if error_count["value"] is not None:
                    payload['patch']['error_count'] = error_count["value"]
                if desired_config["value"] is not None:
                    payload['patch']['desired_config'] = desired_config["value"]

            # Hack to tell the CLI we are passing our own payload; don't generate
            kwargs[FROM_FILE_TAG] = {'value': payload, 'name': FROM_FILE_TAG}
            return func(data_handler=updatemany_data_handler, **kwargs)

        return _decorator
    return create_components_updatemany_shim

# COMPONENTS #
def create_components_update_shim(func):
    """ Callback function to custom create our own payload """

    def _decorator(component_id, state, tags, **kwargs):
        payload = {v['name']: v['value'] for _, v in kwargs.items() if
                   v['value'] is not None}
        if state['value']:
            payload['state'] = json.loads(state['value'])
        if tags['value']:
            payload['tags'] = {
                tag.split('=')[0].strip(): tag.split('=')[1].strip()
                for tag in tags['value'].split(',')}

        # Hack to tell the CLI we are passing our own payload; don't generate
        kwargs[FROM_FILE_TAG] = {'value': payload, 'name': FROM_FILE_TAG}
        return func(component_id=component_id, **kwargs)

    return _decorator


def setup_many_components_update(cfs_cli, version):
    """ Adds the --filter-ids, --filter-status, --filter-enabled, --filter-config-name options """
    list_command = cfs_cli.commands[version].commands['components'].commands['list']
    update_command = cfs_cli.commands[version].commands['components'].commands['update']
    new_command = type(list_command)("updatemany")

    # Copy attributes from list_command to new_command
    for key, value in list_command.__dict__.items():
        setattr(new_command, key, value)

    cfs_cli.commands[version].commands['components'].commands['updatemany'] = new_command
    new_command.params = []
    default_params = [param for param in update_command.params if not param.expose_value]

    # Define options for the new command
    options = [
        ('--filter-ids', str, "Filter by component IDs. A comma-separated list of component IDs"),
        ('--filter-status', str, "Filter by component status. A comma-separated list of statuses"),
        ('--filter-enabled', bool, "Filter by component enabled status. A boolean value"),
        ('--filter-config-name', str, "Filter by component configuration name. A string value"),
        ('--filter-tags', str, "Filter by component tags. A comma-separated list of key=value"),
        ('--patch', str, "JSON component data applied to all filtered components"),
        ('--state', str, "The component state. Set to [] to clear."),
        ('--tags', str, "User-defined tags. A comma-separated list of key=value"),
        ('--enabled', bool, "A flag indicating if the component should be scheduled for configuration."),
        ('--retry-policy', int, "The number of retries to attempt if the component fails to configure."),
        ('--error-count', int, "The count of unsuccessful configuration attempts."),
        ('--desired-config', str, "A reference to a configuration.")
    ]

    for opt, opt_type, help_text in options:
        option(opt, callback=_opt_callback, required=False,
               type=opt_type, metavar='TEXT', help=help_text)(new_command)

    new_command.params += default_params
    new_command.callback = create_components_updatemany_shim_outer(version)(new_command.callback)


def setup_components_update(cfs_cli, version):
    """ Adds the --state and --tags parameters for component updates """
    command = cfs_cli.commands[version].commands['components'].commands['update']
    option(
        '--state',
        callback=_opt_callback,
        required=False,
        type=str,
        metavar='TEXT',
        help="The component state. Set to [] to clear."
    )(command)
    option(
        '--tags',
        callback=_opt_callback,
        required=False,
        type=str,
        metavar='TEXT',
        help="User-defined tags.  A comma-separated list of key=value"
    )(command)
    new_params = command.params[-2:]
    for param in command.params[:-2]:
        if not param.name.startswith('state_'):
            new_params.append(param)
    command.params = new_params
    command.callback = create_components_update_shim(command.callback)


# SOURCES #
def _encode_source_name(source_name):
    # Quote twice.  One level of decoding is automatically done the API framework,
    # so one level of encoding produces the same problems as not encoding at all.
    source_name = urllib.parse.quote(source_name, safe='')
    source_name = urllib.parse.quote(source_name, safe='')
    return source_name

def create_sources_shim(func):
    """ Callback function to custom create our own payload """
    def _decorator(source_id, **kwargs):
        source_id = {"name": source_id["name"], "value": _encode_source_name(source_id["value"])}
        return func(source_id=source_id, **kwargs)
    return _decorator


def setup_sources(cfs_cli):
    """ Adds the --state and --tags parameters for component updates """
    for command_type in ["update", "delete", "describe"]:
        command = cfs_cli.commands["v3"].commands['sources'].commands[command_type]
        command.callback = create_sources_shim(command.callback)


setup(cli)
