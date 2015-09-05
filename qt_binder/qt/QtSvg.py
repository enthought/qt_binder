from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtSvg import *  # noqa

else:
    from PySide.QtSvg import *  # noqa
