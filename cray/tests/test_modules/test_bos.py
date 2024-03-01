#
# MIT License
#
# (C) Copyright 2020-2024 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
""" Test the bos module."""
# pylint: disable=unused-argument
# pylint: disable=invalid-name

import json

from cray.tests.utils import compare_dicts

DEFAULT_BOS_VERSION = 'v2'

BOS_V2_GROUPS = ['applystaged', 'components', 'healthz', 'options', 'sessions',
                  'sessiontemplates', 'sessiontemplatesvalid', 'sessiontemplatetemplate',
                  'v2', 'version']

# helper functions

def bos_url(config, ver=DEFAULT_BOS_VERSION, uri=None) -> str:
    """
    Returns the BOS URL for the specified version and uri.
    If no version is specified, uses the default BOS version.
    """
    base_url = f'{config["default"]["hostname"]}/apis/bos/{ver}'
    if uri is None:
        return base_url
    return f'{base_url}{uri}'

# tests: base

def test_cray_bos_base(cli_runner, rest_mock):
    """ Test cray bos base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos'])
    assert result.exit_code == 0

    outputs = ['Boot Orchestration Service', 'Groups:'] + BOS_V2_GROUPS + ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_list(cli_runner, rest_mock):
    """ Test cray bos list """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config)


def test_cray_bos_v2_base(cli_runner, rest_mock):
    """ Test cray bos v2 base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2'])
    assert result.exit_code == 0

    outputs = ['Groups:'] + BOS_V2_GROUPS + ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_list(cli_runner, rest_mock):
    """ Test cray bos v2 list """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2")

# tests: applystaged

def test_cray_bos_applystaged_base(cli_runner, rest_mock):
    """ Test cray bos applystaged base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'applystaged'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'create']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_applystaged_base(cli_runner, rest_mock):
    """ Test cray bos v2 applystaged base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'applystaged'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'create']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_applystaged_create(cli_runner, rest_mock):
    """ Test cray bos applystaged create command """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'applystaged', 'create', '--xnames', 'foo,bar'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'POST'
    assert data['url'] == bos_url(config, uri='/applystaged')
    compare_dicts(
        { 'xnames': ['foo','bar'] },
        data['body']
    )


def test_cray_bos_v2_applystaged_create(cli_runner, rest_mock):
    """ Test cray bos v2 applystaged create command """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'applystaged', 'create', '--xnames', 'foo,bar'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'POST'
    assert data['url'] == bos_url(config, ver="v2", uri='/applystaged')
    compare_dicts(
        { 'xnames': ['foo','bar'] },
        data['body']
    )


# tests: components

def test_cray_bos_components_base(cli_runner, rest_mock):
    """ Test cray bos components base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'components'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'describe', 'list', 'update', 'updatemany']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_components_base(cli_runner, rest_mock):
    """ Test cray bos v2 components base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'components'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'describe', 'list', 'update', 'updatemany']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_components_updatemany(cli_runner, rest_mock):
    """ Test cray bos v2 components updatemany"""
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'v2', 'components', 'updatemany', '--filter-ids',
         'test1,test2', '--patch', '{}']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PATCH'
    assert data['url'] == bos_url(config, ver="v2", uri='/components')

# tests: healthz

def test_cray_bos_healthz_base(cli_runner, rest_mock):
    """ Test cray bos healthz base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'healthz'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_healthz_base(cli_runner, rest_mock):
    """ Test cray bos v2 healthz base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'healthz'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output

# tests: options

def test_cray_bos_options_base(cli_runner, rest_mock):
    """ Test cray bos options base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'options'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list', 'update']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_options_base(cli_runner, rest_mock):
    """ Test cray bos v2 options base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'options'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list', 'update']
    for txt in outputs:
        assert txt in result.output

# tests: sessions

