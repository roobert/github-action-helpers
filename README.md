# Github Action Helpers

Misc. collection of temporary scripts to aid in triggering Github Actions and then fetching the logs for the triggered action.

These scripts exist since it is (yet?) possible to:
* pass parameters to actions via the API
* tail action logs
* get the ID for a triggered action (we have to assume the latest running action is the one we want the logs for)
