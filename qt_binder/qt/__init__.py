from pyface.qt import is_qt4, is_qt5, qt_api  # noqa

if qt_api == 'pyside2':
    # FIXME: Work around https://bugreports.qt.io/browse/PYSIDE-1093
    # This is not a general solution, since most other Qt-using libraries might
    # get run first. But this is sufficient to get the test suite to run for
    # local development.
    from pyface.qt.QtGui import QApplication

    if QApplication.startingUp():
        app = QApplication([])
