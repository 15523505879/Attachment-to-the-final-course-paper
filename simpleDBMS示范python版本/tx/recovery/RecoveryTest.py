from Transaction import Transaction
from FileMgr import FileMgr
from LogMgr import LogMgr
from BufferMgr import BufferMgr
from BlockID import BlockID
from Page import Page


def printValues(msg):
    print(msg)
    p0 = Page(fm.blockSize())
    p1 = Page(fm.blockSize())
    fm.read(blk0, p0)
    fm.read(blk1, p1)
    pos = 0
    for i in range(6):
        print(p0.getInt(pos), end=" ")
        print(p1.getInt(pos), end=" ")
        pos += 4
    print(p0.getString(30), end=" ")
    print(p1.getString(30), end=" ")
    print("\n")


def init():
    tx1 = Transaction(fm, lm, bm)
    tx2 = Transaction(fm, lm, bm)
    tx1.pin(blk0)
    tx2.pin(blk1)
    pos = 0
    for i in range(6):
        tx1.setInt(blk0, pos, pos, False)
        tx2.setInt(blk1, pos, pos, False)
        pos += 4
    tx1.setString(blk0, 30, "abc", False)
    tx2.setString(blk1, 30, "def", False)
    tx1.commit()
    tx2.commit()
    printValues("After Init")


def modify():
    tx3 = Transaction(fm, lm, bm)
    tx4 = Transaction(fm, lm, bm)
    tx3.pin(blk0)
    tx4.pin(blk1)
    pos = 0
    for i in range(6):
        tx3.setInt(blk0, pos, pos + 100, True)
        tx4.setInt(blk1, pos, pos + 100, True)
        pos += 4
    tx3.setString(blk0, 30, "uvw", True)
    tx4.setString(blk1, 30, "xyz", True)
    bm.flushAll(3)
    bm.flushAll(4)
    printValues("After modification")
    tx3.rollback()
    printValues("After rollback")


def recover():
    tx = Transaction(fm, lm, bm)
    tx.recover()
    printValues("After recovery")


if __name__ == "__main__":
    fm = FileMgr("recoveryTest", 400)
    lm = LogMgr(fm, "simpledb.log")
    bm = BufferMgr(fm, lm, 8)
    blk0 = BlockID("testfile", 0)
    blk1 = BlockID("testfile", 1)
    if fm.length("testfile") == 0:
        init()
        modify()
    else:
        recover()
