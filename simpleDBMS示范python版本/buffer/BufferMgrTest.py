from FileMgr import FileMgr
from BlockID import BlockID
from LogMgr import LogMgr
from BufferMgr import BufferMgr
from BufferAbortException import BufferAbortException
from Buffer import Buffer

fm = FileMgr("buffertest", 400)
lm = LogMgr(fm, "simpledb.log")
bm = BufferMgr(fm, lm, 3)
buff = [Buffer(fm, lm)] * 6
buff[0] = bm.pin(BlockID("testfile", 0))
buff[1] = bm.pin(BlockID("testfile", 1))
buff[2] = bm.pin(BlockID("testfile", 2))
bm.unpin(buff[1])
buff[1] = None
buff[3] = bm.pin(BlockID("testfile", 0))
buff[4] = bm.pin(BlockID("testfile", 1))
print("Available buffers:", bm.available())
try:
    print("Attempting to pin block 3...")
    buff[5] = bm.pin(BlockID("testfile", 3))  # 没有可用的缓冲区
except BufferAbortException as e:
    print("Exception: No available buffers\n")
bm.unpin(buff[2])
buff[2] = None
buff[5] = bm.pin(BlockID("testfile", 3))    # 有可用的缓冲区
print("Final Buffer Allocation:")
for i in range(len(buff)):
    b = buff[i]
    if b is not None:
        print(f"buff[{str(i)}] pinned to block {b.block()}")
