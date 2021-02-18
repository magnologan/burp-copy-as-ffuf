from burp import IBurpExtender, IContextMenuFactory, IHttpRequestResponse
from java.io import PrintWriter
from java.util import ArrayList
from javax.swing import JMenuItem
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection
from javax.swing import JOptionPane
import subprocess
import tempfile
import threading
import time

class BurpExtender(IBurpExtender, IContextMenuFactory, IHttpRequestResponse):


    def str_to_array(self, string):
        return [ord(c) for c in string]

    def registerExtenderCallbacks(self, callbacks):
        callbacks.setExtensionName("Copy as FFUF command")

        stdout = PrintWriter(callbacks.getStdout(), True)
        stderr = PrintWriter(callbacks.getStderr(), True)

        self.helpers = callbacks.getHelpers()
        self.callbacks = callbacks
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, invocation):
        self.context = invocation
        menuList = ArrayList()

        menuList.add(JMenuItem("Copy as FFUF command-line",
                actionPerformed=self.copyRequest))

        return menuList

    def copyRequest(self, event):
        httpTraffic = self.context.getSelectedMessages()[0]
        httpRequest = httpTraffic.getRequest()

        ffuf_cmd = "cat > request.http << EOF\r\n{httpRequest}\r\nEOF\r\n # add FUZZ string and use this command: \\ # ffuf -w <path_to_wordlist> -request request.http"

        httpRequest = self.helpers.bytesToString(httpRequest)

        data = ffuf_cmd.format(httpRequest=httpRequest)

        self.copyToClipboard(data)

        # CompassSecurity Note: 
        # Ugly hack because VMware is messing up the clipboard if a text is still selected, the function
        # has to be run in a separate thread which sleeps for 2 seconds.
        t = threading.Thread(target=self.copyToClipboard, args=(data,True))
        t.start()

    def copyToClipboard(self, data, sleep=False):
        if sleep is True:
            time.sleep(1.5)

        data = self.helpers.bytesToString(data)
        systemClipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
        systemSelection = Toolkit.getDefaultToolkit().getSystemSelection()
        transferText = StringSelection(data)
        systemClipboard.setContents(transferText, None)
        systemSelection.setContents(transferText, None)