# Github Action Helpers

Misc. collection of temporary scripts to aid in triggering Github Actions and then fetching the logs for the triggered action.

These scripts exist since it isn't (yet?) possible to:

* pass parameters to actions via the API
* tail action logs
* get the ID for a triggered action (we have to assume the latest running action is the one we want the logs for)

Since we can't use parameterised actions we use a templating system to write out all combinations of the actions we'd like to use and then use the scripts in the `bin` dir to trigger the actions we want to run.

Further discussion here: https://github.com/cli/cli/issues/1725
