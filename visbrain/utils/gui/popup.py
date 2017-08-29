"""Create basic popup."""

from PyQt5.Qt import QWidget, QRect
from PyQt5 import QtWidgets

from .screenshot_gui import Ui_Screenshot
from ..guitools import textline2color

__all__ = ('ShortcutPopup', 'ScreenshotPopup')


class ShortcutPopup(QWidget):
    """Popup window with the list of shorcuts."""

    def __init__(self):
        """Init."""
        QWidget.__init__(self)
        self.setGeometry(QRect(400, 200, 700, 600))
        layout = QtWidgets.QGridLayout(self)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setStretchLastSection(False)
        layout.addWidget(self.table)
        # Add column names :
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = self.table.horizontalHeaderItem(0)
        item.setText("Keys")
        self.table.setHorizontalHeaderItem(1, item)
        item = self.table.horizontalHeaderItem(1)
        item.setText("Description")

    def set_shortcuts(self, shdic):
        """Fill table."""
        self.table.setRowCount(len(shdic))
        for num, k in enumerate(shdic):
            self.table.setItem(num, 0, QtWidgets.QTableWidgetItem(k[0]))
            self.table.setItem(num, 1, QtWidgets.QTableWidgetItem(k[1]))


class ScreenshotPopup(Ui_Screenshot):
    """Popup window with the list of shorcuts."""

    def __init__(self, fcn_run, canvas_names=[]):
        """Init."""
        super(ScreenshotPopup, self).__init__()
        self._ss = QtWidgets.QWidget()
        self.setupUi(self._ss)

        # Render entire window / selected canvas :
        self._ssSelect.currentIndexChanged.connect(self._fcn_select_render)
        # Add canvas names :
        self._ssCanvasName.addItems(canvas_names)
        # Image resolution :
        self._ssResolution.currentIndexChanged.connect(self._fcn_resolution)
        # Background color :
        self._ssBgcolorChk.clicked.connect(self._fcn_enable_bgcolor)
        # Run :
        self._ssRun.clicked.connect(fcn_run)

        self._fcn_select_render()
        self._fcn_resolution()

    def _fcn_select_render(self):
        """Render either the entire window / selected canvas."""
        txt = int(self._ssSelect.currentIndex())
        self._ssCanvasW.setVisible(txt == 0)

    def _fcn_resolution(self):
        """Choose resolution method."""
        idx = int(self._ssResolution.currentIndex())
        if idx == 0:  # custom
            self._ssCustomW.setVisible(True)
            self._ssFactorW.setVisible(False)
        elif idx == 1:  # factor
            self._ssCustomW.setVisible(False)
            self._ssFactorW.setVisible(True)

    def _fcn_enable_bgcolor(self):
        """Enable background color."""
        self._ssBgcolor.setEnabled(self._ssBgcolorChk.isChecked())

    def show(self):
        """Show widget."""
        self._ss.show()

    def to_kwargs(self):
        """Get arguments."""
        kwargs = {}
        kwargs['entire'] = int(self._ssSelect.currentIndex()) == 1
        kwargs['canvas'] = str(self._ssCanvasName.currentText())
        resolution = int(self._ssResolution.currentIndex())
        if resolution == 0:
            kwargs['print_size'] = (self._ssWidth.value(),
                                    self._ssHeight.value())
        else:
            kwargs['print_size'] = None
        kwargs['unit'] = str(self._ssUnit.currentText())
        kwargs['dpi'] = self._ssDpi.value()
        kwargs['factor'] = self._ssFactor.value()
        kwargs['autocrop'] = self._ssAutocrop.isChecked()
        if self._ssBgcolorChk.isChecked():
            bgcolor = textline2color(str(self._ssBgcolor.text()))[1]
            kwargs['bgcolor'] = bgcolor
        else:
            kwargs['bgcolor'] = None
        kwargs['transparent'] = self._ssTransp.isChecked()
        return kwargs