# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re

from ..internal.SimpleHoster import SimpleHoster


class HostujeNet(SimpleHoster):
    __name__ = "HostujeNet"
    __type__ = "hoster"
    __version__ = "0.08"
    __status__ = "testing"

    __pattern__ = r'http://(?:www\.)?hostuje\.net/\w+'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("fallback", "bool",
                   "Fallback to free download if premium fails", True),
                  ("chk_filesize", "bool", "Check file size", True),
                  ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10)]

    __description__ = """Hostuje.net hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("GammaC0de", None)]

    NAME_PATTERN = r'<input type="hidden" name="name" value="(?P<N>.+?)">'
    SIZE_PATTERN = r'<b>Rozmiar:</b> (?P<S>[\d.,]+) (?P<U>[\w^_]+)<br>'
    OFFLINE_PATTERN = r'Podany plik nie został odnaleziony\.\.\.'

    def setup(self):
        self.multiDL = True
        self.chunk_limit = 1

    def handle_free(self, pyfile):
        m = re.search(r'<script src="([\w^_]+.php)"></script>', self.data)
        if m is not None:
            jscript = self.load("http://hostuje.net/" + m.group(1))
            m = re.search(r"\('(\w+\.php\?i=\w+)'\);", jscript)
            if m is not None:
                self.load("http://hostuje.net/" + m.group(1))
            else:
                self.error(_("Unexpected javascript format"))
        else:
            self.error(_("Script not found"))

        action, inputs = self.parse_html_form(
            pyfile.url.replace('.', r'\.').replace('?', r'\?')
        )
        if not action:
            self.error(_("Form not found"))

        self.download(action, post=inputs)
