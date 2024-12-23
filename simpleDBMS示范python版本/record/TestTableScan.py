import random
from SimpleDB import SimpleDB
from Schema import Schema
from Layout import Layout
from TableScan import TableScan


db = SimpleDB("tabletest", 400, 8)
tx = db.newTx()
sch = Schema()
sch.addIntField("A")
sch.addStringField("B", 9)
layout = Layout(sch)
for fldname in layout.schema().fields():
    offset = layout.offset(fldname)
    print(fldname, "has offset", offset)
print("Filling the table with 50 random records.")
ts = TableScan(tx, "T", layout)
for i in range(50):
    ts.insert()
    n = random.randint(0, 50)
    ts.setInt("A", n)
    ts.setString("B", "rec" + str(n))
    print("inserting into slot ", ts.getRid(), ": {" + str(n) + ", " + "rec" + str(n) + " }")
print("Deleting these records, whose A-values are less than 25.")
count = 0
ts.beforeFirst()
while ts.next():
    a = ts.getInt("A")
    b = ts.getString("B")
    if a < 25:
        count += 1
        print("slot ", ts.getRid(), ": {", a, ",", b + "}")
        ts.delete()
print(count, "values under 25 were deleted.")
print("Here are the remaining records.")
ts.beforeFirst()
while ts.next():
    a = ts.getInt("A")
    b = ts.getString("B")
    print("slot ", ts.getRid(), ": {", a, ",", b + "}")
ts.close()
tx.commit()