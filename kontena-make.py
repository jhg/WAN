#!/usr/bin/env python3
"""
Kontena


Copyright (C) 2016 Jesus Hernandez Gormaz <jhg.jesus@gmail.com>

Under license: Affero Gnu Public License V3
"""

import sys
import os

from zipfile import ZipFile, is_zipfile


if __name__ == "__main__" and len(sys.argv) >= 3 and is_zipfile(sys.argv[1]):
    linked = False
    if len(sys.argv) >= 4 and sys.argv[3] == '--linked':
        linked = True
    kontena_file = os.path.abspath(sys.argv[1])
    kontena_source = os.path.abspath('kontena.py')
    kontena_make = os.path.abspath(sys.argv[2])
    with open(kontena_make, 'wt') as make:
        with open(kontena_source, 'rt') as source:
            with open(kontena_file, 'rb') as data:
                if not linked:
                    make.write(
                        source.read().replace(
                            '    kontena_file = os.path.abspath(sys.argv[1])\n',
                            '    kontena_file = BytesIO(%s)\n' % str(data.read())
                        ).replace(
                            'import os',
                            ''
                        ).replace(
                            ' and len(sys.argv) >= 2',
                            ''
                        ).replace(
                            '    del sys.argv[1]\n',
                            ''
                        ).replace(
                            'V3\n"""',
                            'V3\n\nEmbbebed zip with source code can has other license and copyright.\n"""'
                        ).replace(
                            "    with open(kontena_file, 'rb') as kontena_file:\n",
                            ''
                        ).replace(
                            '        kontena = KontenaApp(sys.argv)\n',
                            '    kontena = KontenaApp(sys.argv)\n'
                        ).replace(
                            '        kontena.open_app(BytesIO(kontena_file.read()))\n',
                            '    kontena.open_app(BytesIO(kontena_file.read()))\n'
                        ).replace(
                            '        kontena.exe()\n',
                            '    kontena.exe()\n'
                        )
                    )
                else:
                    make.write(
                        '#!/usr/bin/env python3\nfrom kontena import KontenaApp\nfrom io import BytesIO\nimport sys\n\n'
                    )
                    make.write(
                        'if __name__ == "__main__":\n    kontena = KontenaApp(sys.argv)\n    kontena.open_app(BytesIO(%s))\n    kontena.exe()\n' % str(data.read())
                    )
