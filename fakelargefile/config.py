'''
Config for the FakeLargeFile package
'''

COPYING = """\
    Copyright 2014 Lauritz Vesteraas Thaulow

    This file is part of the FakeLargeFile python package.

    FakeLargeFile is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License version 3,
    as published by the Free Software Foundation.

    FakeLargeFile is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU General Affero Public License
    along with FakeLargeFile.  If not, see <http://www.gnu.org/licenses/>.
    """


MEMORY_LIMIT = 1000000000


def set_memory_limit(byte_count):
    """
    Set the memory limit.

    If operations require more memory than this, a MemoryLimitError is raised.
    """
    global MEMORY_LIMIT
    MEMORY_LIMIT = byte_count


def get_memory_limit():
    """
    Get the current memory limit.

    The default memory limit is 1GB
    """
    return MEMORY_LIMIT
