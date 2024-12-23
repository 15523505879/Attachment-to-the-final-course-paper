from SimpleDB import SimpleDB
from MetadataMgr import MetadataMgr
from Schema import Schema
from TableScan import TableScan


db = SimpleDB("metadatamgrtest", 400, 8)
tx = db.newTx()
mdm = MetadataMgr(True, tx)

sch = Schema()
sch.addIntField("A")
sch.addStringField("B", 9)

mdm.createTable("MyTable", sch, tx)
layout = mdm.getLayout("MyTable", tx)
size = layout.slotSize()
sch2 = layout.schema()
print("MyTable has slot size", size)
print("Its fields are:")
for fldname in sch2.fields():
    type_str = "int" if sch2.type(fldname) == 4 else f"varchar({sch2.length(fldname)})"
    print(f"{fldname}: {type_str}")

ts = TableScan(tx, "MyTable", layout)
for i in range(50):
    ts.insert()
    n = round(i * 50)
    ts.setInt("A", n)
    ts.setString("B", f"rec{n}")
si = mdm.getStatInfo("MyTable", layout, tx)
print("B(MyTable) =", si.blocksAccessed())
print("R(MyTable) =", si.recordsOutput())
print("V(MyTable,A) =", si.distinctValues())
print("V(MyTable,B) =", si.distinctValues())

viewdef = "select B from MyTable where A = 1"
mdm.createView("viewA", viewdef, tx)
v = mdm.getViewDef("viewA", tx)
print("View def =", v)

mdm.createIndex("indexA", "MyTable", "A", tx)
mdm.createIndex("indexB", "MyTable", "B", tx)
idxmap = mdm.getIndexInfo("MyTable", tx)

ii = idxmap["A"]
print("B(indexA) =", ii.blocksAccessed())
print("R(indexA) =", ii.recordsOutput())
print("V(indexA,A) =", ii.distinctValues("A"))
print("V(indexA,B) =", ii.distinctValues("B"))

ii = idxmap["B"]
print("B(indexB) =", ii.blocksAccessed())
print("R(indexB) =", ii.recordsOutput())
print("V(indexB,A) =", ii.distinctValues("A"))
print("V(indexB,B) =", ii.distinctValues("B"))

tx.commit()