def test_cray_bos_sessions_base(cli_runner, rest_mock):
    """ Test cray bos session base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions'])
    assert result.exit_code == 0

    outputs = ['Groups:', 'status', 'Commands:', 'create', 'delete',
               'describe', 'list']
    for txt in outputs:
        assert txt in result.output
    assert 'update' not in result.output


def test_cray_bos_v2_sessions_base(cli_runner, rest_mock):
    """ Test cray bos v2 session base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions'])
    assert result.exit_code == 0

    outputs = ['Groups:', 'status', 'Commands:', 'create', 'delete',
               'describe', 'list']
    for txt in outputs:
        assert txt in result.output
    assert 'update' not in result.output


def test_cray_bos_sessions_delete(cli_runner, rest_mock):
    """ Test cray bos delete session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'delete', 'foo'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'DELETE'
    assert data['url'] == bos_url(config, uri='/sessions/foo')


def test_cray_bos_v2_sessions_delete(cli_runner, rest_mock):
    """ Test cray bos v2 delete session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'delete', 'foo'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'DELETE'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessions/foo')


def test_cray_bos_sessions_list(cli_runner, rest_mock):
    """ Test cray bos list session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessions')


def test_cray_bos_v2_sessions_list(cli_runner, rest_mock):
    """ Test cray bos v2 list session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessions')


def test_cray_bos_sessions_list_filtered(cli_runner, rest_mock):
    """ Test cray bos list session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli,
                           ['bos', 'sessions', 'list',
                            '--status', 'complete',
                            '--max-age', '1d',
                            '--min-age', '1h'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    expected_url_without_params = bos_url(config, uri='/sessions')
    assert data['url'][:len(expected_url_without_params)+1] == f"{expected_url_without_params}?"
    actual_url_param_string = data['url'].split('?')[-1]
    actual_params = {}
    for kvstring in actual_url_param_string.split('&'):
        k, v = kvstring.split('=')
        actual_params[k] = v

    expected_params = {'min_age': '1h',
                       'max_age': '1d',
                       'status': 'complete'}
    compare_dicts(expected_params, actual_params)


def test_cray_bos_v2_sessions_list_filtered(cli_runner, rest_mock):
    """ Test cray bos v2 list session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli,
                           ['bos', 'v2', 'sessions', 'list',
                            '--status', 'complete',
                            '--max-age', '1d',
                            '--min-age', '1h'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    expected_url_without_params = bos_url(config, ver="v2", uri='/sessions')
    assert data['url'][:len(expected_url_without_params)+1] == f"{expected_url_without_params}?"
    actual_url_param_string = data['url'].split('?')[-1]
    actual_params = {}
    for kvstring in actual_url_param_string.split('&'):
        k, v = kvstring.split('=')
        actual_params[k] = v

    expected_params = {'min_age': '1h',
                       'max_age': '1d',
                       'status': 'complete'}
    compare_dicts(expected_params, actual_params)


def test_bad_path_cray_bos_sessions_list_filtered_invalid(cli_runner, rest_mock):
    """ Test cray bos list session with invalid status filter """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli,
                           ['bos', 'sessions', 'list',
                            '--status', 'foo',
                            '--max-age', '1d',
                            '--min-age', '1h'])
    assert result.exit_code != 0
    assert '--status' in result.output


def test_bad_path_cray_bos_v2_sessions_list_filtered_invalid(cli_runner, rest_mock):
    """ Test cray bos v2 list session with invalid status filter """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli,
                           ['bos', 'v2', 'sessions', 'list',
                            '--status', 'foo',
                            '--max-age', '1d',
                            '--min-age', '1h'])
    assert result.exit_code != 0
    assert '--status' in result.output


def test_cray_bos_sessions_describe(cli_runner, rest_mock):
    """ Test cray bos describe session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'describe', 'foo'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessions/foo')


def test_cray_bos_v2_sessions_describe(cli_runner, rest_mock):
    """ Test cray bos v2 describe session """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'describe', 'foo'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessions/foo')


# pylint: disable=redefined-outer-name
def test_cray_bos_sessions_create(cli_runner, rest_mock):
    """ Test cray bos create session ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'sessions', 'create',
         '--template-name', 'foo',
         '--name', 'bar',
         '--limit', 'harf,blah',
         '--stage', 'true',
         '--include-disabled', 'true',
         '--operation', 'boot']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'POST'
    assert data['url'] == bos_url(config, uri='/sessions')
    compare_dicts(
        {
            'template_name': 'foo',
            'name': 'bar',
            'limit': 'harf,blah',
            'stage': True,
            'include_disabled': True,
            'operation': 'boot',
        },
        data['body']
    )


