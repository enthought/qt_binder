from . import qt_api

if qt_api == 'pyqt':
    # QtUiTools does not exist in PyQt! Luckily it only defines one class.
    from .QtCore import QObject

    class QUiLoader(QObject):
        def addPluginPath(self, path):
            pass

        def availableLayouts(self):
            pass

        def availableWidgets(self):
            pass

        def clearPluginPaths(self):
            pass

        def isLanguageChangeEnabled(self):
            pass

        def isScriptingEnabled(self):
            pass

        def isTranslationEnabled(self):
            pass

        def load(self, device, parentWidget=None):
            pass

        def pluginPaths(self):
            pass

        def registerCustomWidget(self, customWidgetType):
            pass

        def setLanguageChangeEnabled(self, enabled):
            pass

        def setScriptingEnabled(self, enabled):
            pass

        def setTranslationEnabled(self, enabled):
            pass

        def setWorkingDirectory(self, dir):
            pass

        def workingDirectory(self):
            pass

    # Clean up the namespace pollution
    del QObject

else:
    from PySide.QtUiTools import *  # noqa
