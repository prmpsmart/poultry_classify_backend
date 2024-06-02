import os, math, requests, threading, base64, datetime

try:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
except:
    os.system("pip install PyQt5")
    os.system("python ui.py")
    exit()


d = "./ai_history"
if not os.path.isdir(d):
    os.mkdir(d)


class PRMP_QSpinner(QWidget):
    def __init__(
        self,
        parent,
        centerOnParent=True,
        disableParentWhenSpinning=False,
        modality=Qt.NonModal,
    ):
        super().__init__(parent)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        # WAS IN initialize()
        self._color = QColor(Qt.black)
        self._roundness = 100.0
        self._minimumTrailOpacity = 3.14159265358979323846
        self._trailFadePercentage = 80.0
        self._revolutionsPerSecond = 1.57079632679489661923
        self._numberOfLines = 20
        self._lineLength = 10
        self._lineWidth = 2
        self._innerRadius = 10
        self._currentCounter = 0
        self._isSpinning = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()
        # END initialize()

        self.setWindowModality(modality)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, _):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.NoPen)
        for i in range(0, self._numberOfLines):
            painter.save()
            painter.translate(
                self._innerRadius + self._lineLength,
                self._innerRadius + self._lineLength,
            )
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines
            )
            color = self.currentLineColor(
                distance,
                self._numberOfLines,
                self._trailFadePercentage,
                self._minimumTrailOpacity,
                self._color,
            )
            painter.setBrush(color)
            rect = QRect(
                0,
                int(-self._lineWidth / 2),
                int(self._lineLength),
                int(self._lineWidth),
            )
            painter.drawRoundedRect(
                rect, self._roundness, self._roundness, Qt.RelativeSize
            )
            painter.restore()

    def start(self):
        self.updatePosition()
        self._isSpinning = True
        self.show()

        if self.parentWidget and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self):
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateSize()

    def color(self):
        return self._color

    def roundness(self):
        return self._roundness

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def revolutionsPersSecond(self):
        return self._revolutionsPerSecond

    def numberOfLines(self):
        return self._numberOfLines

    def lineLength(self):
        return self._lineLength

    def lineWidth(self):
        return self._lineWidth

    def innerRadius(self):
        return self._innerRadius

    def isSpinning(self):
        return self._isSpinning

    def setRoundness(self, roundness):
        self._roundness = max(0.0, min(100.0, roundness))

    def setColor(self, color=Qt.black):
        self._color = QColor(color)

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def updateSize(self):
        size = int((self._innerRadius + self._lineLength) * 2)
        self.setFixedSize(size, size)

    def updateTimer(self):
        self._timer.setInterval(
            int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        )

    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            self.move(
                int(self.parentWidget().width() / 2 - self.width() / 2),
                int(self.parentWidget().height() / 2 - self.height() / 2),
            )

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(
        self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput
    ):
        color = QColor(colorinput)
        if countDistance == 0:
            return color
        minAlphaF = minOpacity / 100.0
        distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)
        else:
            alphaDiff = color.alphaF() - minAlphaF
            gradient = alphaDiff / float(distanceThreshold + 1)
            resultAlpha = color.alphaF() - gradient * countDistance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color


url = "http://127.0.0.1:8000"


class Request(QObject):
    start = pyqtSignal()
    notify = pyqtSignal(tuple)
    success = pyqtSignal(dict)
    stop = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.notify.connect(self.on_notify)

    def post(self, path: str, json: dict):
        threading.Thread(target=self._post, args=(path, json)).start()

    def _post(self, path: str, json: dict):
        self.start.emit()
        try:
            response = requests.post(f"{url}/{path}", json=json)
            rjson = response.json()

            if response.status_code == 200:
                self.success.emit(rjson)

            self.notify.emit(("Account Error", rjson["detail"]))

        except Exception as e:
            self.notify.emit(("Network Error", str(e)))
        self.stop.emit()

    def on_notify(self, notify: tuple):
        QMessageBox.warning(app.win, notify[0], notify[1])


class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.spinner = PRMP_QSpinner(self, disableParentWhenSpinning=True)
        self.request = Request()
        self.request.start.connect(self.spinner.start)
        self.request.stop.connect(self.spinner.stop)
        self.request.success.connect(self.on_success)

    def on_success(self, _): ...


