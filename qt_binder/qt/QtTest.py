from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtTest import *  # noqa

else:
    from PySide.QtTest import *  # noqa
