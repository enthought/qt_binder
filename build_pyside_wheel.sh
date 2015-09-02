#!/bin/bash
set -e

if [ ${TRAVIS_PYTHON_VERSION} == "2.7" ]; then
    PYSIDE_WHEEL=PySide-1.2.2-cp27-none-linux_x86_64.whl
elif [ ${TRAVIS_PYTHON_VERSION} == "3.4" ]; then
    PYSIDE_WHEEL=PySide-1.2.2-cp34-cp34m-linux_x86_64.whl
fi

if [ -f "${HOME}/.cache/${PYSIDE_WHEEL}" ]; then
   echo "PySide wheel found"
else
   echo "Building PySide"

   git clone https://github.com/PySide/pyside-setup.git
   cd pyside-setup

   # The normal pyside repos only have the right tags upto 1.1.1
   # So we need to replace the repos with the newer ones
   git submodule deinit .
   git rm sources/pyside
   git rm sources/shiboken
   git submodule add --name sources/shiboken -- https://github.com/PySide/shiboken2.git sources/shiboken
   git submodule add --name sources/pyside -- https://github.com/PySide/pyside2.git sources/pyside
   git submodule sync

   # now it is time to build the pyside wheels
   python setup.py bdist_wheel --qmake=/usr/bin/qmake-qt4 --version=1.2.2 --jobs=3
   ls dist/
   cp dist/*.whl ${HOME}/.cache/
fi

pip install "${HOME}/.cache/${PYSIDE_WHEEL}"
