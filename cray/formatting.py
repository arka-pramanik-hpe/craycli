""" Formatting Module """
# pylint: disable=too-few-public-methods
import json
import toml

import requests
import click
from ruamel import yaml
from cray.echo import echo, LOG_DEBUG


def format_result(result, format_type='json', **kwargs):
    """ Format a given result into the desired format """
    # pylint: disable=broad-except
    if isinstance(result, requests.Response):
        try:
            result = result.json()
        except ValueError:  # pragma: NO COVER
            result = result.text
    if isinstance(result, dict):
        # Some formatters try to reinitialize the object which fails.
        # Cast into native dict to prevent this.
        result = dict(result)
    if isinstance(result, (list, dict)):
        try:
            return _formatter(format_type)(result, **kwargs).parse()
        except Exception as e:
            echo(result, level=LOG_DEBUG)
            echo(e, level=LOG_DEBUG)
            raise click.ClickException("Error parsing results.")
    else:
        return Formatter(result, **kwargs).parse()


def _formatter(format_type):
    if format_type.lower() == 'toml':
        return TOML
    if format_type.lower() == 'yaml':
        return YAML
    return JSON


class _NullStream:  # pylint: disable=no-init
    """ NullStream used for yaml dump """

    def write(self, *args, **kwargs):
        """ Null writer """
        pass

    def flush(self, *args, **kwargs):
        """ Null flusher """
        pass


class Formatter(object):
    """ Base formatter """

    def __init__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs

    def parse(self):
        """ Parse data into formatter format """
        return self.data


class JSON(Formatter):
    """ JSON Formatter """

    def parse(self):
        return json.dumps(self.data, indent=2)


class YAML(Formatter):
    """ YAML Formatter """

    def __init__(self, data, **kwargs):
        Formatter.__init__(self, data, **kwargs)
        self.yaml = None


    def _to_string(self, data):
        self.yaml = data

    def parse(self):
        yaml.YAML().dump(self.data, _NullStream(), transform=self._to_string)
        return self.yaml


class TOML(Formatter):
    """ TOML Formatter """

    def __init__(self, data, **kwargs):
        if isinstance(data, list):
            resp = {}
            # TOML doesn't like lists, so wrap in object
            resp[kwargs.get('name', 'results')] = data
            data = resp
        Formatter.__init__(self, data, **kwargs)

    def parse(self):
        return toml.dumps(self.data)
