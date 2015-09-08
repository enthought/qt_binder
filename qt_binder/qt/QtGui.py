from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.Qt import QKeySequence, QTextCursor  # noqa
    from PyQt4.QtGui import *  # noqa

else:
    from PySide.QtGui import *  # noqa
