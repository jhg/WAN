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
    kontena_file = os.path.abspath(sys.argv[1])
    kontena_source = os.path.abspath('kontena.py')
    kontena_make = os.path.abspath(sys.argv[2])
    with open(kontena_make, 'wt') as make:
        with open(kontena_source, 'rt') as source:
            with open(kontena_file, 'rb') as data:
                make.write(
                    source.read().replace(
                        '    kontena_file = os.path.abspath(sys.argv[1])\n',
                        '    kontena_file = BytesIO(%s)\n' % str(data.read())
                    ).replace(
                        'import os',
                        'from io import BytesIO'
                    ).replace(
                        ' and len(sys.argv) >= 2 and is_zipfile(sys.argv[1])',
                        ''
                    ).replace(
                        '    del sys.argv[1]\n',
                        ''
                    ).replace(
                        'V3\n"""',
                        'V3\n\nEmbbebed zip with source code can has other license and copyright.\n"""'
                    )
                )