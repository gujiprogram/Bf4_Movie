from PySide2.QtGui import Qt, QPalette, QBrush, QPixmap

from crawl import *
import os
import sys
from pathlib import Path
from PySide2.QtCore import QFile, QThread
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QProgressBar, QTextBrowser


class crawl_Movie(QThread):

    def __init__(self, keyword, crawl, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.crawl = crawl
        self.type = type
        self.stop_requested = False

    def run(self):
        print(self.keyword)
        print(self.crawl)
        for crawl in self.crawl:
            crawl.crawl_movie_links(self.keyword, self)

    def stop(self):
        self.stop_requested = True


class Widget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        # 设置背景图片
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("D:/Bf4_Movie/image/bk.jpg")))
        self.setPalette(palette)
        # 保存当前运行的线程
        self.current_thread = None

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

        # 添加按钮点击事件处理逻辑
        self.pushButton_Find_Movie = self.findChild(QPushButton, "pushButton")
        self.lineEdit_Movie = self.findChild(QLineEdit, "lineEdit")
        self.textBrowser_Link = self.findChild(QTextBrowser, "textBrowser")
        self.progressBar_Progress = self.findChild(QProgressBar, "progressBar")
        self.progressBar_Progress.hide()
        self.lineEdit_Movie.setPlaceholderText("请输入电影名称");
        self.pushButton_Find_Movie.clicked.connect(self.on_pushButton_Find_Movie_clicked)
        # 连接按下Enter键的事件到按钮的点击槽函数
        self.lineEdit_Movie.returnPressed.connect(self.on_pushButton_Find_Movie_clicked)

    def on_pushButton_Find_Movie_clicked(self):
        self.progressBar_Progress.show()
        self.progressBar_Progress.setValue(0)
        self.progressBar_Progress.setFormat("努力爬取中......")
        self.textBrowser_Link.clear()
        search_keyword = self.lineEdit_Movie.text()

        # 中止上次线程
        if self.current_thread:
            try:
                self.current_thread.stop()
                self.crawl_thread.quit()
                self.crawl_thread.wait()
                print("删除线程")
                self.crawl_thread.deleteLater()
            except Exception as e:
                print(f"Error stopping thread: {e}")

        crawl = []
        crawl_object1 = Crawl()
        crawl_object2 = Crawl_pansearch()
        # 将对象添加到crawl列表中
        crawl.append(crawl_object1)
        crawl.append(crawl_object2)

        # 创建新的线程
        self.crawl_thread = QThread()
        self.crawl_worker = crawl_Movie(keyword=search_keyword, crawl=crawl)
        self.current_thread = self.crawl_worker

        for crawl_object in crawl:
            crawl_object.link_signal.connect(self.on_links_received)
            crawl_object.progress_signal.connect(self.on_progress_received)

        self.crawl_worker.moveToThread(self.crawl_thread)
        self.crawl_thread.started.connect(self.crawl_worker.run)
        self.crawl_thread.finished.connect(self.crawl_thread.deleteLater)
        self.crawl_thread.start()

    def on_links_received(self, link):
        self.textBrowser_Link.setOpenExternalLinks(True)
        self.textBrowser_Link.append(link)
        self.textBrowser_Link.append(
            "----------------------------------------------------------------------------------------------------------")
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
