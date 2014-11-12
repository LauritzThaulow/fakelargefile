'''
Errors for use in this package
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


class NoContainingSegment(Exception):
    pass


class MemoryLimitError(Exception):
    """
    Raised when an operation would require excessive amounts of memory.

    If an operation, like for example creating a string out of a
    FakeLargeFile, would require more memory than the return value of
    :py:func:`fakelargefile.config.get_memory_limit`, then this exception
    is raised.
    """
    pass
