"""Configuration manager."""

import json
import os


class Config:
    """Configuration manager."""

    config_file = "/con.yml"
    configurations = ""

    def read_config(self):
        """Read configurations from file."""
        try:
            f = open(
                os.path.dirname(os.path.realpath(__file__)) +
                self.config_file,
                'r'
            )
            content = f.read()
            if len(content) <= 0:
                return None
            configs = json.loads(content)
            f.close()
            return configs
        except IOError as er:
            print(er)

        return None

    def write_config(self, configs=configurations):
        """Write configurations to file."""
        try:
            f = open(
                os.path.dirname(os.path.realpath(__file__)) +
                self.config_file,
                'w'
            )
            f.write(json.dumps(configs))
            f.close()
            return True
        except IOError as er:
            print(er)

        return None

    def get_settings(self):
        """Get all settings."""
        conf = self.read_config()
        if conf is not None and "settings" in conf.keys():
            return conf['settings']
        return None

    def save_settings(self, settings={}):
        """Save settings."""
        conf = self.read_config()
        if conf is not None and 'settings' in conf.keys():
            conf['settings'].update(settings)
        else:
            conf['settings'] = settings
        self.write_config(conf)

    def add_preset(self, preset={}):
        """Add preset."""
        print('Adding preset')
        conf = self.read_config()
        if conf is not None and 'presets' in conf.keys():
            conf['presets'].update(preset)
            print(preset)
        else:
            conf['presets'] = preset
            print(preset)
        print(conf)
        self.write_config(conf)
        print('preset added')

    def get_preset(self, name):
        """Get preset configurations."""
        con = self.read_config()
        if 'presets' in con and name in con['presets']:
            return con['presets'][name]
        return None

    def remove_preset(self, name):
        """Remove preset configuration."""
        conf = self.read_config()
        if (conf is not None and
                'presets' in conf.keys() and
                name in conf['presets'].keys()):
            del conf['presets'][name]
        self.write_config(conf)

    def update_preset(self, target, preset):
        """Update preset with changes."""
        conf = self.read_config()
        if (conf is None or
                (
                    'presets' in conf.keys() and
                    preset.keys()[0] not in conf['presets'].keys()
                )):
            self.add_preset(preset)
        else:
            if preset.keys()[0] == target:
                conf['presets'][target].update(preset[target])
            else:
                conf['presets'][preset.keys()[0]] = conf['presets'].pop(target)
                conf['presets'][preset.keys()[0]].update(
                    preset[preset.keys()[0]]
                )
            self.write_config(conf)

    def __init__(self):
        """Initialize by reding file."""
        self.configurations = self.read_config()

    def get_preset_list(self):
        """Get all preset name list."""
        conf = self.read_config()
        if 'presets' not in conf or conf['presets'] is None:
            return None

        preset_list = []
        for name in conf['presets']:
            preset_list.append(name)

        return preset_list


if __name__ == '__main__':
    print('> Configuration manager')
    print('> Not self running app... yet')
