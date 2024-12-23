import random
from SimpleDB import SimpleDB
from Layout import Layout
from Schema import Schema
from RecordPage import RecordPage


db = SimpleDB("recordtest", 400, 8)
tx = db.newTx()
sch = Schema()
sch.addIntField("A")
sch.addStringField("B", 9)
layout = Layout(sch)
for fldname in layout.schema().fields():
    offset = layout.offset(fldname)
    print(fldname, "has offset ", offset)
blk = tx.append("testfile")
tx.pin(blk)
rp = RecordPage(tx, blk, layout)
rp.format()
print("Filling the page with random records.")
slot = rp.insertAfter(-1)
while slot >= 0:
    n = random.randint(0, 50)
    rp.setInt(slot, "A", n)
    rp.setString(slot, "B", "rec" + str(n))
    print("inserting into slot", slot, ": {", n, ",", "rec" + str(n) + " }")
    slot = rp.insertAfter(slot)
print("Deleting these records, whose A-values are less than 25.")
count = 0
slot = rp.nextAfter(-1)
while slot >= 0:
    a = rp.getInt(slot, "A")
    b = rp.getString(slot, "B")
    if a < 25:
        count += 1
        print("slot ", slot, ": {", a, ", " + b + " }")
        rp.delete(slot)
    slot = rp.nextAfter(slot)
print(count, "values under 25 were deleted.")
print("Here are the remaining records.")
slot = rp.nextAfter(-1)
while slot >= 0:
    a = rp.getInt(slot, "A")
    b = rp.getString(slot, "B")
    print("slot", slot, ": {", a, ", " + b + " }")
    slot = rp.nextAfter(slot)
tx.unpin(blk)
tx.commit()
