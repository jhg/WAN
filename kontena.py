#!/usr/bin/env python3
"""
Kontena


Copyright (C) 2016 Jesus Hernandez Gormaz <jhg.jesus@gmail.com>

Under license: Affero Gnu Public License V3
"""

import sys
import os

from zipfile import ZipFile, is_zipfile

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtCore import QUrl, QVariant, QTimer, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtNetwork import QNetworkRequest, QNetworkReply


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
        # self.setHeader(
        #     QNetworkRequest.ContentTypeHeader,
        #     QVariant('text/html; charset=utf-8')
        # )
        QTimer.singleShot(0, self, SIGNAL("readyRead()"))
        QTimer.singleShot(0, self, SIGNAL("finished()"))
        self.open(self.ReadOnly | self.Unbuffered)
        self.setUrl(url)
        self.content = parent.kontena.read_file(str(url.path()[1:]))
        self.offset = 0

    def abort(self):
        pass

    def isSequential(self):
        return True

    def bytesAvailable(self):
        return len(self.content)

    def readData(self, maxSize):
        _offset = min(maxSize, self.bytesAvailable())
        _content = self.content[self.offset:_offset]
        self.offset = _offset
        return _content


class KontenaManager(QNetworkAccessManager):

    def __init__(self, kontena, table):
        QNetworkAccessManager.__init__(self)
        self.finished.connect(self._finished)
        self.table = table
        self.kontena = kontena

    def _finished(self, reply):
        headers = reply.rawHeaderPairs()
        headers = {str(k): str(v) for k, v in headers}
        content_type = headers.get("Content-Type")
        url = reply.url().toString()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if status is not None:
            status, ok = status.toInt()
            str(status)
        else:
            status = 'null'
        self.table.update([url, status, content_type])

    def createRequest(self, operation, request, data):
        if request.url().scheme() == "file":
            return KontenaFileReply(self, request.url())
        return super(KontenaManager, self).createRequest(operation, request, data)


class KontenaApp(object):

    def __init__(self, argv):
        self.app = app = QApplication(argv)
        self.browser = QWebView()
        requests_table = RequestsTable()
        manager = KontenaManager(self, requests_table)
        page = QWebPage()
        page.setNetworkAccessManager(manager)
        self.browser.setPage(page)
        grid = QGridLayout()
        grid.addWidget(self.browser, 0, 0)
        # grid.addWidget(requests_table, 4, 0)
        self.window = QWidget()
        self.window.setLayout(grid)

    def open_app(self, path):
        self.kontena = ZipFile(path)

    def read_file(self, file_name):
        return self.kontena.read(file_name)

    def exe(self):
        self.browser.load(QUrl('file:///index.html'))
        self.window.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__" and len(sys.argv) >= 2 and is_zipfile(sys.argv[1]):
    kontena_file = os.path.abspath(sys.argv[1])
    del sys.argv[1]
    kontena = KontenaApp(sys.argv)
    kontena.open_app(kontena_file)
    kontena.exe()
