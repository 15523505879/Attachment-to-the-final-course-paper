from SimpleDB import SimpleDB
from TableMgr import TableMgr
from Schema import Schema


db = SimpleDB("tblmgrtest", 400, 8)
tx = db.newTx()
tm = TableMgr(True, tx)
sch = Schema()
sch.addIntField("A")
sch.addStringField("B", 9)
tm.createTable("Mytable", sch, tx)

layout = tm.getLayout("Mytable", tx)
size = layout.slotSize()
sch2 = layout.schema()
print("MyTable has slot size ", size)
print("Its fields are:")
for fldname in sch2.fields():
    Thetype = None
    if sch2.type(fldname) == 4:
        Thetype = "int"
    else:
        flLen = sch2.length(fldname)
        Thetype = "varchar(" + str(flLen) + ")"
    print(fldname, ":", Thetype)
tx.commit()