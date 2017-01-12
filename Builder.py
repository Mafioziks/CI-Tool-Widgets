#!/usr/bin/env python3

from threading import Thread
import os
import webbrowser
import re
import time
import gi
from termcolor import colored
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Gio, Notify, AppIndicator3
from jenkinsapi.jenkins import Jenkins
from pydbus import SessionBus

#import gitlab                   # Neet to test this
from pytest import Config
from TaskList import TaskList


class JenManager(Thread):
    """Jenkins task manager."""

    __env__ = ['git', 'svn']
    builders = list()
    _quit = False

    def __init__(self, threadID, name, q):
        """Initialize JenManager."""
        print(colored('JenManager initialized', 'green'))
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.config = Config()
        self.login_data = self.config.get_login()

    def run(self):
        """Run builders."""
        while (
            not self.tasks.empty() or
            self.tasks.get_with_status('listed') is not None or
            self.has_running_builders() or
            not self._quit
        ):
            task = None
            # Get task for builder which is not active
            for tsk in self.tasks.get_with_status('listed'):
                if not self.has_running_builders():
                    task = tsk
                    break

                for b in self.builders:
                    if 'job' not in tsk:
                        if (b.getName() == 'Deploy.git.branch' and
                                b.is_alive()):
                            print('Still alive')
                            tsk = None

                        print('Setting task 1')
                        task = tsk
                        break

                    elif b.getName() == tsk['job'] and b.is_alive():
                        print('still alive 2')
                        task = None

                    print('Setting task 2')
                    task = tsk
                    break

            # ----------------------------------------

            # if self.has_running_builders():
            #     time.sleep(1)
            #     continue

            # task = self.tasks.get_with_status('listed')
            if task is None or len(task) <= 0:
                time.sleep(1)
                continue

            # task = task[0]
            task_parameters = self.config.get_preset(task['name'])
            parameters = dict()
            job_name = ''

            if 'job' in task:
                job_name = task['job']
                parameters = dict()
                for key in task:
                    if (key != 'job' and
                            key != 'description' and
                            key != 'name' and
                            key != 'recipient' and
                            key != 'status' and
                            key != 'id'):
                        parameters.update({key: task[key]})
            else:
                print('Old...')
                if task_parameters['vcs'].startswith('git'):
                    parameters = {
                        'GIT_URL': task_parameters['vcs'],
                        'JSITE': task_parameters['url'],
                        'JDEPLOY_HOST': task_parameters['deploy'],
                        'JASSETS_DEPLOYMENT_HOST': task_parameters['assets'],
                        'JTAG': task['tag']
                    }

                    job_name = 'Deploy.git.branch'

                    if re.match("^\d+\.\d+\.\d+$", task['tag']) is not None:
                        job_name = 'Deploy.git.tag'
                else:
                    job_name = 'Deploy.svn'
                    parameters = {
                        'JPROJECT': task_parameters['tag'],
                        'JSITE': task_parameters['url'],
                        'JDEPLOY_HOST': task_parameters['deploy'],
                        'JASSETS_DEPLOYMENT_HOST': task_parameters['assets'],
                    }

            b = JenBulder(1, job_name, 1)
            b.set_login_data(
                self.login_data['url'],
                self.login_data['username'],
                self.login_data['password']
            )
            b.set_build_parameters(
                parameters
            )
            b.set_task(self.tasks, task['id'])
            self.tasks.update_task(task['id'], 'queued')
            self.builders.append(b)
            print(self.builders)
            b.start()

        for b in self.builders:
            if b.is_alive():
                b.join()

        return

    def has_running_builders(self):
        """Check if manager has any builders still running."""
        # Thread counting may not work
        if len(self.builders) <= 0:
            return False

        for b in self.builders:
            if b.is_alive():
                return True
            else:
                self.builders.remove(b)

        return False

    def set_task_list(self, tasks):
        """Add task list."""
        self.tasks = tasks

    def quit(self):
        """Set quit."""
        self._quit = True


