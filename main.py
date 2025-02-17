import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]
ll = '61.403754,55.159535'
spn = '0.002,0.002'


class Example(QWidget):
    def __init__(self, ll, spn):
        super().__init__()
        self.getImage(ll, spn)
        self.initUI()
        self.ll = ll
        self.spn = spn
        self.scale = 0.002

    def getImage(self, ll, spn):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        ll_spn = f'll={ll}&spn={spn}'
        # Готовим запрос.

        map_request = f"{server_address}{ll_spn}&apikey={api_key}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        scale = float(self.spn.split(',')[0])
        x, y = self.ll.split(',')
        if event.key() == Qt.Key.Key_Right:
            x = float(x)
            x += scale / 2
            x = str(x)
        elif event.key() == Qt.Key.Key_Left:
            x = float(x)
            x -= scale / 2
            x = str(x)
        elif event.key() == Qt.Key.Key_Up:
            y = float(y)
            y += scale / 2
            y = str(y)
        elif event.key() == Qt.Key.Key_Down:
            y = float(y)
            y -= scale / 2
            y = str(y)
        elif event.key() == Qt.Key.Key_PageDown:
            self.scale += 0.002
            print(self.scale)
        elif event.key() == Qt.Key.Key_PageUp:
            if self.scale - 0.002 >= 0:
                self.scale -= 0.002
                print(self.scale)
        self.spn = f'{self.scale},{self.scale}'
        self.ll = ','.join([x, y])
        self.getImage(self.ll, self.spn)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example(ll, spn)
    ex.show()
    sys.exit(app.exec())
