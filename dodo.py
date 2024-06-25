
from glob import glob
from doit.tools import create_folder

HTMLINDEX = "_build/html/index.html"

def task_html():
    """Generate HTML docs."""
    return {
        # 'actions': ['sphinx-build -M html "Documentation/docs" "msg/_build"'],
        # 'file_dep': ["Documentation/docs/index.rst", "Documentation/docs/server_documentation.rst", "msg/server/__init__.py"],
        'task_dep': ['i18n'],
        'targets': [HTMLINDEX]
    }

def task_erase():
    """Erase all trash"""
    return {
        'actions': ['git clean -xdf']
    }


def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract --keywords=ngettext:2,3 --keywords=gettext:2 msg -o msg/MSG.pot'],
            'file_dep': glob('msg/server/*.py'),
            'targets': ['msg/MSG.pot'],
           }

def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -D MSG_Locale -d msg/po -l ru_RU.UTF-8 -i msg/MSG.pot'],
            'file_dep': ['msg/MSG.pot'],
            'targets': ['msg/po/ru_RU.UTF-8/LC_MESSAGES/MSG_Locale.po'],
           }

def task_i18n():
    """Compile translations."""
    return {
            'actions': [
                (create_folder, [f'msg/po/ru_RU.UTF-8/LC_MESSAGES']),
                f'pybabel compile -D MSG_Locale -l ru_RU.UTF-8 -i msg/po/ru_RU.UTF-8/LC_MESSAGES/MSG_Locale.po -d msg/po'
                       ],
            'file_dep': ['msg/po/ru_RU.UTF-8/LC_MESSAGES/MSG_Locale.po'],
            'targets': ['msg/po/ru_RU.UTF-8/LC_MESSAGES/MSG_Locale.mo'],
           }

def task_test():
    """Update translations."""
    return {
            # 'actions': ['python3.10 -m unittest test_client_server.py test_client.py'],
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
