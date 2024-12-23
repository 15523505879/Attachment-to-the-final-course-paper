from SimpleDB import SimpleDB
import random

db = SimpleDB("plannertest")
tx = db.newTx()
planner = db.planner()
cmd = "create table T1(A int, B varchar(9))"
planner.executeUpdate(cmd, tx)
n = 5
print("Inserting", n, "random records")
for i in range(n):
    a = random.randint(0, 50)
    b = "rec" + str(a)
    cmd = "insert into T1(A,B) values(" + str(a) + ", '" + b + "')"
    planner.executeUpdate(cmd, tx)
print("插入结束")
qry = "select A, B from T1 where A=20"
# :p ProjectPlan
p = planner.createQueryPlan(qry, tx)
s = p.open()
while s.next():
    print(s.getInt("A"), s.getString("B"))
s.close()
tx.commit()

