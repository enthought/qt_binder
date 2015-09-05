from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtScript import *  # noqa

else:
    from PySide.QtScript import *  # noqa
