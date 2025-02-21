import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QRadioButton, QLineEdit, QPushButton

SCREEN_SIZE = [600, 450]
ll = '61.403754,55.159535'
spn = '0.002,0.002'


class Example(QWidget):
    def __init__(self, ll, spn):
        super().__init__()
        self.dark = False
        self.metka_ll = None
        self.getImage(ll, spn)
        self.initUI()
        self.ll = ll
        self.spn = spn
        self.scale = 0.002

    def getImage(self, ll, spn):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'af90eac0-d94c-489a-8b0a-7cc38740ab4b'
        ll_spn = f'll={ll}&spn={spn}'
        map_request = f"{server_address}{ll_spn}"
        if self.metka_ll is not None:
            map_request += f"&pt={self.metka_ll},pm2rdm"
        if self.dark:
            map_request += "&theme=dark"
        map_request += f"&apikey={api_key}"
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
        self.radio_button = QRadioButton(self)
        self.radio_button.setText('Тёмная тема')
        self.radio_button.move(500, 10)
        self.radio_button.clicked.connect(self.mousePressEvent)
        self.poisk = QLineEdit(self)
        self.poisk.move(225, 425)
        self.btn_poisk = QPushButton(self)
        self.btn_poisk.move(370, 425)
        self.btn_poisk.setText('Искать!')
        self.btn_poisk.clicked.connect(self.search)

    def search(self):
        try:
            toponym_to_find = self.poisk.text()

            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

            geocoder_params = {
                "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
                "geocode": toponym_to_find,
                "format": "json"}

            response = requests.get(geocoder_api_server, params=geocoder_params)

            if not response:
                # обработка ошибочной ситуации
                self.poisk.setText('ERROR')
                return

            # Преобразуем ответ в json-объект
            json_response = response.json()
            # Получаем первый топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            self.ll = ','.join(toponym['Point']['pos'].split(' '))
            left_corner = toponym['boundedBy']['Envelope']['upperCorner']
            right_corner = toponym['boundedBy']['Envelope']['lowerCorner']
            self.scale = min(float(left_corner.split(' ')[0]) - float(right_corner.split(' ')[0]),
                             float(left_corner.split(' ')[1]) - float(right_corner.split(' ')[1]))
            self.spn = f"{self.scale},{self.scale}"
            self.metka_ll = self.ll
            self.getImage(self.ll, self.spn)
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.poisk.clearFocus()
        except Exception:
            self.poisk.setText('ERROR')

    def mousePressEvent(self, event):
        if self.radio_button.isChecked():
            self.dark = True
        else:
            self.dark = False
        self.getImage(self.ll, self.spn)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.poisk.clearFocus()

    def keyPressEvent(self, event):
        scale = float(self.spn.split(',')[0])
        x, y = self.ll.split(',')
        if event.key() == Qt.Key.Key_Right:
            self.poisk.clearFocus()
            x = float(x)
            x += scale / 2
            x = str(x)
        elif event.key() == Qt.Key.Key_Left:
            self.poisk.clearFocus()
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
        elif event.key() == Qt.Key.Key_PageUp:
            if self.scale - 0.002 >= 0:
                self.scale -= 0.002
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
