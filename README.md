# twentytwenty
Tooling to assist in migrating to collections

These tools may cover many common cases, but do not aim to address all cases.

After using these tools, users should manually verify the changes, and may be required to make further changes to produce functional content.

## role2collection

> **_NOTE:_**  This script requires Python 3.8 or newer

1. Does not perform `doc_fragments` rewrites
1. Does not do anything with the `tests` directory, other than keep them with the role
1. Does not modify anything in role YAML files
1. Overwrites duplicate files
1. Does not come with any warranties

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
