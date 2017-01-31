"""Build dialog."""

from Config import Config as Con
# Import JIRA
from jira import JIRA

# Import Jenkins
from jenkinsapi.jenkins import Jenkins

# Import Git Explorer
from GitExplorer import GitExplorer

# Import interface libraries
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class BuildDialog (Gtk.Dialog):
    """Build Dialog."""

    def __init__(self, name):
        """Initialize build dialog."""
        Gtk.Dialog.__init__(
            self,
            name,
            None,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK
            )
        )
        self.content_area = self.get_content_area()
        self.content_area.set_spacing(15)

        self.cmb_presets = Gtk.ComboBoxText()
        self.cmb_presets.set_name('def_cmbPresets')
        self.content_area.pack_start(self.cmb_presets, False, True, 0)

        self.cmb_presets.connect('changed', self.do_add_empty_fields)

        self.txt_receiver = Gtk.Entry()
        self.txt_receiver.set_name('def_receiver')
        self.content_area.pack_end(self.txt_receiver, False, True, 10)

        self.lbl_receiver = Gtk.Label('Inform:')
        self.lbl_receiver.set_name('def_lbl_receiver')
        self.content_area.pack_end(self.lbl_receiver, False, True, 10)

        self.sep_hseparator = Gtk.HSeparator()
        self.sep_hseparator.set_name('def_separator')
        self.content_area.pack_end(self.sep_hseparator, False, True, 10)

        children = self.content_area.get_children()
        for child in children:
            if str(child.get_name()) == 'GtkBox':
                child.set_name('def_GtkBox')

    def set_project(self, project, mr=None):
        """Set project to choose from."""
        # Get presets from config
        con = Con()
        presets = con.get_preset_list()
        self.preset_list = list()
        for pr in presets:
            if str.lower(str(pr)).find(project) != -1:
                self.preset_list.append(pr)

        children = self.content_area.get_children()
        for child in children:
            if child.get_name() == 'def_cmbPresets':
                self.content_area.remove(child)

        self.cmb_presets = Gtk.ComboBoxText()
        self.cmb_presets.set_name('def_cmbPresets')
        for pr in self.preset_list:
            self.cmb_presets.insert(0, pr, pr)
        self.cmb_presets.connect('changed', self.do_add_empty_fields)
        self.content_area.pack_start(self.cmb_presets, False, True, 0)
        self.mr = mr
        self.show_all()

    def get_preset(self):
        """Return full preset information."""
        choosed_preset = self.cmb_presets.get_active_text()
        con = Con()
        preset_info = con.get_preset(choosed_preset)

        if preset_info is None:
            return None

        children = self.content_area.get_children()
        for child in children:
            if (str(child.get_name()).find('def_') == -1 and
                    str(child.get_name()).find('lbl_') == -1):
                preset_info.update(
                    {str(child.get_name()): str(child.get_text())}
                )

        if (self.txt_receiver.get_text() is not None and
                len(self.txt_receiver.get_text()) > 3):
            preset_info.update({'receiver': self.txt_receiver.get_text()})

        desc = ''
        if 'GIT_URL' in preset_info and 'JTAG' in preset_info:
            git = GitExplorer()
            desc = git.get_mr_title(
                preset_info['GIT_URL'],
                self.mr
            )

        if desc is None or len(desc) < 3:
            desc = str(self.mr)

        preset_info.update({'description': desc})
        preset_info.update({'name': choosed_preset + ' > ' + str(self.mr)})
        preset_info.update({'status': 'listed'})

        return preset_info

    def do_add_empty_fields(self, widget):
        """Add needed parameters for build."""
        children = self.content_area.get_children()
        for child in children:
            if str(child.get_name()).find('def_') == -1:
                self.content_area.remove(child)

        con = Con()
        preset = con.get_preset(self.cmb_presets.get_active_text())

        for key in preset:
            if preset[key] is None or len(preset[key]) <= 0:
                lbl_missing = Gtk.Label(key)
                lbl_missing.set_name('lbl_' + str(key))
                self.content_area.pack_start(lbl_missing, False, True, 0)

                txt_missing = Gtk.Entry()
                txt_missing.set_name(key)
                if key == 'JTAG' and self.mr is not None:
                    txt_missing.set_text(self.mr)
                self.content_area.pack_start(txt_missing, False, True, 0)

        self.show_all()
