"""Preset manager window."""

from Settings import SettingsDialog
from Config import Config as Con

# Import Jenkins
from jenkinsapi.jenkins import Jenkins

# Import interface libraries
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class JenkinsPresets(Gtk.Window):
    """Jenkins preset creator window."""

    def __init__(self):
        """Initialize presset manager window."""
        Gtk.Window.__init__(self, title="Preset Manager")

        self.page_layout = Gtk.Notebook()
        self.add(self.page_layout)

        # Add presset add page
        self.page_add_preset = Gtk.Box()
        self.page_add_preset.set_orientation(Gtk.Orientation.VERTICAL)
        self.page_add_preset.set_spacing(16)
        self.page_layout.append_page(
            self.page_add_preset, Gtk.Label('Add Preset')
        )

        self.lbl_preset_name = Gtk.Label('Preset name')
        self.lbl_preset_name.set_name('lblPresetName')
        self.page_add_preset.pack_start(
            self.lbl_preset_name,
            True,
            True,
            0
        )

        self.txt_preset_name = Gtk.Entry()
        self.txt_preset_name.set_name('txtPresetName')
        self.page_add_preset.pack_start(
            self.txt_preset_name,
            True,
            True,
            0
        )

        jenkins_jobs = self.get_jenkins_jobs()

        self.cmbJobs = Gtk.ComboBoxText()
        self.cmbJobs.set_name('cmbJobs')

        for job in jenkins_jobs:
            self.cmbJobs.insert(0, job, job)

        self.cmbJobs.connect('changed', self.do_add_parameter_fields)
        self.page_add_preset.pack_start(self.cmbJobs, False, True, 0)

        self.btn_preset_add = Gtk.Button('Add preset')
        self.btn_preset_add.set_name('btnAddPreset')
        self.btn_preset_add.connect('clicked', self.do_add_preset)
        self.page_add_preset.pack_end(self.btn_preset_add, False, True, 0)

        # Page preset list
        self.page_preset_list = Gtk.Box()
        self.page_preset_list.set_orientation(Gtk.Orientation.VERTICAL)
        self.page_preset_list.set_spacing(16)
        self.page_layout.append_page(
            self.page_preset_list, Gtk.Label('Manage presets')
        )

        self.update_preset_list()

        self.btn_remove_preset = Gtk.Button('Remove')
        self.btn_remove_preset.connect('clicked', self.do_remove_preset)
        self.page_preset_list.pack_end(self.btn_remove_preset, False, True, 0)

        self.show_all()

    def get_jenkins_jobs(self):
        """Get list of jenkins jobs."""
        con = Con()
        settings = con.get_settings()

        if 'jenkins' not in settings:
            SettingsDialog()

        self.jenkins = Jenkins(
            settings['jenkins'],
            settings['username'],
            settings['password']
        )

        return self.jenkins.get_jobs_list()

    def do_add_parameter_fields(self, widget):
        """Get and add to window job parameters."""
        children = self.page_add_preset.get_children()

        while Gtk.events_pending():
            Gtk.main_iteration()

        label_test = Gtk.Label('Test')
        self.page_add_preset.pack_start(label_test, False, True, 0)

        for child in children:
            if (child.get_name() != 'cmbJobs' and
                    child.get_name() != 'btnAddPreset' and
                    child.get_name() != 'lblPresetName' and
                    child.get_name() != 'txtPresetName'):
                self.page_add_preset.remove(child)

        parameters = self.jenkins.get_job(
            self.cmbJobs.get_active_text()
        ).get_params()

        # Test for getting parameter info.
        # Need to make for default values cmb boxes.
        for p in parameters:
            par_label = Gtk.Label(str(p['name']))
            self.page_add_preset.pack_start(par_label, False, True, 0)
            if 'choices' in p:
                par_cmb = Gtk.ComboBoxText()
                par_cmb.set_name(str(p['name']))

                for ch in p['choices']:
                    par_cmb.insert(0, ch, ch)

                self.page_add_preset.pack_start(
                    par_cmb,
                    False,
                    True,
                    0
                )
                continue

            par_entry = Gtk.Entry()
            par_entry.set_name(str(p['name']))
            self.page_add_preset.pack_start(par_entry, False, True, 0)

        self.show_all()

        Gtk.main_iteration()

    def do_add_preset(self, widget):
        """Add new preset."""
        print('> Adding preset')
        preset = dict()
        preset_name = self.txt_preset_name.get_text()
        preset.update({preset_name: {}})
        for child in self.page_add_preset.get_children():
            if (str(child.__class__.__name__) == 'Entry' or
                    str(child.__class__.__name__) == 'ComboBoxText'):
                if (child.get_name() == 'txtPresetName' or
                        child.get_name() == 'cmbJobs'):
                    continue

                if str(child.__class__.__name__) == 'ComboBoxText':
                    preset[preset_name].update(
                        {child.get_name(): child.get_active_text()}
                    )
                    continue

                preset[preset_name].update(
                    {child.get_name(): child.get_text()}
                )

        preset[preset_name].update({'job': self.cmbJobs.get_active_text()})
        # On building from presets need to set Entry fields for empty values.
        con = Con()
        con.add_preset(preset)
        self.update_preset_list()
        self.show_all()

    def do_remove_preset(self, widget):
        """Remove selected preset."""
        preset = self.cmb_presets.get_active_text()
        if preset is not None and len(preset) > 3:
            con = Con()
            con.remove_preset(preset)
        self.update_preset_list()

    def update_preset_list(self):
        """Update preset list elements."""
        children = self.page_preset_list.get_children()
        for child in children:
            if child.get_name() == 'cmbPresets':
                self.page_preset_list.remove(child)
        con = Con()
        presets = con.get_preset_list()
        self.cmb_presets = Gtk.ComboBoxText()
        self.cmb_presets.set_name('cmbPresets')
        if presets is not None:
            for p in presets:
                self.cmb_presets.insert(0, p, p)
        self.cmb_presets.show()
        self.page_preset_list.pack_start(self.cmb_presets, False, True, 0)
        self.show_all()
