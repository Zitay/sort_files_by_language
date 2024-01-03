#!c:\users\itay\pycharmprojects\sort_files_by_language\new_env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'tika==2.6.0','console_scripts','tika-python'
__requires__ = 'tika==2.6.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('tika==2.6.0', 'console_scripts', 'tika-python')()
    )
