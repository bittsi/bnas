# Staging

## Description
For system integration projects there is a need to stage the switches first in a lab before shipping to the customer. The switches will be connected on the console port to a terminalserver and on the out-of-band interface to our lab environment.
There are three staging racks in place. Therefore the staging rack has to be defined with the playbook "setup_infrastructure.yml". After that the playbook "staging.yml" can be used to generate the configs and to load them on the new switches.

The playbook "staging.yml" does the following:
- Generates switch configurations (initial config and full config) -> tag "generate"
- Prepares the switches for SSH connections (connects via terminalserver) and gets the switches ready for config replacement (e.g. archive flash, remove certificate) -> tag "prepare"
- Replaces the initial config on the switches (the replacement file must be a complete configuration) -> tag "replace"
- Merges the full config on the switches and saves the running config as a backup config afterwards-> tag "merge"
- Verifies that the current running config is equal to the original running config (saved right after merge operation) -> tag "verify"


The above listed jobs are defined in playbooks. Each of these playbooks can be run individually or invoked with tags (see [Usage](#usage)).

## Dependencies
To configure the devices the playbook "setup_infrastructure.yml" must have been run before playbook "staging.yml".

## Slack Integration
Just for fun there is custom callback plugin for slack (custom_slack.py) in the folder "callback_plugins". To enable the plugin and to specify the depth of the output messages use extra-vars (see [Slack usage](#slack-usage)).

## Usage
### Run this playbook first
`ansible-playbook setup_infrastructure.yml`

### Overwrite default username and password for terminalserver
`ansible-playbook staging.yml --extra-vars "ts_username=name ts_password=pwd"`

### Run only playbook "generate" for all switches
`ansible-playbook staging.yml --tags "generate"`

### Do not run playbook "generate" but all other playbooks for all switches
`ansible-playbook staging.yml --skip-tags "generate"`

### Do not run playbooks "generate" and "prepare" but all other playbooks for all switches
`ansible-playbook staging.yml --skip-tags "generate,prepare"`

### Run all playbooks for access-switches
`ansible-playbook staging.yml --limit "access"`

### Run only playbook "generate" for access-switches
`ansible-playbook staging.yml --tags "generate" --limit "access"`

### Run playbooks "generate" and "merge"  for a single switch with credentials for terminalserver specified
`ansible-playbook staging.yml --tags "generate,merge" --limit "test_48_3-1" --extra-vars "ts_username=name ts_password=pwd"`

## Slack usage
### Environment variables
**Mandatory:**

`export SLACK_WEBHOOK_URL=<webhook_url>`

**Optional:**

`export SLACK_CHANNEL=<channel>`

`export SLACK_INVOCATION=True`


### Enable Slack plugin
`ansible-playbook staging.yml --extra_vars "callback=slack"`

### Enable Slack plugin and display more details

`ansible-playbook staging.yml --extra-vars "callback=slack slack_details=True"`


