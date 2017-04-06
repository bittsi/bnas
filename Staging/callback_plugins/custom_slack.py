#
# Custom Slack Callback Plugin: Just for fun
# Goal was to have something working and not a comprehensive and reviewed plugin (Try&Error)
#
# Code copied, combined and modified from the following ansible callback plugings:
#  - default.py
#  - slack.py
#  - hipchat.py
#
#  https://github.com/ansible/ansible/tree/devel/lib/ansible/plugins/callback
#
# Invoke ansible-playbook with --extra-vars "callback=slack" to enable the plugin
# Invoke ansible-playbook with --extra-vars "callback=slack" "slack_details=true" to see the plays and the tasks

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import uuid

try:
    from __main__ import cli
except ImportError:
    cli = None

from ansible import constants as C
from ansible.constants import mk_boolean
from ansible.module_utils.urls import open_url
from ansible.plugins.callback import CallbackBase

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False


class CallbackModule(CallbackBase):
    """This is an ansible callback plugin that sends status
    updates to a Slack channel during playbook execution.

    This plugin makes use of the following environment variables:
        SLACK_WEBHOOK_URL (required): Slack Webhook URL
        SLACK_CHANNEL     (optional): Slack room to post in. Default: #ansible
        SLACK_USERNAME    (optional): Username to post as. Default: ansible
                                      details. Default: False

    Requires:
        prettytable

    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'custom_slack'
    CALLBACK_NEEDS_WHITELIST = True



    def __init__(self, display=None):

        self.disabled = False

        if cli:
            self._options = cli.options
        else:
            self._options = None


        #super(CallbackModule, self).__init__()

        super(CallbackModule, self).__init__(display=display)

        if not HAS_PRETTYTABLE:
            self.disabled = True
            self._display.warning('The `prettytable` python module is not '
                                  'installed. Disabling the Slack callback '
                                  'plugin.')

        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.channel = os.getenv('SLACK_CHANNEL', '#ansible')
        self.username = os.getenv('SLACK_USERNAME', 'ansible')
        self.show_invocation = True


#        if self.webhook_url is None:
#            self.disabled = True
#            self._display.warning('Slack Webhook URL was not provided. The '
#                                  'Slack Webhook URL can be provided using '
#                                  'the `SLACK_WEBHOOK_URL` environment '
#                                  'variable.')

        self.playbook_name = None
        self._play = None
        self._last_task_banner = None
        self.playbook = None
        self.extra_vars = None
        self.slack_details = False
        self.bla_url = None

        # This is a 6 character identifier provided with each message
        # This makes it easier to correlate messages when there are more
        # than 1 simultaneous playbooks running
        self.guid = uuid.uuid4().hex[:6]

    def send_msg(self, attachments):
        payload = {
            'channel': self.channel,
            'username': self.username,
            'attachments': attachments,
            'parse': 'none',
        }

        data = json.dumps(payload)
        self._display.debug(data)
        self._display.debug(self.webhook_url)
        try:
            response = open_url(self.webhook_url, data=data)
            return response.read()
        except Exception as e:
            self._display.warning('Could not submit message to Slack: %s' %
                                  str(e))

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        self.playbook = playbook

        self.disabled = True
        
        title = [
            '*PLAYBOOK '
        ]
        self._options = cli.options
        invocation_items = []
        if self._options and self.show_invocation:
            tags = self._options.tags
            skip_tags = self._options.skip_tags
            extra_vars = self._options.extra_vars
            subset = self._options.subset
            inventory = os.path.basename(
                os.path.realpath(self._options.inventory)
            )

            invocation_items.append('Inventory:  %s' % inventory)
            if tags and tags != 'all':
                invocation_items.append('Tags:       %s' % tags)
            if skip_tags:
                invocation_items.append('Skip Tags:  %s' % skip_tags)
            if subset:
                invocation_items.append('Limit:      %s' % subset)
            if extra_vars:
                invocation_items.append('Extra Vars: %s' %
                                      ' '.join(extra_vars))
                
                # set variable if slack_details is set to true
                ev_item = extra_vars[0].split(' ')
                for item in ev_item:
                    if 'slack_details' in item:
                        value = item.split('=')[1]
                        if value.lower() == 'true':
                            self.slack_details = True
                    if 'callback' in item:
                        value = item.split('=')[1]
                        if value.lower() != 'slack':
                            self.disabled = True
                        else:
                            self.disabled = False
                            if self.webhook_url is None:
                                self.disabled = True
                                self._display.warning('Slack Webhook URL was not provided. The '
                                                      'Slack Webhook URL can be provided using '
                                                      'the `SLACK_WEBHOOK_URL` environment '
                                                      'variable.')





        title.append('[%s]' % self.playbook_name)
        title.append('*')

        msg_items = [' '.join(title)]
        if invocation_items:
            msg_items.append('```\n%s\n```' % '\n'.join(invocation_items))

        msg = '\n'.join(msg_items)

        attachments = [{
            'fallback': msg,
            'fields': [
                {
                    'value': msg
                }
            ],
            'color': 'normal',
            'mrkdwn_in': ['text', 'fallback', 'fields'],
        }]

        if self.disabled != True:
            self.send_msg(attachments=attachments)

    def v2_playbook_on_play_start(self, play):
        """Display Play start messages"""


        if self.slack_details == True:
            name = play.name or 'Play name not specified (%s)' % play._uuid
            msg = '*PLAY [%s]*' % name
            attachments = [
                {
                    'fallback': msg,
                    'text': msg,
                    'color': 'normal',
                    'mrkdwn_in': ['text', 'fallback', 'fields'],
                }
            ]
            self._play = play
            self.send_msg(attachments=attachments)


    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        t = prettytable.PrettyTable(['Host', 'Ok', 'Changed', 'Unreachable',
                                     'Failures'])

        failures = False
        unreachable = False

        for h in hosts:
            s = stats.summarize(h)

            if s['failures'] > 0:
                failures = True
            if s['unreachable'] > 0:
                unreachable = True

            t.add_row([h] + [s[k] for k in ['ok', 'changed', 'unreachable',
                                            'failures']])

        attachments = []
        msg_items = [
            '*Playbook Complete* (_%s_)' % self.guid
        ]
        if failures or unreachable:
            color = 'danger'
            msg_items.append('\n*Failed!*')
        else:
            color = 'good'
            msg_items.append('\n*Success!*')

        msg_items.append('```\n%s\n```' % t)

        msg = '\n'.join(msg_items)

        attachments.append({
            'fallback': msg,
            'fields': [
                {
                    'value': msg
                }
            ],
            'color': color,
            'mrkdwn_in': ['text', 'fallback', 'fields']
        })

        self.send_msg(attachments=attachments)


    def v2_runner_on_ok(self, result):
        if self.slack_details == True:
            if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)
    
            self._clean_results(result._result, result._task.action)
    
            delegated_vars = result._result.get('_ansible_delegated_vars', None)
            self._clean_results(result._result, result._task.action)
            if result._task.action in ('include', 'include_role'):
                return
            elif result._result.get('changed', False):
                if delegated_vars:
                    msg = "changed: [%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
                else:
                    msg = "changed: [%s]" % result._host.get_name()
                color = 'warning'
            else:
                if delegated_vars:
                    msg = "ok: [%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
                else:
                    msg = "ok: [%s]" % result._host.get_name()
                color = 'good'
    
            self._handle_warnings(result._result)
    
            if result._task.loop and 'results' in result._result:
                self._process_items(result)
            else:               
                attachments = [
                    {
                       'fallback': msg,
                       'text': msg,
                       'color': color,
                       'mrkdwn_in': ['text', 'fallback', 'fields'],
                    }
                ]
    
                self.send_msg(attachments=attachments)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if self.slack_details == True:
            if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
                self._print_task_banner(result._task)
    
            delegated_vars = result._result.get('_ansible_delegated_vars', None)
    
    
            if result._task.loop and 'results' in result._result:
                self._process_items(result)
    
            else:
                if delegated_vars:
                    self._display.display("fatal: [%s -> %s]: FAILED! => %s" % (result._host.get_name(), delegated_vars['ansible_host'], self._dump_results(result._result)), color=C.COLOR_ERROR)
                else:
                    msg = "fatal: [%s]: FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result))
                    attachments = [
                        {
                           'fallback': msg,
                           'text': msg,
                           'color': 'danger',
                           'mrkdwn_in': ['text', 'fallback', 'fields'],
                        }
                    ]
        
                    self.send_msg(attachments=attachments)
               
        


    def v2_playbook_on_task_start(self, task, is_conditional):
        if self.slack_details == True:
            if self._play.strategy != 'free':
                self._print_task_banner(task)

    def _print_task_banner(self, task):
        # args can be specified as no_log in several places: in the task or in
        # the argument spec.  We can check whether the task is no_log but the
        # argument spec can't be because that is only run on the target
        # machine and we haven't run it thereyet at this time.
        #
        # So we give people a config option to affect display of the args so
        # that they can secure this if they feel that their stdout is insecure
        # (shoulder surfing, logging stdout straight to a file, etc).
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args

        msg = u"TASK [%s%s]" % (task.get_name().strip(), args)
        attachments = [
            {
               'fallback': msg,
               'title': msg,
               'color': 'normal',
               'mrkdwn_in': ['text', 'fallback', 'fields'],
            }
        ]

        self.send_msg(attachments=attachments)

        if self._display.verbosity >= 2:
            path = task.get_path()
            if path:
                msg = "task path: %s" % path
                attachments = [
                    {
                       'fallback': msg,
                       'title': msg,
                       'color': 'warning',
                       'mrkdwn_in': ['text', 'fallback', 'fields'],
                    }
                ]

                self.send_msg(attachments=attachments)
        self._last_task_banner = task._uuid


