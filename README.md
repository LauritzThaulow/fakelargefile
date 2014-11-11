fakelargefile
=============

A file-like object that simulates a very large file while requiring very 
little memory.

```python
>>> from fakelargefile import FakeLargeFile, RepeatingSegment, LiteralSegment
>>> flf = FakeLargeFile()
>>> flf.append(RepeatingSegment(start=0, stop="10G", string="spam "))
>>> flf.seek(9990000000)
>>> flf.read(10)
'spam spam '
```

Using segments you can build your fake file layer by layer, using the above
segment types. But its real powers emerge when you go beyond the standard
file-like methods:

```python
>>> flf.insert_literal(start=999999999, string=", sausage, eggs and")
>>> flf[999999990:1000000028]
'spam spam, sausage, eggs and spam spam'
>>> i = flf.index("eggs", 0)
>>> i, flf[i:i + 4]
(1000000010, 'eggs')
```

All these operations are near-instantaneous.

Oh, you're afraid you might ask for a string too large to fit in your memory?
Not a problem, my friend:

```python
>>> from fakelargefile import MemoryLimitError
... try:
...     flf[:]
... except MemoryLimitError:
...     print "Oops"
...
Oops
```
