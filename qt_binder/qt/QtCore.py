from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtCore import *  # noqa

    from PyQt4.QtCore import pyqtProperty as Property  # noqa
    from PyQt4.QtCore import pyqtSignal as Signal  # noqa
    from PyQt4.QtCore import pyqtSlot as Slot  # noqa
    from PyQt4.Qt import QCoreApplication  # noqa
    from PyQt4.Qt import Qt  # noqa

    __version__ = QT_VERSION_STR
    __version_info__ = tuple(map(int, QT_VERSION_STR.split('.')))

else:
    try:
        from PySide import __version__, __version_info__  # noqa
    except ImportError:
        pass
    from PySide.QtCore import *  # noqa