class Account(Widget):
    def __init__(self):
        super().__init__()

        hlay = QHBoxLayout(self)
        hlay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hlay.addStretch()

        vlay = QVBoxLayout()
        hlay.addLayout(vlay)

        title = QLabel("Account")
        title.setObjectName("title")
        vlay.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)

        vlay.addSpacing(20)

        flay = QFormLayout()
        vlay.addLayout(flay)

        e = ""
        e = "prmpsmart@gmail.com"
        self.emailLE = QLineEdit(e)
        self.emailLE.setPlaceholderText("Enter email")
        flay.addRow("Email : ", self.emailLE)

        p = ""
        p = "prmpsmart"
        self.passwordLE = QLineEdit(p)
        self.passwordLE.setEchoMode(QLineEdit.Password)
        self.passwordLE.setPlaceholderText("Enter password")
        flay.addRow("Password : ", self.passwordLE)

        vlay.addSpacing(40)

        hlay2 = QHBoxLayout()
        vlay.addLayout(hlay2)

        register = QPushButton("Register")
        register.clicked.connect(self.register)
        hlay2.addWidget(register)

        login = QPushButton("Login")
        login.clicked.connect(self.login)
        hlay2.addWidget(login)

        hlay.addStretch()

    def account(self, new: bool = False):
        email = self.emailLE.text()
        password = self.passwordLE.text()

        if len(email) < 5:
            self.request.notify.emit(
                (
                    "Invalid email",
                    "Enter a valid email.",
                )
            )

        elif len(password) < 5:
            self.request.notify.emit(
                ("Invalid password", "Password must be longer than 5 characters.")
            )
        else:
            self.request.post(
                "login",
                dict(
                    email=email,
                    password=password,
                    new=new,
                ),
            )

    def register(self):
        return self.account(True)

    def login(self):
        return self.account()

    def on_success(self, _):
        return self.window().show_home()


class Home(Widget):
    def __init__(self):
        super().__init__()

        self.setVisible(False)

        lay = QVBoxLayout(self)

        self.pixmap: QPixmap = None
        self.returned_pixmap: QPixmap = None

        self.image_label = QLabel("Selected image will\ndisplay here")
        self.image_label.setObjectName("image_label")
        self.image_label.setWordWrap(True)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.image_label, 1)

        lay.addSpacing(10)

        # self.disease_name = QLabel("Disease name will show here.")
        # self.disease_name.setObjectName("disease_name")
        # self.disease_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # lay.addWidget(self.disease_name)

        lay.addSpacing(10)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addWidget(QLabel("History : "))
        self.history_combo = QComboBox()
        hlay.addWidget(self.history_combo)

        hlay.addStretch()

        browse = QPushButton("Browse Image")
        browse.clicked.connect(self.browse)
        hlay.addWidget(browse)

        reload = QPushButton("Reload")
        reload.clicked.connect(self.reload)
        hlay.addWidget(reload)

        self.load_history()
        self.history_combo.activated[str].connect(self.on_history)

    def on_history(self, history: str):
        file = f"{d}/{history}"
        
        if os.path.isfile(file):
            self.returned_pixmap = None
            self.pixmap = QPixmap(file)
            self.setPixmap()

    def load_history(self):
        self.history_combo.clear()
        self.history_combo.addItems(os.listdir(d))

    def browse(self):
        pictures_path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        pictures_dir = QDir(pictures_path)

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select an image file",
            pictures_dir.absolutePath(),
            "Images (*.png *.jpg *.jpeg)",
        )
        if file:
            self.pixmap = QPixmap(file)
            self.reload()

    def base64_image(self):
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        self.pixmap.save(buffer, "PNG")
        base64_data = base64.b64encode(byte_array.data())
        return base64_data.decode("utf-8")

    def setPixmap(self):
        pixmap = self.returned_pixmap or self.pixmap
        if self.pixmap:
            self.image_label.setPixmap(pixmap.scaledToHeight(self.image_label.height()))

    def reload(self):
        self.returned_pixmap = None
        self.setPixmap()

        self.request.post(
            "classify2",
            dict(image=self.base64_image()),
        )

    def on_success(self, data: dict):
        disease = data.get("disease")
        disease_image = data.get("disease_image")

        # self.disease_name.setText(disease or "No disease found")

        if disease and disease_image:
            dt = str(datetime.datetime.now()).replace(":", "-")
            filename = f"{d}/{dt}.png"
            image = base64.b64decode(disease_image)

            open(filename, "wb").write(image)

            self.returned_pixmap = QPixmap(filename)
            self.setPixmap()

        self.load_history()


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Poultry Classify with AI")
        self.setFixedSize(550, 500)

        lay = QVBoxLayout(self)

        self.account = Account()
        lay.addWidget(self.account)

        self.home = Home()
        lay.addWidget(self.home)

        self.show_home()

    def show_home(self):
        self.account.hide()
        self.home.show()

    def mousePressEvent(self, _):
        App.instance().quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.setStyleSheet(
            """
            QWidget {
                font-size: 15px;
            }
            Account QLabel#title {
                font-size: 30px;
                font-weight: bold;
            }
            Account QLineEdit {
                padding: 5px;
                min-width: 300px;
            }
            Home QLabel#image_label {
                font-size: 40px;
                font-weight: bold;
            }
            Home QLabel#disease_name {
                font-size: 20px;
                font-weight: bold;
            }
            QComboBox {
                min-width: 200px
            }
        """
        )

        self.win = Window()
        self.win.show()


app = App()
app.exec()
