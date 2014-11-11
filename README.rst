FakeLargeFile
=============

Intro
-----

A ``FakeLargeFile`` instance is a file-like object that simulates a very large
file while requiring very little memory and being smart about operations.

>>> from fakelargefile import FakeLargeFile, RepeatingSegment
>>> flf = FakeLargeFile()
>>> flf.append(RepeatingSegment(start=0, stop="10G", string="spam "))
>>> flf.seek(9990000000)
>>> flf.read(10)
'spam spam '

You can build your fake file layer by layer by using the ``overwrite`` method,
or from beginning to end by using the ``append`` method, whatever suits your
needs. Your building blocks are segment types like literal and repeating 
segments, and you may implement custom segment types.

The real powers of ``FakeLargeFile`` emerge when you go beyond the standard 
file-like methods:

>>> flf.insert_literal(start=1000000005, string="ham ")
>>> flf.insert_literal(start=999999999, string=", sausage, eggs and")
>>> flf[999999990:1000000033]
'spam spam, sausage, eggs and spam ham spam '
>>> i = flf.index("eggs and spam", 0)
>>> i, flf[i:i + 13]
(1000000010, 'eggs and spam')
>>> flf.delete(0, 999999990)
>>> flf[:43]
'spam spam, sausage, eggs and spam ham spam '

All these operations are smart. How fast they are depend on the number of
segments they work on and their underlying data, not on how many bytes that
seemingly need moving or searching. All the above code examples take about
0.3 milliseconds to execute altogether, not counting the import statements.

Operations like ``flf[:43]`` return real python strings. You might worry about
accidently executing ``flf[:100000000000]``. Well, worry no more: there's 
built-in protection against accidently creating very large strings. If the 
memory required by some operation is above a certain limit (which you can
change yourself), a ``MemoryLimitError`` exception will be raised before the
string is actually built.



Developers note
---------------

This package is first and foremost an exercise in doing a python package
*the right way*. I'm trying to cover all the bases. Documentation, tests
with full coverage, commit messages, pep8, structure, code comments, 
the works.

As of this writing, not all the bases have been visited yet. Here's a short
TODO list:

- full documentation
- get code to release quality and functionality

Please tell me what I can do to improve this package!
