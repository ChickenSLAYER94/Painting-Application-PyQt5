"""
Name: Krishna Ramdam
Student Number: 3015281
Assignment: 02
Subject: HCI & GUI Programming
Year: Third
"""

import sys
from enum import Enum
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QGridLayout, QAction, QGroupBox, QRadioButton, QSlider, \
    QLabel, QPushButton, QApplication, QFileDialog, QColorDialog, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QImage, QPen, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
from qtpy import QtCore, QtGui

# this is one of the menu in title bar which allows to choose different shapes
class DrawMode(Enum):
    Point = 1
    Rectangle = 2
    Ellipse = 3

# this will contain brush thickness, brush styles, brush cap and brush color
class ToolBox(QWidget):
    def __init__(self):
        super().__init__()

      # setting size of toolbar
        self.setMaximumWidth(180)
        self.setMinimumWidth(180)

        # making toolbar vertical
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

# it signifies drawing zone
class DrawingZone(QWidget):
    def __init__(self):
        super().__init__()

        # here we initialize images which will be resize later on
        self.resizeSavedImage = QImage(0, 0, QImage.Format_RGB32)
        self.savedImage = QImage(0, 0, QImage.Format_RGB32)

       # creating white canvas
        self.image = QImage(self.width(), self.height(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

       # This is the default selection of function that we used in out paint
        self.drawing = False
        self.brushSize = 1
        self.brushColor = Qt.black
        self.brushStyle = Qt.SolidLine
        self.brushCap = Qt.RoundCap
        self.brushJoin = Qt.RoundJoin
        self.drawMode = DrawMode.Point

        # the size of canvas of our program will not go beyound minimum width of 300
        self.lastPoint = QPoint()
        self.setMinimumWidth(300)

        # creating canvas for shapes like rectangle and ellipse
        self.pix = QPixmap(QtCore.QSize(1700, 945))

        ''' here we are making canvas transparent so that the shapes we created will projected in 
        main canvas (i.e painter.drawImage(self.rect(), self.image, self.image.rect()) which is on line 83.'''
        self.pix.fill(Qt.transparent)
        self.begin, self.destination = QPoint(), QPoint()

    # this method is called when our widget is resized
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    # this method runs when the painting in Drawing zone initiated.
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())
        painter.drawPixmap(QPoint(), self.pix)

        # when rectangle shape is selected it will give preview of shape when mousePressEvent and mouseMoveEvent is runs
        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            if self.drawMode == DrawMode.Rectangle:
                painter.drawRect(rect.normalized())
            # Gives preview of ellipse while on mouseMoveEvent
            if self.drawMode == DrawMode.Ellipse:
                painter.drawEllipse(rect.normalized())

    # this method will run when ever mouse is left button is pressed
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # if the pressed button is the left button
            if self.drawMode == DrawMode.Point:
                self.drawing = True  # enter drawing mode
                self.lastPoint = event.pos()  # save the location of the mouse press as the lastPoint
                print(self.lastPoint)  # print the lastPoint for debugging purposes

            # mousePressEvent for rectangle shape
            elif self.drawMode == DrawMode.Rectangle:
                self.begin = event.pos()
                self.destination = self.begin

            # mousePressEvent for ellipse shape
            elif self.drawMode == DrawMode.Ellipse:
                self.begin = event.pos()
                self.destination = self.begin

            self.update()
    # this method will run after mousePressEvent runs
    # this method will keep on running unless method mouseReleaseEvent is triggered
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton & self.drawing & (self.drawMode == DrawMode.Point):  # if there was a press, and it was the left button and we are in drawing mode
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brish size, line type, cap type, join type. Images available here http://doc.qt.io/qt-5/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, self.brushStyle, self.brushCap, self.brushJoin))
            painter.drawLine(self.lastPoint,
                             event.pos())  # draw a line from the point of the original press to the point to where the mouse was dragged to
            self.lastPoint = event.pos()  # set the last point to refer to the point we have just moved to, this helps when drawing the next line segment

        # mouseMoveEvent for rectangle shape
        elif event.buttons() & Qt.LeftButton & (self.drawMode == DrawMode.Rectangle):
            self.destination = event.pos()

        # mouseMoveEvent for ellipse shape
        elif event.buttons() & Qt.LeftButton & (self.drawMode == DrawMode.Ellipse):
            self.destination = event.pos()

        self.update()  # call the update method of the widget which calls the paintEvent of this class

    '''this method is triggered when we release pressed button(i e. left button on mouse)
    after this method Point, shapes and different function used in this paint app is visible on the canvas'''
    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            # this will save the image before initiation of adjustment.
            self.savedImage = self.resizeSavedImage
            self.resizeSavedImage = self.image
            self.drawing = False

        #mouseReleaseEvent for rectangle shape
        elif event.button() & Qt.LeftButton & (self.drawMode == DrawMode.Rectangle):
            rect = QRect(self.begin, self.destination)
            painter = QPainter(self.pix)
            painter.drawRect(rect.normalized())
            self.begin, self.destination = QPoint(), QPoint()
            self.update()

        # mouseReleaseEvent for ellipse shape
        elif event.button() & Qt.LeftButton & (self.drawMode == DrawMode.Ellipse):
            elli = QRect(self.begin, self.destination)
            painter = QPainter(self.pix)
            painter.drawEllipse (elli.normalized())
            self.begin, self.destination = QPoint(), QPoint()
            self.update()

        self.update()

class PaintingApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        # set window title
        self.setWindowTitle("Paint Application")

        # set the windows dimensions
        top = 400
        left = 400
        width = 800
        height = 600
        self.setGeometry(top, left, width, height)
        self.setWindowIcon(QIcon("./icons/paint-brush.png"))

        '''Setting up grid layout'''
        self.grid = QGridLayout()
        self.box = ToolBox()
        self.imageArea = DrawingZone()
        self.setBrushSlider()
        self.setBrushStyle()
        self.setBrushCap()
        self.setBrushJoin()
        self.setColorChanger()

        # here we are adjusting position of our toolbox and drawingZone in our main window
        self.grid.addWidget(self.box, 0, 10, 0, 1)
        self.grid.addWidget(self.imageArea, 0, 1, 1, 1)

        win = QWidget()
        win.setLayout(self.grid)
        self.setCentralWidget(win)

        mainMenu = self.menuBar()
        fileM = mainMenu.addMenu(" File")  # the space is required as "File" is reserved in Mac
        drawM = mainMenu.addMenu("Draw")
        help = mainMenu.addMenu("Help")

        # creating save function and adding it inside file (fileM) in menu bar
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileM.addAction(saveAction)

        # if we click save from menubar this will trigger the code
        saveAction.triggered.connect(self.save)

        # creating open function and adding it inside file (fileM) in menu bar
        openAction = QAction(QIcon("./icons/open.png"), "Open", self)
        openAction.setShortcut("Ctrl+O")
        fileM.addAction(openAction)

        # if we click open from menubar this will trigger the code
        openAction.triggered.connect(self.open)

        # creating clear function and adding it inside file (fileM) in menu bar
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)
        clearAction.setShortcut("Ctrl+C")
        fileM.addAction(clearAction)

        # if we click clear from menubar this will trigger the code
        clearAction.triggered.connect(self.clear)

        # when point is selected from draw in menubar, it will be used to draw lines in our canvas
        self.pointAction = QAction("Point", self, checkable=True)
        self.pointAction.setShortcut("Ctrl+P")
        self.pointAction.setChecked(True)
        drawM.addAction(self.pointAction)

        # triggers Point function
        self.pointAction.triggered.connect(lambda: self.changeDrawMode(self.pointAction))

        # when rectange is selected from draw in menubar, it will be used to draw rectangle in our canvas
        self.RectangleAction = QAction("Rectangle", self, checkable=True)
        self.RectangleAction.setShortcut("Ctrl+L")
        drawM.addAction(self.RectangleAction)

        # triggers rectangle functionality
        self.RectangleAction.triggered.connect(lambda: self.changeDrawMode(self.RectangleAction))

        # when ellipse is selected from draw in menubar, it will be used to draw rectangle in our canvas
        self.EllipseAction = QAction("Ellipse", self, checkable=True)
        self.EllipseAction.setShortcut("Ctrl+E")
        drawM.addAction(self.EllipseAction)

        # triggers ellipse functionality
        self.EllipseAction.triggered.connect(lambda: self.changeDrawMode(self.EllipseAction))

        # when exit is selected from file in menubar, it will terminate the program
        exitAction = QAction(QIcon("./icons/exit.png"), "Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        fileM.addAction(exitAction)

        # triggers exit functionality
        exitAction.triggered.connect(self.exitProgram)

        # when about is selected from help option in menubar, it will display info about our paint app
        aboutAction = QAction(QIcon("./icons/about.png"), "About", self)
        aboutAction.setShortcut("Ctrl+I")
        help.addAction(aboutAction)

        # triggers about information
        aboutAction.triggered.connect(self.about)

        # this action is triggered after going to help option in menubar, it will display helpful info of our paint app
        helpAction = QAction(QIcon("./icons/help.png"), "Help", self)
        helpAction.setShortcut("Ctrl+H")
        help.addAction(helpAction)

        # triggers help functionality
        helpAction.triggered.connect(self.help)

        # updates imageArea
        self.imageArea.update()

    # from menubar if we choose draw and select one of three variant of shape(like rectangle).
    # This method is used to trigger one user selected shape variant
    def changeDrawMode(self, check):
        if check.text() == "Point":
            self.EllipseAction.setChecked(False)
            self.pointAction.setChecked(True)
            self.RectangleAction.setChecked(False)
            self.imageArea.drawMode = DrawMode.Point
        elif check.text() == "Rectangle":
            self.EllipseAction.setChecked(False)
            self.pointAction.setChecked(False)
            self.RectangleAction.setChecked(True)
            self.imageArea.drawMode = DrawMode.Rectangle
        elif check.text() == "Ellipse":
            self.pointAction.setChecked(False)
            self.EllipseAction.setChecked(True)
            self.RectangleAction.setChecked(False)
            self.imageArea.drawMode = DrawMode.Ellipse

    # this method created to change the brush thickness
    def setBrushSlider(self):
        self.thicknessSlider = QGroupBox("Brush Thickness")
        self.thicknessSlider.setMaximumHeight(100)

        # set slider min and max value
        self.sizeOfBrush = QSlider(Qt.Horizontal)
        self.sizeOfBrush.setMinimum(1)
        self.sizeOfBrush.setMaximum(40)
        self.sizeOfBrush.valueChanged.connect(self.sizeSliderChange)
        
        # displaying size in our program
        self.brushSizeLabel = QLabel()
        self.brushSizeLabel.setText("%s px" % self.imageArea.brushSize)

        sliderLayout = QVBoxLayout()
        sliderLayout.addWidget(self.sizeOfBrush)
        sliderLayout.addWidget(self.brushSizeLabel)
        self.thicknessSlider.setLayout(sliderLayout)
        self.box.vbox.addWidget(self.thicknessSlider)

    # This method will change brush thickness according to user slider input
    def sizeSliderChange(self, value):
        self.imageArea.brushSize = value
        self.brushSizeLabel.setText("%s px" % value)

    # method to alter type of brush
    def setBrushStyle(self):
        self.brush_line_type = QGroupBox("Brush style")
        self.brush_line_type.setMaximumHeight(100)
 
        #created radio button to select one of three stypes of brush
        self.styleSolid = QRadioButton(" Solid")
        self.styleSolid.setIcon(QIcon("./icons/solid.png"))
        self.styleSolid.setIconSize(QSize(32, 64))
        self.styleSolid.clicked.connect(lambda: self.changeBrushStyle(self.styleSolid))

        self.styleDash = QRadioButton(" Dash")
        self.styleDash.setIcon(QIcon("./icons/dash.png"))
        self.styleDash.setIconSize(QSize(32, 64))
        self.styleDash.clicked.connect(lambda: self.changeBrushStyle(self.styleDash))

        self.styleDot = QRadioButton(" Dot")
        self.styleDot.setIcon(QIcon("./icons/dot.png"))
        self.styleDot.setIconSize(QSize(32, 64))
        self.styleDot.clicked.connect(lambda: self.changeBrushStyle(self.styleDot))

        # add in the main layout
        self.styleSolid.setChecked(True)
        brushStyle = QVBoxLayout()
        brushStyle.addWidget(self.styleSolid)
        brushStyle.addWidget(self.styleDash)
        brushStyle.addWidget(self.styleDot)
        self.brush_line_type.setLayout(brushStyle)
        self.box.vbox.addWidget(self.brush_line_type)

    # method to change the brush caps
    def setBrushCap(self):
        self.capType = QGroupBox("Brush cap")
        self.capType.setMaximumHeight(100)

        # created radio button to choose from one of 3 brush cap type
        self.capSquare = QRadioButton("Square")
        self.capSquare.clicked.connect(lambda: self.changeBrushCap(self.capSquare))
        self.capFlat = QRadioButton("Flat")
        self.capFlat.clicked.connect(lambda: self.changeBrushCap(self.capFlat))
        self.capRound = QRadioButton("Round")
        self.capRound.clicked.connect(lambda: self.changeBrushCap(self.capRound))

        # add in the main layout
        self.capRound.setChecked(True)
        qv = QVBoxLayout()
        qv.addWidget(self.capSquare)
        qv.addWidget(self.capFlat)
        qv.addWidget(self.capRound)
        self.capType.setLayout(qv)
        self.box.vbox.addWidget(self.capType)

    # method to change the brush caps
    def setBrushJoin(self):
        self.brush_join_type = QGroupBox("Brush join")
        self.brush_join_type.setMaximumHeight(100)

        # created radio button to choose from one of 3 brush join type
        self.joinRound = QRadioButton("Round")
        self.joinRound.clicked.connect(lambda: self.changeBrushJoin(self.joinRound))
        self.joinMiter = QRadioButton("Miter")
        self.joinMiter.clicked.connect(lambda: self.changeBrushJoin(self.joinMiter))
        self.joinBevel = QRadioButton("Bevel")
        self.joinBevel.clicked.connect(lambda: self.changeBrushJoin(self.joinBevel))

        # add in the main layout
        self.joinRound.setChecked(True)
        brushJoinLayout = QVBoxLayout()
        brushJoinLayout.addWidget(self.joinRound)
        brushJoinLayout.addWidget(self.joinMiter)
        brushJoinLayout.addWidget(self.joinBevel)
        self.brush_join_type.setLayout(brushJoinLayout)
        self.box.vbox.addWidget(self.brush_join_type)

    # method which displays color selection 
    def showColorPrompt(self):
        self.col = QColorDialog.getColor()
        if self.col.isValid():
            self.brush_colour.setStyleSheet("background-color: %s" % self.col.name())
            self.imageArea.brushColor = self.col

    # driver method for setBrushJoin to change Brush join according to user selection
    def changeBrushJoin(self, btn):
        if btn.text() == "Round":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.RoundJoin
        if btn.text() == "Miter":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.MiterJoin
        if btn.text() == "Bevel":
            if btn.isChecked():
                self.imageArea.brushJoin = Qt.BevelJoin

    # driver method for setBrushCap to change Brush Style according to user selection
    def changeBrushStyle(self, btn):
        if btn.text() == " Solid":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.SolidLine
        if btn.text() == " Dash":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.DashLine
        if btn.text() == " Dot":
            if btn.isChecked():
                self.imageArea.brushStyle = Qt.DotLine

    # driver method for setBrushCap to change Brush Cap according to user selection
    def changeBrushCap(self, btn):
        if btn.text() == "Square":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.SquareCap
        if btn.text() == "Flat":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.FlatCap
        if btn.text() == "Round":
            if btn.isChecked():
                self.imageArea.brushCap = Qt.RoundCap

    # driver method of showColorPrompt which set the user selected color
    def setColorChanger(self):
        self.groupBoxColor = QGroupBox("Color")
        self.groupBoxColor.setMaximumHeight(100)

        self.col = QColor(0, 0, 0)
        self.brush_colour = QPushButton()
        self.brush_colour.setFixedSize(60, 60)
        self.brush_colour.clicked.connect(self.showColorPrompt)
        self.brush_colour.setStyleSheet("background-color: %s" % self.col.name())
        self.box.vbox.addWidget(self.brush_colour)

        # add to main layout
        colorBoxLayout = QVBoxLayout()
        colorBoxLayout.addWidget(self.brush_colour)
        self.groupBoxColor.setLayout(colorBoxLayout)

        self.box.vbox.addWidget(self.groupBoxColor)

    
    # This method is used to resize the main window
    def resizeEvent(self, a0: QtGui.QResizeEvent):
        if self.imageArea.resizeSavedImage.width() != 0:
            self.imageArea.image = self.imageArea.resizeSavedImage.scaled(self.imageArea.width(), self.imageArea.height(), QtCore.Qt.IgnoreAspectRatio)
        self.imageArea.update()

    # this method initiate save functionality for saveAction
    def save(self):
        savingPath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if savingPath == "":
            return # do nothing and return

        self.imageArea.image.save(savingPath)

    # this method is used to open user selected file from their own storage and display it in our main canvas
    def open(self):
        openingPath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if openingPath == "":
            return
        with open(openingPath, 'rb') as f:
            content = f.read()

        # Update and scale drawing zone and load the image
        self.imageArea.image.loadFromData(content)
        self.imageArea.image = self.imageArea.image.scaled(self.imageArea.width(), self.imageArea.height(),
                                                           QtCore.Qt.IgnoreAspectRatio)
        self.imageArea.resizeSavedImage = self.imageArea.image
        self.imageArea.update()

    # this is driver method for clear action
    # which will clear everything in canvas
    def clear(self):
        self.imageArea.pix.fill(QtGui.QColor(0, 0, 0, 0))
        self.imageArea.image.fill(Qt.white)
        self.imageArea.update()

  # Terminates program
    def exitProgram(self):
        QtCore.QCoreApplication.quit()

    #this is driver method for about action which display the information about our program
    def about(self):
        QMessageBox.about(self, "About QPaint",
                          "<p>This paint program is made with PYQT "
                          ".  Here you can draw with different color and use shapes."
                          " You can save your created file or open you file.</p>")

    # this is driver method for help action which display helpful information to operate our program
    def help(self):
        msg = QMessageBox()
        msg.setText("Help"
                    "<p>Welcome on Paint Application.</p> "
                    "<p>On the menu bar you can see three option: File   Draw    Help </p>"
                    "<p>Inside each menubar you can have function to save, open</p> "
                    "<p>Get information about application or choose from different shapes to draw</p>"
                    "<p>On the right hand side you can see the toolbar where you can choose."
                    "<p>Brush Size, Brush Cap and Brush Color.</p>"
                    "Hope you will enjoy our application."
                    "If you find any difficulty to run."
                    "Please to contact at krisrdm94@gmail.com</p>")
        msg.setWindowTitle("Help")
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintingApplication()
    window.show()
    app.exec()