class JenBulder(Thread):
    """Builder for jenkins."""

    def __init__(self, threadID, name, q):
        """Initialize JenBuilder."""
        print(colored('JenBuider initialized', 'green'))
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        currpath = os.path.dirname(os.path.realpath(__file__))
        self.APP_ICON = currpath+"/Jenkins_logo.png"
        Notify.init('JenBuilder')

    def set_login_data(self, url, username, password):
        """Set login data."""
        self.url = url
        self.username = username
        self.password = password

    def get_server_instance(self):
        """Get server instance."""
        if (not hasattr(self, 'url') or
                not hasattr(self, 'username') or
                not hasattr(self, 'password')):
            print(colored('Missing log in data', 'red'))
            return False

        try:
            self.server = Jenkins(self.url, self.username, self.password)
            return True
        except Exception as ex:
            print(colored(ex, 'red'))
        return False

    def get_job_parameters(self, jobName):
        """Get parameters for job."""
        if not self.get_server_instance():
            print(colored('Server instance not received', 'red'))
            return False

        if not self.server.has_job(jobName):
            print(colored('Job [' + jobName + '] not found', 'red'))
            return False

        return self.server[jobName].get_params_list()

    def set_build_parameters(self, parameters={}):
        """Set build parameters."""
        self.parameters = parameters

    def set_task(self, task, id):
        """Set task information."""
        self.task = task
        self.task_id = id

    def get_description(self):
        """Get task description."""
        if hasattr(self, 'task'):
            return str(self.task.get_task(self.task_id)['description'])
        return ''

    def remove_task(self):
        """Delete task."""
        if hasattr(self, 'task'):
            self.task.remove_task(self.task_id)

    def update_task(self, status):
        """Update task."""
        if hasattr(self, 'task'):
            self.task.update_task(self.task_id, status)

    def get_recepient(self):
        """Get recepient."""
        if 'recepient' in self.task.get_task(self.task_id):
            return str(self.task.get_task(self.task_id)['recepient'])
        return None

    def get_target(self):
        """Get target info for notifications."""
        task = self.task.get_task(self.task_id)
        if 'name' in task:
            return str(task['name'])
        return str(task['url'] + ' / ' + task['tag'])

    def run(self):
        """Build task."""
        if not self.get_server_instance():
            print(colored('Server instance not received', 'red'))
            return

        if not self.server.has_job(self.name):
            print(colored('Job [' + self.name + '] not found', 'red'))
            return

        job_parameters = self.server[self.name].get_params_list()

        for key in self.parameters:
            if key not in job_parameters:
                print(
                    colored(
                        'Unknown job [' + self.name + '] parameter - ' + key,
                        'red'
                        )
                    )
                return
            if self.parameters[key] is None or len(self.parameters[key]) <= 0:
                print(
                    colored(
                        'Empty job [' + self.name + '] parameter - ' + key,
                        'red'
                        )
                    )
                return

        self.qi = self.server[self.name].invoke(build_params=self.parameters)

        self.qi.block_until_building()
        print(
            colored(
                str(self.__class__.__name__)+'/'+self.name,
                'green'
            )+': Building...'
        )
        # Add notify for building
        Notify.Notification.new(
            "<b>BUILD STARTED: </b>" +
            self.get_target(),
            self.get_description(),
            self.APP_ICON
        ).show()
        self.update_task('building')
        self.qi.block_until_complete()
        # Add notify for finish
        print(
            colored(
                str(self.__class__.__name__)+'/'+self.name,
                'green'
            )+': Finished'
        )
        Notify.Notification.new(
            "<b>BUILD FINISHED: </b>" +
            self.get_target(),
            self.get_description(),
            self.APP_ICON
        ).show()
        self.update_task('finished')
        self.remove_task()

        if not self.qi.get_build().is_good():
            print(str(self.qi.get_build().baseurl) + "/console")
            webbrowser.open(str(self.qi.get_build().baseurl) + "/console")
        else:
            recepient = self.get_recepient()
            if recepient is not None:
                self.send_msg(
                    recepient,
                    'Uzlikts: ' + self.get_target()
                )
                self.remove_task()
        return

    def send_msg(self, recipient, message):
        """Send message to pidgin / jabber."""
        bus = SessionBus()
        purple = bus.get(
            "im.pidgin.purple.PurpleService",
            "/im/pidgin/purple/PurpleObject"
        )
        my_id = purple.PurpleAccountsGetAllActive()[0]
        conv = purple.PurpleConversationNew(1, my_id, recipient)
        conv_im = purple.PurpleConvIm(conv)
        purple.PurpleConvImSend(conv_im, message)


if __name__ == '__main__':
    print('Not self running programm :(')
    print('This part exist just for quick tests')
