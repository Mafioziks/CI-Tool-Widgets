#!/usr/bin/env python3

import os
import re
import sys
import webbrowser
from termcolor import colored
from Builder import JenManager
from Settings import SettingsDialog
from PresetManager import JenkinsPresets
from BuildDialog import BuildDialog
from LoginDialog import LoginDialog
# My imports
from Config import Config as Con      # New config class
from TaskList import TaskList
from GitExplorer import GitExplorer

# Import JIRA
from jira import JIRA
from jira import exceptions as JiraExceptions

# Import interface libraries
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, AppIndicator3, Gdk

test = True


class JiraHelper:
    """Jira helper."""

    def __init__(self):
        """Initialize base."""
        self.tasks = TaskList()

    def get_my_tasks(self):
        """Testing jira getting my ticket list."""
        if 'j' not in locals():
            con = Con()
            settings = con.get_settings()
            if settings is None or 'jira' not in settings:
                print(
                    colored(
                        '> Jira access not added!',
                        'red'
                    )
                )
                return None
            try:
                self.j = JIRA(
                    server=settings['jira'],
                    basic_auth=(settings['username'], settings['password'])
                )
            except JiraExceptions.JIRAError as ex:
                if str(ex).find('HTTP 401'):
                    print(
                        colored(
                            'Error > HTTP 401: ' +
                            'Problem with Jira or wrong username/passowrd',
                            'red'
                        )
                    )
                else:
                    print(colored(ex, 'red'))
                sys.exit(0)
            except Exception as eex:
                print(colored(eex.message, 'red'))
                sys.exit(0)
        print('Ticket owner: ' + str(self.j.current_user()))
        my_issues = self.j.search_issues(
            'assignee = ' + self.j.current_user(),
            maxResults=20
        )
        print('--------------------------------------------')
        for iss in my_issues:
            if str(iss.fields.status) == 'Closed':
                continue

            if str(iss.fields.status) == 'Open':
                col = 'blue'
            elif str(iss.fields.status) == 'Closed':
                col = 'yellow'
            elif str(iss.fields.status) == 'Test ready':
                col = 'red'
            elif str(iss.fields.status) == 'Review Functional':
                col = 'green'
            else:
                col = 'white'
            print(
                colored(
                    '[' + str(iss) + '] ' +
                    str(iss.fields.summary) + ' | ' +
                    str(iss.fields.status) + ' (' +
                    str(iss.fields.issuetype) + ' | ' +
                    str(iss.fields.priority) + ')',
                    col
                )
            )
        return my_issues

    def add_indicator(self, *args, **kwargs):
        """Add app indicator or update it."""
        icon = "/res/img/icons/jira_icon_25x25.png"
        if test:
            icon = "/res/img/icons/jira_icon__test_25x25.png"

        menu = self.create_menu()
        currpath = os.path.dirname(os.path.realpath(__file__))
        APP_ICON = currpath + icon
        if 'indicator' not in locals():
            self.indicator = AppIndicator3.Indicator.new(
                "JiraHelper",
                APP_ICON,
                AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(menu)
        # TODO: Automatic menu indicator
        # threading.Timer(30, self.add_indicator).start()

    def create_menu(self):
        """Create menu."""
        issues = self.get_my_tasks() or list()
        menu = Gtk.Menu()
        con = Con()
        settings = con.get_settings()

        for issue in issues:
            if str(issue.fields.status) == 'Closed':
                continue

            img = Gtk.Image()
            img.set_from_file(
                os.path.dirname(os.path.realpath(__file__)) +
                '/res/img/priority/' +
                str(issue.fields.priority) + '.png'
            )

            item = Gtk.ImageMenuItem(
                '[' + str(issue) + '] (' +
                str(issue.fields.status) + ') ' +
                str(issue.fields.summary)
            )
            item.set_image(img)

            submenu = Gtk.Menu()

            item_open = Gtk.MenuItem('Open in browser')
            item_open.connect(
                'activate',
                self.do_open_in_browser,
                settings['jira'] + 'browse/' + str(issue)
            )
            submenu.append(item_open)

            submenu.append(Gtk.SeparatorMenuItem())

            # Add task reasign task
            transitions = self.j.transitions(issue)
            for t in transitions:
                item_transition = Gtk.MenuItem(t['name'])
                item_transition.connect(
                    'activate',
                    self.do_issue_transition,
                    issue,
                    t['id']
                )
                submenu.append(item_transition)

            # Create build buttons for ticket
            build_parameters = self.get_git_links(issue)
            for build_p in build_parameters:
                print(colored(build_p, 'yellow'))
                item_build = Gtk.MenuItem(
                    'Build: ' + build_p['project'] + '|' + build_p['mr']
                )
                item_build.connect(
                    'activate',
                    self.do_build,
                    build_p['project'], build_p['mr']
                )
                submenu.append(item_build)
            item.set_submenu(submenu)
            menu.append(item)

        menu.append(Gtk.SeparatorMenuItem())

        itemDashboard = Gtk.MenuItem('Open Dashboard')
        itemDashboard.connect('activate', self.do_dashboard)
        menu.append(itemDashboard)

        itemUpdate = Gtk.MenuItem('Update')
        itemUpdate.connect('activate', self.add_indicator)
        menu.append(itemUpdate)

        itemSettings = Gtk.MenuItem('Settings')
        itemSettings.connect('activate', self.do_settings)
        menu.append(itemSettings)

        itemPresets = Gtk.MenuItem('Presets')
        itemPresets.connect('activate', self.do_manage_presets)
        menu.append(itemPresets)

        itemQuit = Gtk.MenuItem('Quit')
        itemQuit.connect('activate', self.do_quit)
        menu.append(itemQuit)
        menu.show_all()

        return menu

    def do_quit(self, widget):
        """Quit app."""
        # Send stop signal to JenManager before quit
        if 'jm' in locals():
            self.jm.quit()
        sys.exit()

    def do_open_in_browser(self, widget, url):
        """Open link in browser."""
        print(str(url))
        webbrowser.open(url)

    def do_issue_transition(self, widget, issue, transition_id, person=None):
        """Transit issue."""
        if person is None:
            try:
                self.j.transition_issue(issue, str(transition_id))
            except JiraExceptions.JIRAError as e:
                print("JIRAError: " + str(e))
            sys.exit(0)
        else:
            try:
                self.j.transition_issue(
                    issue,
                    str(transition_id),
                    assignee={'name': person}
                )
            except JiraExceptions.JIRAError as e:
                print("JIRAError: " + str(e))
            sys.exit(0)
        self.add_indicator()

    def get_git_links(self, issue):
        """Get git links for issue to build."""
        # Get urls from issue description
        urls = re.findall('(http[^\s]*)', str(issue.fields.description))
        # Get links from comments
        # for comment in issue.fields.comment.comments:
        #     find = re.findall('(http://git[^\s]*)', comment.body)
        #     if len(find) >=0:
        #         urls.extend(find)
        urlList = list()
        for url in urls:
            # Get git urls
            if len(re.findall('git', url)) <= 0:
                continue
            url_parts = url.split('/')
            if (re.match(r'^\d+$', url_parts[len(url_parts)-1])):
                urlList.append({
                    'mr': 'mr' + url_parts[len(url_parts)-1],
                    'project': url_parts[len(url_parts)-3]
                })
        return urlList

    def do_build(self, widget, project, mr, preset=''):
        """Send task to build."""
        build = BuildDialog('Build: ' + project + ' | ' + mr)
        build.set_project(project, mr)
        build.show_all()
        response = build.run()
        if response != Gtk.ResponseType.OK:
            build.destroy()
            return

        task = build.get_preset()
        build.destroy()
        self.tasks.add_custom_task(task)

        # If JenManager thread does not exist or is finished - create new
        if not hasattr(self, 'jm') or not self.jm.is_alive():
            self.jm = JenManager(1, 'JMan', 1)
            self.jm.set_task_list(self.tasks)
            self.jm.start()
        return

    def do_dashboard(self, widget):
        """Open Jira dashboard."""
        con = Con()
        settings = con.get_settings()
        if settings is not None and 'jira' in settings:
            webbrowser.open(settings['jira'])
        else:
            print(colored('> Jira not added', 'red'))

    def login(self):
        """Login to system."""
        con = Con()
        settings = con.get_settings()
        if (settings is None or
                'username' not in settings or
                'password' not in settings):

            dialog_login = Gtk.Dialog(
                "Login",
                None,
                0,
                (
                    Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK,
                    Gtk.ResponseType.OK
                )
            )

            dialog_login.set_default_size(300, 200)
            dialog_content = dialog_login.get_content_area()

            lbl_login = Gtk.Label('Login')
            dialog_content.add(lbl_login)

            lbl_uname = Gtk.Label('Username')
            dialog_content.add(lbl_uname)

            txt_uname = Gtk.Entry().set_orientation(Gtk.Orientation.VERTICAL)
            dialog_content.add(txt_uname)

            lbl_pass = Gtk.Label('Password')
            dialog_content.add(lbl_pass)

            txt_pass = Gtk.Entry()
            dialog_content.add(txt_pass)

            dialog_login.show_all()

            response = dialog_login.run()

            while (response != Gtk.ResponseType.CANCEL or (
                response == Gtk.ResponseType.OK and
                len(txt_uname) > 3 and
                len(txt_pass) > 3
            )):
                print('Please fill all fields!')

            if response == Gtk.ResponseType.CANCEL:
                sys.exit()

            con.save_settings({
                'username': txt_uname.get_text(),
                'password': txt_pass.get_text()
            })

            settings = con.get_settings()

            dialog_login.destroy()

        self.username = settings['username']
        self.password = settings['password']

    def do_settings(self, widget):
        """Open settings."""
        SettingsDialog()

    def do_manage_presets(self, widget):
        """Open Preset manager."""
        JenkinsPresets()


if __name__ == '__main__':
    print('JiraHelper - App started')
    print('------------------------')
    con = Con()
    configs = con.read_config()
    if configs is None:
        login = LoginDialog()
        login.show_all()
        response = login.run()

        if response == Gtk.ResponseType.CANCEL:
            exit

        con.save_settings(
            settings={
                'username': login.get_username(),
                'password': login.get_password()
            }
        )

    del con

    jh = JiraHelper()
    jh.add_indicator()
    Gtk.main()