# pylint: disable=redefined-outer-name
def test_cray_bos_v2_sessions_create(cli_runner, rest_mock):
    """ Test cray bos create v2 session ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'v2', 'sessions', 'create',
         '--template-name', 'foo',
         '--name', 'bar',
         '--limit', 'harf,blah',
         '--stage', 'true',
         '--include-disabled', 'true',
         '--operation', 'boot']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'POST'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessions')
    compare_dicts(
        {
            'template_name': 'foo',
            'name': 'bar',
            'limit': 'harf,blah',
            'stage': True,
            'include_disabled': True,
            'operation': 'boot',
        },
        data['body']
    )


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_sessions_create_missing_required(cli_runner, rest_mock):
    """ Test cray bos create session ... when all required parameters are missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'create'])
    assert result.exit_code != 0
    assert '--template-name' in result.output or '--operation' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_v2_sessions_create_missing_required(cli_runner, rest_mock):
    """ Test cray bos v2 create session ... when all required parameters are missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'create'])
    assert result.exit_code != 0
    assert '--template-name' in result.output or '--operation' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_sessions_create_missing_required_template(cli_runner, rest_mock):
    """ Test cray bos create session ... when a required parameter is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'create',
                                 '--operation', 'reboot'])
    assert result.exit_code != 0
    assert '--template-name' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_v2_sessions_create_missing_required_template(cli_runner, rest_mock):
    """ Test cray bos v2 create session ... when a required parameter is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'create',
                                 '--operation', 'reboot'])
    assert result.exit_code != 0
    assert '--template-name' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_sessions_create_missing_required_operation(cli_runner, rest_mock):
    """ Test cray bos create session ... when a required parameter is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'create',
                                 '--template-name', 'foo'])
    assert result.exit_code != 0
    assert '--operation' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_v2_sessions_create_missing_required_operation(cli_runner, rest_mock):
    """ Test cray bos v2 create session ... when a required parameter is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'create',
                                 '--template-name', 'foo'])
    assert result.exit_code != 0
    assert '--operation' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_sessions_create_invalid_operation(cli_runner, rest_mock):
    """ Test cray bos create session ... when an invalid operation is specified
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'create',
                                 '--template-name', 'foo', '--operation', 'bar'])
    assert result.exit_code != 0
    assert '--operation' in result.output


# pylint: disable=redefined-outer-name
def test_bad_path_cray_bos_v2_sessions_create_invalid_operation(cli_runner, rest_mock):
    """ Test cray bos v2 create session ... when an invalid operation is specified
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'create',
                                 '--template-name', 'foo', '--operation', 'bar'])
    assert result.exit_code != 0
    assert '--operation' in result.output

def test_bad_path_cray_bos_sessions_update(cli_runner, rest_mock):
    """ Test cray bos session update -- should not work """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'update'])
    assert result.exit_code != 0


def test_bad_path_cray_bos_v2_sessions_update(cli_runner, rest_mock):
    """ Test cray bos v2 session update -- should not work """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'update'])
    assert result.exit_code != 0

# tests: sessions: status

def test_cray_bos_sessions_status_base(cli_runner, rest_mock):
    """ Test cray bos session status base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'status'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_sessions_status_base(cli_runner, rest_mock):
    """ Test cray bos v2 session status base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'status'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_sessions_status_list(cli_runner, rest_mock):
    """ Test cray bos session status list"""
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'sessions', 'status', 'list', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessions/foo/status')


def test_cray_bos_v2_sessions_status_list(cli_runner, rest_mock):
    """ Test cray bos v2 session status list"""
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'v2', 'sessions', 'status', 'list', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessions/foo/status')


def test_bad_path_cray_bos_sessions_status_list_missing_required_session(
        cli_runner,
        rest_mock
):
    """Test cray bos session status list... when the required Session ID
       parameter missing

    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessions', 'status', 'list'])
    assert result.exit_code != 0
    assert 'SESSION_ID' in result.output


