import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow,
                             QPushButton, QHBoxLayout, QWidget, QSizePolicy)
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class MainWindow(QMainWindow):
    g_map: QLabel
    press_delta = 0.1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('main_window.ui', self)

        self.map_zoom = 5
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''

        self.light_btn = QPushButton('Светлая тема')
        self.dark_btn = QPushButton('Тёмная тема')

        self.light_btn.setFixedSize(120, 30)
        self.dark_btn.setFixedSize(120, 30)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.light_btn)
        self.buttons_layout.addWidget(self.dark_btn)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.buttons_widget = QWidget()
        self.buttons_widget.setLayout(self.buttons_layout)
        self.buttons_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.gridLayout.addWidget(self.buttons_widget, 1, 0, Qt.AlignmentFlag.AlignHCenter)

        self.light_btn.clicked.connect(self.set_light_theme)
        self.dark_btn.clicked.connect(self.set_dark_theme)

        self.refresh_map()

    def set_light_theme(self):
        self.map_l = 'map'
        self.refresh_map()

    def set_dark_theme(self):
        self.map_l = 'skl'
        self.refresh_map()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_PageUp and self.map_zoom < 17:
            self.map_zoom += 1
        if key == Qt.Key.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        if key == Qt.Key.Key_Left:
            self.map_ll[0] -= self.press_delta
        if key == Qt.Key.Key_Right:
            self.map_ll[0] += self.press_delta
        if key == Qt.Key.Key_Up:
            self.map_ll[1] += self.press_delta
        if key == Qt.Key.Key_Down:
            self.map_ll[1] -= self.press_delta

        self.refresh_map()

    def refresh_map(self):
        try:
            map_params = {
                "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
                "l": self.map_l,
                'z': self.map_zoom,
            }
            session = requests.Session()
            retry = Retry(total=10, connect=5, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.get('https://static-maps.yandex.ru/1.x/',
                                   params=map_params)
            response.raise_for_status()

            with open('tmp.png', mode='wb') as tmp:
                tmp.write(response.content)

            pixmap = QPixmap()
            pixmap.load('tmp.png')

            self.g_map.setPixmap(pixmap)
        except Exception as e:
            print(f"Ошибка при загрузке карты: {e}")


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
