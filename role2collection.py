#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) 2020 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
import os
import re
import shutil
from pathlib import Path

import yaml

# This list should not container files/dirs for 3rd party tools
# Use --extra-path for additional paths
ROLE_PATHS = set((
    'defaults',
    'files',
    'handlers',
    'meta',
    'tasks',
    'templates',
    'tests',
    'vars',
    'README',
    'README.md',
    'LICENSE',
    'LICENSE.txt',
))

PLUGINS = frozenset((
    'action_plugins',
    'become_plugins',
    'cache_plugins',
    'callback_plugins',
    'cliconf_plugins',
    'connection_plugins',
    'doc_fragments',
    'filter_plugins',
    'httpapi_plugins',
    'inventory_plugins',
    'library',
    'lookup_plugins',
    'module_utils',
    'netconf_plugins',
    'shell_plugins',
    'strategy_plugins',
    'terminal_plugins',
    'test_plugins',
    'vars_plugins',
))

IMPORT_RE = re.compile(
    br'(\bimport) (ansible\.module_utils\.)(\S+)(.*)$',
    flags=re.M
)
FROM_RE = re.compile(
    br'(\bfrom) (ansible\.module_utils\.?)(\S+)? import (.+)$',
    flags=re.M
)

BAD_NAME_RE = re.compile(r'[^a-zA-Z0-9_]')


def dir_to_plugin(v):
    if v[-8:] == '_plugins':
        return v[:-8]
    elif v == 'library':
        return 'modules'
    return v


parser = argparse.ArgumentParser()
parser.add_argument(
    '--extra-path',
    default=[],
    action='append',
    help='Extra role relative file/directory path to keep with the role. '
         'May be supplied multiple times',
)
parser.add_argument(
    'path',
    type=Path,
    metavar='ROLE_PATH',
    help='Path to a role to migrate',
)
parser.add_argument(
    'output',
    type=Path,
    metavar='COLLECTION_PATH',
    help='Path to collection where role should be migrated',
)
args = parser.parse_args()

path = args.path.resolve()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)

base = os.path.commonpath([path, output])

ROLE_PATHS.update(args.extra_path)

try:
    meta = path / 'meta'
    for main in ('main.yml', 'main.yaml', 'main.json'):
        if (meta / main).exists():
            break
    else:
        raise RuntimeError('no meta/main.yml')
    role_meta = yaml.safe_load((meta / main).read_text())
    role_name = role_meta['galaxy_info']['role_name']
except Exception as e:
    role_name = path.name.split('.')[-1]

# Normalize the role name
coll_role_name = re.sub(
    '_+',
    '_',
    BAD_NAME_RE.sub('_', role_name)
)

_extras = set(os.listdir(path)).difference(PLUGINS | ROLE_PATHS)
try:
    _extras.remove('.git')
except KeyError:
    pass
extras = [path / e for e in _extras]

for role_dir in ROLE_PATHS:
    src = path / role_dir
    if not src.exists():
        continue
    dest = output / 'roles' / coll_role_name / role_dir
    print(f'Copying {src.relative_to(base)} to {dest.relative_to(base)}')
    if src.is_dir():
        shutil.copytree(
            src,
            dest,
            symlinks=True,
            dirs_exist_ok=True
        )
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            src,
            dest,
            follow_symlinks=False
        )

for plugin_dir in PLUGINS:
    src = path / plugin_dir
    plugin = dir_to_plugin(plugin_dir)
    if not src.is_dir():
        continue
    dest = output / 'plugins' / plugin
    print(f'Copying {src.relative_to(base)} to {dest.relative_to(base)}')
    shutil.copytree(
        src,
        dest,
        symlinks=True,
        dirs_exist_ok=True
    )

module_utils = []
module_utils_dir = path / 'module_utils'
if module_utils_dir.is_dir():
    for root, dirs, files in os.walk(module_utils_dir):
        for filename in files:
            if os.path.splitext(filename)[1] != '.py':
                continue
            full_path = (Path(root) / filename).relative_to(module_utils_dir)
            parts = bytes(full_path)[:-3].split(b'/')
            if parts[-1] == b'__init__':
                del parts[-1]
            module_utils.append(parts)

additional_rewrites = []


def import_replace(match):
    parts = match.group(3).split(b'.')
    if parts in module_utils:
        if match.group(1) == b'import' and match.group(4) == b'':
            additional_rewrites.append(parts)
            return (
                b'import ..module_utils.%s as %s' % (match.group(3), parts[-1])
            )
        return b'%s ..module_utils.%s%s' % match.group(1, 3, 4)
    return match.group(0)


def from_replace(match):
    try:
        parts3 = match.group(3).split(b'.')
    except AttributeError:
        parts3 = None
    parts4 = match.group(4).split(b'.')
    if parts3 in module_utils:
        return b'%s ..module_utils.%s import %s' % match.group(1, 3, 4)
    if parts4 in module_utils:
        if parts3:
            return b'%s ..module_utils.%s import %s' % match.group(1, 3, 4)
        return b'%s ..module_utils import %s' % match.group(1, 4)
    return match.group(0)


modules_dir = output / 'plugins' / 'modules'
for rewrite_dir in (module_utils_dir, modules_dir):
    if rewrite_dir.is_dir():
        for root, dirs, files in os.walk(rewrite_dir):
            for filename in files:
                if os.path.splitext(filename)[1] != '.py':
                    continue
                full_path = (Path(root) / filename)
                text = full_path.read_bytes()

                new_text = IMPORT_RE.sub(
                    import_replace,
                    text
                )

                new_text = FROM_RE.sub(
                    from_replace,
                    new_text
                )

                for rewrite in additional_rewrites:
                    pattern = re.compile(
                        re.escape(
                            br'ansible.module_utils.%s' % b'.'.join(rewrite)
                        )
                    )
                    new_text = pattern.sub(
                        rewrite[-1],
                        new_text
                    )

                if text != new_text:
                    print('Rewriting imports for {}'.format(full_path))
                    full_path.write_bytes(new_text)
                    additional_rewrites[:] = []


for extra in extras:
    dest = output / extra.name
    print(
        f'Copying {extra.relative_to(base)} to {dest.relative_to(base)}'
    )
    if extra.is_dir():
        shutil.copytree(
            extra,
            dest,
            symlinks=True,
            dirs_exist_ok=True
        )
    else:
        shutil.copy2(
            extra,
            dest,
            follow_symlinks=False
        )
