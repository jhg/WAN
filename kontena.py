#!/usr/bin/env python
import sys
import os

from zipfile import ZipFile, is_zipfile

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4.QtCore import QUrl, QVariant, QTimer, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class UrlInput(QLineEdit):
    def __init__(self, browser):
        super(UrlInput, self).__init__()
        self.browser = browser
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QUrl(self.text())
        browser.load(url)


class JavaScriptEvaluator(QLineEdit):
    def __init__(self, page):
        super(JavaScriptEvaluator, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        result = frame.evaluateJavaScript(self.text())

class ActionInputBox(QLineEdit):
    def __init__(self, page):
        super(ActionInputBox, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        action_string = str(self.text()).lower()
        if action_string == "b":
            self.page.triggerAction(QWebPage.Back)
        elif action_string == "f":
            self.page.triggerAction(QWebPage.Forward)
        elif action_string == "s":
            self.page.triggerAction(QWebPage.Stop)
        elif action_string == "r":
            self.page.triggerAction(QWebPage.Reload)


class RequestsTable(QTableWidget):
    header = ["url", "status", "content-type"]

    def __init__(self):
        super(RequestsTable, self).__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(self.header)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.ResizeToContents)

    def update(self, data):
        last_row = self.rowCount()
        next_row = last_row + 1
        self.setRowCount(next_row)
        for col, dat in enumerate(data, 0):
            if not dat:
                continue
            self.setItem(last_row, col, QTableWidgetItem(dat))


class KontenaFileReply(QNetworkReply):
    def __init__(self, parent, url):
        super(KontenaFileReply, self).__init__(parent)
        #self.setHeader(QNetworkRequest.ContentTypeHeader, QVariant('text/html; charset=utf-8'))
        QTimer.singleShot(0, self, SIGNAL("readyRead()"))
        QTimer.singleShot(0, self, SIGNAL("finished()"))
        self.open(self.ReadOnly | self.Unbuffered)
        self.setUrl(url)
        self.content = parent.wam.read(str(url.path()[1:]))
        self.offset = 0

    def __getattribute__(self, name):
        print(name)
        return object.__getattribute__(self, name)

    def abort(self):
        pass

    def isSequential(self):
        return True

    def bytesAvailable(self):
        return len(self.content)

    def readData(self, maxSize):
        _offset = min(maxSize, self.bytesAvailable)
        _content = self.content[self.offset:_offset]
        self.offset = _offset
        return _content


class Manager(QNetworkAccessManager):
    def __init__(self, table, wam=None):
        QNetworkAccessManager.__init__(self)
        self.finished.connect(self._finished)
        self.table = table
        self.wam = wam

    def _finished(self, reply):
        headers = reply.rawHeaderPairs()
        headers = {str(k):str(v) for k,v in headers}
        content_type = headers.get("Content-Type")
        url = reply.url().toString()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        status, ok = status.toInt()
        self.table.update([url, str(status), content_type])

    def createRequest(self, operation, request, data):
        if request.url().scheme() != "wam" or self.wam is None:
            return super(Manager, self).createRequest(operation, request, data)
        else:
            return KontenaFileReply(self, request.url())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    grid = QGridLayout()
    browser = QWebView()
    #url_input = UrlInput(browser)
    requests_table = RequestsTable()
    wam_file = ZipFile(os.path.abspath(sys.argv[1]))
    manager = Manager(requests_table, wam_file)
    page = QWebPage()
    page.setNetworkAccessManager(manager)
    browser.setPage(page)
    browser.load(QUrl('wam:///test.html'))

    #js_eval = JavaScriptEvaluator(page)
    #action_box = ActionInputBox(page)

    #grid.addWidget(url_input, 1, 0)
    #grid.addWidget(action_box, 2, 0)
    grid.addWidget(browser, 0, 0)
    grid.addWidget(requests_table, 4, 0)
    #grid.addWidget(js_eval, 5, 0)

    main_frame = QWidget()
    main_frame.setLayout(grid)
    main_frame.show()

    sys.exit(app.exec_())