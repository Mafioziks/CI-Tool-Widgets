"""Login dialog."""

# Import interface libraries
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class LoginDialog (Gtk.Dialog):
    """Login Dialog."""

    def __init__(self):
        """Initialize build dialog."""
        Gtk.Dialog.__init__(
            self,
            'Login',
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

        self.lbl_username = Gtk.Label('Username:')
        self.content_area.add(self.lbl_username)

        self.txt_username = Gtk.Entry()
        self.content_area.add(self.txt_username)

        self.lbl_password = Gtk.Label('Password:')
        self.content_area.add(self.lbl_password)

        self.txt_password = Gtk.Entry()
        self.content_area.add(self.txt_password)

    def get_username(self):
        """Get username."""
        return self.txt_username.get_text()

    def get_password(self):
        """Get password."""
        return self.txt_password.get_text()
