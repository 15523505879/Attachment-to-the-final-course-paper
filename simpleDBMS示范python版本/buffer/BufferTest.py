from FileMgr import FileMgr
from BlockID import BlockID
from LogMgr import LogMgr
from BufferMgr import BufferMgr


if __name__ == "__main__":
    fm = FileMgr("buffertest", 400)
    lm = LogMgr(fm, "simpledb.log")
    bm = BufferMgr(fm, lm, 3)
    buff1 = bm.pin(BlockID("testfile", 1))
    p = buff1.contents()
    n = p.getInt(80)
    p.setInt(80, n + 1)
    buff1.setModified(1, 0)
    print("The new value is: ", (n + 1))
    # 这里缓冲池中的第一个缓冲区中的block仍然为blk1
    bm.unpin(buff1)
    # 这里找不到block为2的缓冲区，调用assignToBlock把对块blk1的修改保存到磁盘中，更改缓冲池中第一个缓冲区的block为blk2，
    buff2 = bm.pin(BlockID("testfile", 2))
    # buff3 = bm.pin(BlockID("testfile", 3))
    # buff4 = bm.pin(BlockID("testfile", 4))
    bm.unpin(buff2)
    buff2 = bm.pin(BlockID("testfile", 1))
    p2 = buff2.contents()
    p2.setInt(80, 9999)
    buff2.setModified(1, 0)
