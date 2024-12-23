from SimpleDB import SimpleDB
from Schema import Schema
from Layout import Layout
from TableScan import TableScan
from Term import Term
from Expression import Expression
from SelectScan import SelectScan
from Predicate import Predicate
from ProjectScan import ProjectScan
from ProductScan import ProductScan


db = SimpleDB("scantest2")
tx = db.newTx()

sch1 = Schema()
sch1.addIntField("A")
sch1.addStringField("B", 9)
layout1 = Layout(sch1)
us1 = TableScan(tx, "T1", layout1)
us1.beforeFirst()
n = 5
print("Inserting " + str(n) + " records into T1.")
for i in range(n):
    us1.insert()
    us1.setInt("A", i)
    us1.setString("B", "bbb" + str(i))
us1.close()

sch2 = Schema()
sch2.addIntField("C")
sch2.addStringField("D", 9)
layout2 = Layout(sch2)
us2 = TableScan(tx, "T2", layout2)
us2.beforeFirst()
print("Inserting " + str(n) + " records into T2.")
for i in range(n):
    us2.insert()
    us2.setInt("C", n - i - 1)
    us2.setString("D", "ddd" + str(n - i - 1))
us2.close()

s1 = TableScan(tx, "T1", layout1)
s2 = TableScan(tx, "T2", layout2)
s3 = ProductScan(s1, s2)
# 选择所有A=C的记录
t = Term(Expression("A"), Expression("C"))
pred = Predicate(t)
print("The predicate is ", pred)
s4 = SelectScan(s3, pred)

# projecting on [B,D]
c = ["B", "D"]
s5 = ProjectScan(s4, c)
while s5.next():
    print(s5.getString("B") + " " + s5.getString("D"))
s5.close()
tx.commit()