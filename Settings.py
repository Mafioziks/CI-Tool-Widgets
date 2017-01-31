"""Settings window."""

import requests
from termcolor import colored
from Config import Config as Con
# Import JIRA
from jira import JIRA

# Import Jenkins
from jenkinsapi.jenkins import Jenkins

# Import Gitlab
import gitlab

# Import interface libraries
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class SettingsDialog (Gtk.Window):
    """Settings window."""

    def __init__(self):
        """Initialize settings window."""
        Gtk.Window.__init__(self, title="Settings")

        con = Con()
        settings = con.get_settings()
        self.set_name('settingsWindow')

        self.content = Gtk.HBox(spacing=6)
        self.content.set_name('settingsBox')
        self.content.set_orientation(Gtk.Orientation.VERTICAL)
        self.add(self.content)

        self.lbl_jira_url = Gtk.Label('<b>Jira url</b>')
        self.lbl_jira_url.set_name('lblJira')
        self.lbl_jira_url.set_alignment(xalign=0, yalign=0.5)
        self.lbl_jira_url.set_use_markup(True)
        self.content.pack_start(self.lbl_jira_url, True, True, 0)

        self.txt_jira_url = Gtk.Entry()
        if settings is not None and 'jira' in settings.keys():
            self.txt_jira_url.set_text(settings['jira'])
        self.txt_jira_url.set_name('txtJira')
        self.content.pack_start(self.txt_jira_url, True, True, 0)

        self.lbl_jenkins_url = Gtk.Label('<b>Jenkins url</b>')
        self.lbl_jenkins_url.set_alignment(xalign=0, yalign=0.5)
        self.lbl_jenkins_url.set_name('lblJenkins')
        self.lbl_jenkins_url.set_use_markup(True)
        self.content.pack_start(self.lbl_jenkins_url, True, True, 0)

        self.txt_jenkins_url = Gtk.Entry()
        self.txt_jenkins_url.set_name('txtJenkins')
        if settings is not None and 'jenkins' in settings.keys():
            self.txt_jenkins_url.set_text(settings['jenkins'])
        self.content.pack_start(self.txt_jenkins_url, True, True, 0)

        self.lbl_gitlab_url = Gtk.Label('<b>Gitlab url</b>')
        self.lbl_gitlab_url.set_name('lblGitlab')
        self.lbl_gitlab_url.set_alignment(xalign=0, yalign=0.5)
        self.lbl_gitlab_url.set_use_markup(True)
        self.content.pack_start(self.lbl_gitlab_url, True, True, 0)

        self.txt_gitlab_url = Gtk.Entry()
        self.txt_gitlab_url.set_name('txtGitlab')
        if settings is not None and 'gitlab' in settings.keys():
            self.txt_gitlab_url.set_text(settings['gitlab'])
        self.content.pack_start(self.txt_gitlab_url, True, True, 0)

        self.btn_test = Gtk.Button(label='Test links & save correct')
        self.btn_test.set_name('btnTest')
        self.btn_test.connect('clicked', self.on_btn_clicked_test)
        self.content.pack_start(self.btn_test, True, True, 0)

        self.set_default_size(400, 200)

        self.set_style("""
        #lblJira, #lblJenkins, #lblGitlab{
            color: #18f;
            padding-left: 10px;
            font-family: "Arial";
            letter-spacing: 0.5em;
        }

        #txtJira, #txtJenkins, #txtGitlab {
            border: none;
            border-bottom: 2px solid black;
            border-radius: 0px;
            background: rgba(0,0,0,0);
            color: black;
            box-shadow: none;
        }

        #settinfsBox {
            padding: 10px;
        }

        #btnTest {
            background-color: #1236b7;
            box-shadow: none;
            color: black;
            font-weight: bold;
        }
        """)

        self.show_all()

    def set_style(self, css):
        """Set styles."""
        style_provider = Gtk.CssProvider()

        style_provider.load_from_data(bytes(css.encode()))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_btn_clicked_test(self, widget):
        """Test logins for links."""
        print('> Testing settings - urls')

        con = Con()
        settings = con.get_settings()

        jira_valid = False
        jenkins_valid = False
        gitlab_valid = False

        # Test jira connection
        jira_url = self.txt_jira_url.get_text()
        if len(jira_url) > 0:
            try:
                jira = JIRA(
                    server=jira_url,
                    basic_auth=(settings['username'], settings['password'])
                )

                user = jira.current_user()
                if len(user) > 0:
                    self.set_style(
                        """
                        #txtJira {
                            color: green;
                            font-weight: bold;
                        }
                        """
                    )
                    print('> Successfully connected to Jira as: ' + str(user))
                    jira_valid = True
            except requests.exceptions.MissingSchema as miss:
                print(colored('> Error: Not a link!', 'red'))
                self.set_style(
                    """
                    #txtJira {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )
            except Exception as e:
                print('Error: ' + str(e.message))
                self.set_style(
                    """
                    #txtJira {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )
        else:
            print('ELSE')

        # Test Jenkins connection
        jenkins_url = self.txt_jenkins_url.get_text()
        if len(jenkins_url) > 0:
            try:
                server = Jenkins(
                    jenkins_url,
                    settings['username'],
                    settings['password']
                )
                server.get_jenkins_obj()
                self.set_style(
                    """
                    #txtJenkins {
                        color: green;
                        font-weight: bold;
                    }
                    """
                )
                print('> Successfully connected to Jenkins')
                jenkins_valid = True
            except requests.exceptions.MissingSchema as miss:
                print(colored('> Error: Wrong Jenkins Url!', 'red'))
                self.set_style(
                    """
                    #txtJenkins {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )
            except Exception as e:
                if hasattr(e, 'message'):
                    print('Error: ' + str(e.message))
                self.set_style(
                    """
                    #txtJenkins {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )

        # Test Gitlab connection
        gitlab_url = self.txt_gitlab_url.get_text()
        if len(gitlab_url) > 0:
            try:
                git = gitlab.Gitlab(
                    url=gitlab_url,
                    http_username=settings['username'],
                    http_password=settings['password'],
                    email=settings['username'],
                    password=settings['password']
                )
                git.auth()
                self.set_style(
                        """
                        #txtGitlab {
                            color: green;
                            font-weight: bold;
                        }
                        """
                )
                print('> Successfully connected to Gitlab')
                gitlab_valid = True
            except requests.exceptions.MissingSchema as miss:
                print(colored('> Error: Wrong Gitlab Url!', 'red'))
                self.set_style(
                    """
                    #txtGitlab {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )
            except Exception as e:
                print('Error: ' + str(e.message))
                self.set_style(
                    """
                    #txtGitlab {
                        color: red;
                        font-weight: bold;
                    }
                    """
                )

        new_settings = dict()
        if jira_valid:
            new_settings.update({'jira': jira_url})

        if jenkins_valid:
            new_settings.update({'jenkins': jenkins_url})

        if gitlab_valid:
            new_settings.update({'gitlab': gitlab_url})

        con.save_settings(new_settings)
