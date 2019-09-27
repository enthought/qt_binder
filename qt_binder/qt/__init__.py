from pyface.qt import is_qt4, is_qt5, qt_api  # noqa

if qt_api == 'pyside2':
    # Work around https://bugreports.qt.io/browse/PYSIDE-1093
    from pyface.qt.QtGui import QApplication

    if QApplication.startingUp():
        app = QApplication([])
