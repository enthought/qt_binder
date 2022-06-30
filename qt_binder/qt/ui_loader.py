# (C) Copyright 2014-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from . import is_qt4, qt_api

if qt_api.startswith('pyqt'):
    def load_ui(path):
        from collections import Counter
        if is_qt4:
            from PyQt4 import uic
        else:
            from PyQt5 import uic

        ui = uic.loadUi(path)
        names_hist = Counter()
        for child in ui.children():
            name = child.objectName()
            if name:
                names_hist[name] += 1

        names = []
        for name, count in names_hist.items():
            if count == 1 and not name.startswith('_'):
                names.append(name)

        return ui, names

else:
    def load_ui(path):
        from collections import Counter
        if qt_api == 'pyside':
            from PySide.QtUiTools import QUiLoader
        elif qt_api == 'pyside2':
            from PySide2.QtUiTools import QUiLoader
        elif qt_api == 'pyside6':
            from PySide6.QtUiTools import QUiLoader
        else:
            raise RuntimeError(f"Unrecognized qt_api = {qt_api!r}")

        class RecordingUiLoader(QUiLoader):
            """ Record the names of widgets as they are created.
            """

            def __init__(self, *args, **kwds):
                self.names = Counter()
                super(RecordingUiLoader, self).__init__(*args, **kwds)

            def to_be_bound(self):
                """ Return the names of child widgets/layouts to be bound.
                """
                names = []
                for name, count in self.names.items():
                    if count == 1 and not name.startswith('_'):
                        names.append(name)
                return names

            def createLayout(self, className, parent=None, name=u''):
                if name:
                    self.names[name] += 1
                layout = super(RecordingUiLoader, self).createLayout(
                    className, parent, name)
                return layout

            def createWidget(self, className, parent=None, name=u''):
                if name:
                    self.names[name] += 1
                widget = super(RecordingUiLoader, self).createWidget(
                    className, parent, name)
                return widget

        loader = RecordingUiLoader()
        ui = loader.load(path)
        names = loader.to_be_bound()
        # Exclude the root object from this list as it is always bound to the
        # UIFile itself.
        self_name = ui.objectName()
        if self_name in names:
            names.remove(self_name)

        return ui, names
