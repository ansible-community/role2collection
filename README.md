# twentytwenty
Tooling to assist in migrating to collections

These tools may cover many common cases, but do not aim to address all cases.

After using these tools, users should manually verify the changes, and may be required to make further changes to produce functional content.

## role2collection

> **_NOTE:_**  This script requires Python 3.8 or newer

### Help

```
usage: role2collection.py [-h] [--extra-path EXTRA_PATH]
                          ROLE_PATH COLLECTION_PATH

positional arguments:
  ROLE_PATH             Path to a role to migrate
  COLLECTION_PATH       Path to collection where role should be migrated

optional arguments:
  -h, --help            show this help message and exit
  --extra-path EXTRA_PATH
                        Extra role relative file/directory path to keep with
                        the role
```

### Example use

```
$ python3.8 role2collection.py --extra-path CONTRIBUTING.md roles/role.name collections/ansible_collections/ns/name
```

### What does this tool do

1. Migrates standard role directories and a few files into a role within a collection:
  * `defaults`
  * `files`
  * `handlers`
  * `meta`
  * `tasks`
  * `templates`
  * `tests`
  * `vars`
  * `README.md` / `README`
  * `LICENSE.txt` / `LICENSE`
  * For any other file or directory you wish to keep with a role use `--extra-path`
1. Migrates plugins from the role into the collection level plugin directories
1. Rewrites `module_utils` imports in `modules` and `module_utils` to support the migration
1. Migrates all other directories or files into the root of the collection

### Notes

1. Does not perform `doc_fragments` rewrites
1. Does not do anything with the `tests` directory, other than keep them with the role
1. Does not modify anything in role YAML files
1. Overwrites duplicate files
1. Does not come with any warranties
