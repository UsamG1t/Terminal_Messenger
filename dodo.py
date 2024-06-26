import os
from glob import glob
from doit.tools import create_folder

HTMLINDEX = "_build/html/index.html"

def task_html():
    """Generate HTML docs."""
    return {
        'actions': ['sphinx-build -M html ./docs msg/docs/_build'],
        'file_dep': glob('docs/*.rst') + glob('msg/*/*.py'),
        'task_dep': ['i18n'],
        'targets': ['docs/_build']
    }

def task_erase():
    """Erase all trash"""
    return {
        'actions': ['git clean -xdf']
    }


def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract --keywords=ngettext:2,3 --keywords=_:2 msg -o msg.pot'],
            'file_dep': glob('msg/server/*.py'),
            'targets': ['msg.pot'],
           }

def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -D msg -d po -l ru_RU.UTF-8 -i msg.pot'],
            'file_dep': ['msg.pot'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/msg.po'],
           }

def task_mo():
    return {
            'actions': [
                (os.makedirs, ["msg/ru_RU.UTF-8/LC_MESSAGES"],{"exist_ok": True}),
                'pybabel compile -D msg -l ru_RU.UTF-8 -d msg -i po/ru_RU.UTF-8/LC_MESSAGES/msg.po'
                ],
            'file_dep': ['po/ru_RU.UTF-8/LC_MESSAGES/msg.po'],
            'targets': ['msg/msg.mo'],
            }

def task_i18n():
    """Compile translations."""
    return {
            'actions': None,
            'task_dep': ['pot', 'po', 'mo'],
           }

def task_test():
    """Update translations."""
    return {
            'actions': ['python3.10 -m unittest'],
            'task_dep': ['i18n'],
           }

def task_sdist():
    """Build distributive."""
    return {
            'actions': ['python3.10 -m build -s -n'],
            'task_dep': ['erase'],
           }

def task_wheel():
    """Build binary wheel."""
    return {
            'actions': ['python3.10 -m build -w'],
            'task_dep': ['i18n', 'html'],
           }
