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
