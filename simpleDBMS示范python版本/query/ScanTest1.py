from SimpleDB import SimpleDB
from Schema import Schema
from Layout import Layout
from TableScan import TableScan
from Constant import Constant
from Term import Term
from Expression import Expression
from SelectScan import SelectScan
from Predicate import Predicate
from ProjectScan import ProjectScan
import random

db = SimpleDB("scantest1")
tx = db.newTx()

sch1 = Schema()
sch1.addIntField("A")
sch1.addStringField("B", 9)
layout = Layout(sch1)
s1 = TableScan(tx, "T", layout)

s1.beforeFirst()
n = 100
print("Inserting " + str(n) + " random records.")
for i in range(n):
    s1.insert()
    k = random.randint(0, 50)
    s1.setInt("A", k)
    s1.setString("B", "rec" + str(k))
s1.close()

s2 = TableScan(tx, "T", layout)
# 查找所有A=10的记录
c = Constant(10)
t = Term(Expression("A"), Expression(c))
pred = Predicate(t)
print("The predicate is ", pred)
s3 = SelectScan(s2, pred)
fields = ["B"]
s4 = ProjectScan(s3, fields)
print("获取B")
while s4.next():
    print(s4.getString("B"))
s4.close()
tx.commit()