def test_bad_path_cray_bos_v2_sessions_status_list_missing_required_session(
        cli_runner,
        rest_mock
):
    """Test cray bos v2 session status list... when the required Session ID
       parameter missing

    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessions', 'status', 'list'])
    assert result.exit_code != 0
    assert 'SESSION_ID' in result.output

# tests: sessiontemplates

def test_cray_bos_sessiontemplates_base(cli_runner, rest_mock):
    """ Test cray bos sessiontemplates base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessiontemplates'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'create', 'delete', 'describe', 'list', 'update']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_sessiontemplates_base(cli_runner, rest_mock):
    """ Test cray bos v2 sessiontemplates base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessiontemplates'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'create', 'delete', 'describe', 'list', 'update']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_sessiontemplates_delete(cli_runner, rest_mock):
    """ Test cray bos delete sessiontemplates """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'sessiontemplates', 'delete', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'DELETE'
    assert data['url'] == bos_url(config, uri='/sessiontemplates/foo')


def test_cray_bos_v2_sessiontemplates_delete(cli_runner, rest_mock):
    """ Test cray bos v2 delete sessiontemplates """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'v2', 'sessiontemplates', 'delete', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'DELETE'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates/foo')


def test_cray_bos_sessiontemplates_list(cli_runner, rest_mock):
    """ Test cray bos list sessiontemplates """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'sessiontemplates', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessiontemplates')


def test_cray_bos_v2_sessiontemplates_list(cli_runner, rest_mock):
    """ Test cray bos v2 list sessiontemplates """
    runner, cli, config = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessiontemplates', 'list'])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates')


def test_cray_bos_sessiontemplates_describe(cli_runner, rest_mock):
    """ Test cray bos describe sessiontemplate """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'sessiontemplates', 'describe', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessiontemplates/foo')


def test_cray_bos_v2_sessiontemplates_describe(cli_runner, rest_mock):
    """ Test cray bos v2 describe sessiontemplate """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'v2', 'sessiontemplates', 'describe', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates/foo')


def test_cray_bos_sessiontemplates_create(cli_runner, rest_mock):
    """ Test cray bos create sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'sessiontemplates', 'create', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PUT'
    assert data['url'] == bos_url(config, uri='/sessiontemplates/foo')
    compare_dicts(
        {
            'enable_cfs': True
        }, data['body']
    )


def test_cray_bos_v2_sessiontemplates_create(cli_runner, rest_mock):
    """ Test cray bos v2 create sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'v2', 'sessiontemplates', 'create', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PUT'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates/foo')
    compare_dicts(
        {
            'enable_cfs': True
        }, data['body']
    )


def test_cray_bos_sessiontemplates_create_full(cli_runner, rest_mock):
    """ Test cray bos create sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'sessiontemplates', 'create',
         '--enable-cfs', False, '--cfs-configuration',
         'test-config', '--description', 'desc', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PUT'
    assert data['url'] == bos_url(config, uri='/sessiontemplates/foo')
    expected = {
        'enable_cfs': False,
        'cfs': {'configuration': 'test-config'},
        'description': 'desc'
    }
    compare_dicts(expected, data['body'])


