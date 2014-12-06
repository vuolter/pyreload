# -*- coding: utf-8 -*-

import re

from urllib import unquote
from urlparse import urljoin, urlparse

from module.plugins.Hook import Hook
from module.plugins.Plugin import SkipDownload


class SkipRev(Hook):
    __name__    = "SkipRev"
    __type__    = "hook"
    __version__ = "0.12"

    __config__ = [("auto",   "bool", "Automatically keep all rev files needed by package", True),
                  ("tokeep", "int" , "Min number of rev files to keep for package"       ,    1),
                  ("unskip", "bool", "Restart a skipped rev when download fails"         , True)]

    __description__ = """Skip files ending with extension rev"""
    __license__     = "GPLv3"
    __authors__     = [("Walter Purcaro", "vuolter@gmail.com")]


    def _setup(self):
        super(self.pyfile.plugin, self).setup()
        if self.pyfile.hasStatus("skipped"):
            raise SkipDownload(self.pyfile.getStatusName())


    def pyname(self, pyfile):
        plugin = pyfile.plugin

        if hasattr(plugin, "info") and 'name' in plugin.info and plugin.info['name']:
            name = plugin.info['name']

        elif hasattr(plugin, "parseInfo"):
            name = next(plugin.parseInfo([pyfile.url]))['name']

        elif hasattr(plugin, "getInfo"):  #@NOTE: if parseInfo was not found, getInfo should be missing too
            name = plugin.getInfo(pyfile.url)['name']

        else:
            self.logWarning("Unable to grab file name")
            name = urlparse(unquote(pyfile.url)).path.split('/')[-1])

        return name


    def downloadPreparing(self, pyfile):
        if pyfile.getStatusName() is "unskipped" or not pyname(pyfile).endswith(".rev"):
            return

        tokeep = self.getConfig("tokeep")

        if tokeep > 0:
            saved = [True for link in pyfile.package().getChildren() \
                     if link.name.endswith(".rev") and (link.hasStatus("finished") or link.hasStatus("downloading"))].count(True)

            if saved < tokeep:
                return

        pyfile.setCustomStatus("SkipRev", "skipped")
        pyfile.plugin.setup = _setup  #: work-around: inject status checker inside the preprocessing routine of the plugin


    def downloadFailed(self, pyfile):
        if self.getConfig("auto") is False:

            if self.getConfig("unskip") is False:
                return

            if not pyfile.name.endswith(".rev"):
                return

        for link in pyfile.package().getChildren():
            if link.hasStatus("skipped") and link.name.endswith(".rev"):
                link.setCustomStatus("unskipped", "queued")
                return
