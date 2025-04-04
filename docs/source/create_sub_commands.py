#!/usr/bin/python3
""" Create basic doc files for any newly created modules

MIT License

(C) Copyright [2020] Hewlett Packard Enterprise Development LP

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
import os
import sys

GROUP_DIR = os.path.join(os.getcwd(), sys.argv[1], 'groups')
MODULE_DIR = os.path.join(os.getcwd(), '../cray/modules')


def is_valid_module(module_dir, name):
    """ Make sure path is a valid module directory """
    if not os.path.isdir(os.path.join(module_dir, name)) or name[0] == '_':
        return False
    return True


def filename(name):
    """ Get filename without extension"""
    return os.path.splitext(name)[0]


def get_modules(path, base_name=None):
    """ Determine what modules are missing doc files"""
    name = []
    if base_name is not None:
        name.append(base_name)
    modules = []
    for file in os.listdir(path):
        if is_valid_module(path, file):
            importer = ".modules.".join(name + [filename(file)])
            file_name = ".".join(name + [filename(file)])
            modules.append((file_name, importer))
            new_path = os.path.join(path, file, "modules")
            sub_modules = []
            if os.path.exists(new_path):
                sub_modules = get_modules(new_path, file)
            modules = modules + sub_modules
    return modules


def generate_doc_files(module_dir, group_dir, template=None):
    """ Generate basic docs for new modules """

    _template = """
.. click:: cray.modules.{module}.cli:cli
   :prog: cray {cmd}
   :show-nested:
    """

    if template is None:
        template = _template

    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    modules = get_modules(module_dir)

    docs = [filename(i) for i in os.listdir(group_dir)]

    missing = [i for i in modules if i[0] not in docs]

    for missed in missing:
        name = missed[0]
        mod = missed[1]
        cmd = name.replace('.', ' ')
        with open(os.path.join(group_dir, '{}.rst'.format(name)), 'w') as f_p:
            f_p.write(template.format(module=mod, cmd=cmd))


if __name__ == '__main__':
    generate_doc_files(MODULE_DIR, GROUP_DIR)