def test_cray_bos_v2_sessiontemplates_create_full(cli_runner, rest_mock):
    """ Test cray bos v2 create sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'v2', 'sessiontemplates', 'create',
         '--enable-cfs', False, '--cfs-configuration',
         'test-config', '--description', 'desc', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PUT'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates/foo')
    expected = {
        'enable_cfs': False,
        'cfs': {'configuration': 'test-config'},
        'description': 'desc'
    }
    compare_dicts(expected, data['body'])


def test_cray_bos_sessiontemplates_update(cli_runner, rest_mock):
    """ Test cray bos update sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'sessiontemplates', 'update',
         '--enable-cfs', False, '--cfs-configuration',
         'test-config', '--description', 'desc', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PATCH'
    assert data['url'] == bos_url(config, uri='/sessiontemplates/foo')
    expected = {
        'enable_cfs': False,
        'cfs': {'configuration': 'test-config'},
        'description': 'desc'
    }
    compare_dicts(expected, data['body'])


def test_cray_bos_v2_sessiontemplates_update(cli_runner, rest_mock):
    """ Test cray bos v2 update sessiontemplate ... happy path """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli,
        ['bos', 'v2', 'sessiontemplates', 'update',
         '--enable-cfs', False, '--cfs-configuration',
         'test-config', '--description', 'desc', 'foo']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'PATCH'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplates/foo')
    expected = {
        'enable_cfs': False,
        'cfs': {'configuration': 'test-config'},
        'description': 'desc'
    }
    compare_dicts(expected, data['body'])


def test_bad_path_cray_bos_sessiontemplates_create_missing_required(
        cli_runner,
        rest_mock
):
    """Test cray bos create sessiontemplate ... when a required parameter
    is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessiontemplates', 'create'])
    assert result.exit_code != 0
    assert 'SESSION_TEMPLATE_ID' in result.output


def test_bad_path_cray_bos_v2_sessiontemplates_create_missing_required(
        cli_runner,
        rest_mock
):
    """Test cray bos v2 create sessiontemplate ... when a required parameter
    is missing
    """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessiontemplates', 'create'])
    assert result.exit_code != 0
    assert 'SESSION_TEMPLATE_ID' in result.output

# tests: sessiontemplatesvalid

def test_cray_bos_sessiontemplatesvalid_base(cli_runner, rest_mock):
    """ Test cray bos sessiontemplatesvalid base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessiontemplatesvalid'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'describe']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_sessiontemplatesvalid_base(cli_runner, rest_mock):
    """ Test cray bos v2 sessiontemplatesvalid base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessiontemplatesvalid'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'describe']
    for txt in outputs:
        assert txt in result.output

# tests: sessiontemplatetemplate

def test_cray_bos_sessiontemplatetemplate_base(cli_runner, rest_mock):
    """ Test cray bos sessiontemplatetemplate base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'sessiontemplatetemplate'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_sessiontemplatetemplate_base(cli_runner, rest_mock):
    """ Test cray bos v2 sessiontemplatetemplate base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'sessiontemplatetemplate'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_sessiontemplatetemplate_list(cli_runner, rest_mock):
    """ Test cray bos sessiontemplatetemplate list """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'sessiontemplatetemplate', 'list']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, uri='/sessiontemplatetemplate')


def test_cray_bos_v2_sessiontemplatetemplate_list(cli_runner, rest_mock):
    """ Test cray bos v2 sessiontemplatetemplate list """
    runner, cli, config = cli_runner
    result = runner.invoke(
        cli, ['bos', 'v2', 'sessiontemplatetemplate', 'list']
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data['method'] == 'GET'
    assert data['url'] == bos_url(config, ver="v2", uri='/sessiontemplatetemplate')

# tests: version

def test_cray_bos_version_base(cli_runner, rest_mock):
    """ Test cray bos version base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'version'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output


def test_cray_bos_v2_version_base(cli_runner, rest_mock):
    """ Test cray bos v2 version base command """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli, ['bos', 'v2', 'version'])
    assert result.exit_code == 0

    outputs = ['Commands:', 'list']
    for txt in outputs:
        assert txt in result.output

# verify that v1 is gone

def test_bad_path_cray_bos_v1(cli_runner, rest_mock):
    """ Test cray bos v1 """
    runner, cli, _ = cli_runner
    result = runner.invoke(cli,
                           ['bos', 'v1'])
    assert result.exit_code != 0
