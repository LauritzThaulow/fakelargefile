'''
These classes represent segments of the large file
'''


from abc import ABCMeta, abstractmethod


class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable_):
        callable_.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable_)


segment_types = []


def register_segment(cls):
    segment_types.append(cls)
    return cls


class AbstractSegment(object):

    __metaclass__ = ABCMeta

    def __init__(self, start, size):
        self.start = start
        self.size = size

    def intersects(self, start, stop):
        """
        Return True if some part of other is inside self.

        Returns True even if other is of length 0, if it is *inside* self.

        Returns False if other is merely adjacent.
        """
        if self.start < stop < self.stop:
            return True
        elif self.start < start < self.stop:
            return True
        return False

    def intersects_segment(self, other):
        """
        Convenience method for self.intersects(other.start, other.stop)
        """
        return self.intersects(other.start, other.stop)

    def cut(self, start, stop):
        """
        Parts left after removing part between start and stop.

        Cuts from and including start to and not including stop.

        The start to stop interval has to intersect self, or a ValueError is
        raised.
        """
        if not self.intersects(start, stop):
            raise ValueError(
                "Cant cut from {} to {} on segment from {} to {}".format(
                    start, stop, self.start, self.stop))
        if start <= self.start < stop < self.stop:
            return [self[stop:]]
        elif self.start < start < self.stop <= stop:
            return [self[:start]]
        elif self.start < start <= stop < self.stop:
            return [self[:start], self[stop:]]
        else:
            raise ValueError(
                "Unforseen case: does {}->{} intersect {}->{}".format(
                    start, stop, self.start, self.stop))

    def __len__(self):
        """
        The lenght of the segment in bytes.
        """
        return self.size

    @property
    def stop(self):
        """
        Return the positon of the byte after the last byte of this segment.
        """
        return self.start + self.size

    @abstractmethod
    def __str__(self):
        """
        Return the entire object as a string.

        .. warning: Actually builds a string representation of something that
           may be extremely large. Doesn't care at all about memory
           consumption. Should only be used when you know this is not a
           problem.
        """
        pass

    @abstractclassmethod
    def example(cls, start, size):  # @NoSelf
        """
        Return an example segment of this class with the given size and start.
        """
        pass

    @abstractmethod
    def __getitem__(self, slice_):
        """
        Slicing implementation for each segment subclass.

        Only these cases need to be implemented:

        - slice from start to some point in the middle
        - slice from some point in the middle to the end

        For the last case, the start point of the returned segment should be
        such that ``segment[x:].start == segment.start + x``.

        Any unsupported case should raise an IndexError.
        """
        pass

    @abstractmethod
    def copy(self, start=None):
        """
        Return a copy of this segment, possibly shifted to start elsewhere.

        This should always be true, no matter the value of ``x``::

            str(self) == str(self.copy(start=x))

        """
        pass


@register_segment
class StaticSegment(AbstractSegment):
    def __init__(self, start, text):
        super(StaticSegment, self).__init__(start, len(text))
        self.text = text

    def __str__(self):
        return self.text

    @classmethod
    def example(cls, start, size):
        basis = """\
aslkjf aslkjf lkasjdf lk jwelk vnzlkewlnas alksfjasdjflkajsdlfkj dsalf ljkasd
sadlf jl awlekjfasldvj oienzl nvlan lkj asdfjlkasdj lfkajsd ljfkalkjas dj
sad flkjaslkfienvoiwanvoasvonon  sdan vn ovon von eaon awonv on v nowaein
sald flavne

asld flkasjdfl kaslk flkasj dflkajsflaksdjf

asdfl kjasl kveln alvaielnalkasfnals lfnvin neniviennievnievninievsa,sdn las
asdlk vonenasdin go oxzihvejnvoai shf vnje naon vjln aadve
        """
        basis = basis * (size // len(basis) + 1)
        return cls(start, basis[:size])

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.text)

    def __getitem__(self, slice_):
        if slice_.start is None and self.start < slice_.stop <= self.stop:
            return type(self)(
                self.start, self.text[:slice_.stop - self.start])
        elif self.start <= slice_.start < self.stop and slice_.stop is None:
            return type(self)(
                slice_.start, self.text[slice_.start - self. start:])
        else:
            raise IndexError((
                "Unsupported slice operation. "
                "Start: {}, stop: {}, slice: {!r}").format(
                    self.start, self.stop, slice_))
