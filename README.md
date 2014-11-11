fakelargefile
=============

*This package is first and foremost an exercise in doing a python package*
the right way. *I'm trying to do check all the boxes. Documentation, tests
with full coverage, commit messages, pep8, structure, code comments, 
the works. Please tell me what I can do to improve this package!*

A FakeLargeFile is a file-like object that simulates a very large file while
requiring very little memory and being smart about operations.

```python
>>> from fakelargefile import FakeLargeFile, RepeatingSegment
>>> flf = FakeLargeFile()
>>> flf.append(RepeatingSegment(start=0, stop="10G", string="spam "))
>>> flf.seek(9990000000)
>>> flf.read(10)
'spam spam '
```

Using segments you can build your fake file layer by layer, using segment 
types like literal and repeating segments. But its real powers emerge when
you go beyond the standard file-like methods:


```python
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
```

All these operations are smart about how they work, and how fast they are
depend on the complexity and number of the segments, not on how many bytes
that seemingly need moving or searching.

Indexing into the fakelargefile, and various other operations, return real 
python strings, so there's built-in protection against accidently creating
very large strings. If the memory limit would be broken by some operation,
a MemoryLimitError exception will be raised before it is even attempted.

