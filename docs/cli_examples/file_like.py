

from fakelargefile import FakeLargeFile, RepeatingSegment


flf = FakeLargeFile()
flf.append(RepeatingSegment(start=0, stop="10G", string="spam "))
flf.seek(9990000000)
flf.read(10)
