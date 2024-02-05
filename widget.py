# This Python file uses the following encoding: utf-8
from PySide2.QtGui import Qt, QPalette, QBrush, QPixmap

from crawl import *
import os
import sys
from pathlib import Path
from PySide2.QtCore import QFile, QThread, Signal
from PySide2.QtUiTools import QUiLoader
import time
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QProgressBar, QTextBrowser


class crawl_Movie(QThread):

    def __init__(self, keyword, crawl, parent=None):
        super().__init__(parent)
        self.links = []
        self.keyword = keyword
        self.crawl = crawl

    def run(self):
        print(self.keyword)
        self.crawl.crawl_movie_links(self.keyword)


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        # 设置背景图片
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("D:/Bf4_Movie/image/bk.jpg")))
        self.setPalette(palette)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

        # 添加按钮点击事件处理逻辑
        self.pushButton_Find = self.findChild(QPushButton, "pushButton")
        self.lineEdit_Movie = self.findChild(QLineEdit, "lineEdit")
        self.textBrowser_Link = self.findChild(QTextBrowser, "textBrowser")
        self.progressBar_Progress = self.findChild(QProgressBar, "progressBar")
        self.progressBar_Progress.hide()
        self.lineEdit_Movie.setPlaceholderText("请输入电影名称");
        self.pushButton_Find.clicked.connect(self.on_pushButton_Find_clicked)
        # 连接按下Enter键的事件到按钮的点击槽函数
        self.lineEdit_Movie.returnPressed.connect(self.on_pushButton_Find_clicked)

    def on_pushButton_Find_clicked(self):
        self.progressBar_Progress.show()
        self.progressBar_Progress.setValue(0)
        self.progressBar_Progress.setFormat("努力爬取中......")
        self.textBrowser_Link.clear()
        search_keyword = self.lineEdit_Movie.text()
        self.crawl = Crawl()
        self.crawl_thread = crawl_Movie(keyword=search_keyword, crawl=self.crawl)
        self.crawl.link_signal.connect(self.on_links_received)
        self.crawl.progress_signal.connect(self.on_progress_received)
        self.crawl_thread.start()

    def on_links_received(self, link):
        self.textBrowser_Link.setOpenExternalLinks(True)
        self.textBrowser_Link.append(link)
        self.textBrowser_Link.append("----------------------------------------------------------------------------------------------------------")
        self.textBrowser_Link.append("\n")

    def on_progress_received(self, progress):
        # 更新进度值
        self.progressBar_Progress.show()
        self.progressBar_Progress.setValue(int(progress))
        self.progressBar_Progress.setFormat("爬取中...... : {}%".format("{:.1f}".format(progress)))
        # 设置进度条的对齐方式
        self.progressBar_Progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if int(progress) == 100:
            self.progressBar_Progress.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
