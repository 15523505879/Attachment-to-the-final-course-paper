from FileMgr import FileMgr
from LogMgr import LogMgr
from BufferMgr import BufferMgr
from Transaction import Transaction
from BlockID import BlockID



fm = FileMgr("txTest", 400)
lm = LogMgr(fm, "simpledb.log")
bm = BufferMgr(fm, lm, 8)

tx1 = Transaction(fm, lm, bm)
blk = BlockID("testfile", 1)
tx1.pin(blk)
tx1.setInt(blk, 80, 1, False)
tx1.setString(blk, 40, "one", False)
tx1.commit()

tx2 = Transaction(fm, lm, bm)
tx2.pin(blk)
ival = tx2.getInt(blk, 80)
sval = tx2.getString(blk, 40)
print("initial value at location 80 = ", ival)
print("initial value at location 40 = " + sval)
newIval = ival + 1
newSval = sval + "!"
tx2.setInt(blk, 80, newIval, True)
tx2.setString(blk, 40, newSval, True)
tx2.commit()

tx3 = Transaction(fm, lm, bm)
tx3.pin(blk)
print("new value at location 80 = ", tx3.getInt(blk, 80))
print("new value at location 40 = ", tx3.getString(blk, 40))
tx3.setInt(blk, 80, 9999, True)
print("pre-rollback value at location 80 = ", tx3.getInt(blk, 80))
tx3.rollback()

tx4 = Transaction(fm, lm, bm)
tx4.pin(blk)
print("post-rollback at location 80 = ", tx4.getInt(blk, 80))
tx4.commit()
