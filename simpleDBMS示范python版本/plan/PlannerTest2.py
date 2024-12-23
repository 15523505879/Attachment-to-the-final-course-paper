from SimpleDB import SimpleDB


db = SimpleDB("plannertest2")
tx = db.newTx()
planner = db.planner()
cmd = "create table T1 (A int, B varchar(9))"
planner.executeUpdate(cmd, tx)
n = 100
print("Inserting " + str(n) + " records into T1.")
for i in range(n):
    a = i
    b = "bbb" + str(a)
    cmd = "insert into T1 (A, B) values(" + str(a) + ", '" + b + "')"
    planner.executeUpdate(cmd, tx)

cmd = "create table T2 (C int, D varchar(9))"
planner.executeUpdate(cmd, tx)
print("Inserting " + str(n) + " records into T2.")
for i in range(n):
    c = n - i - 1
    d = "ddd" + str(c)
    cmd = "insert into T2 (C,D) values(" + str(c) + ", '" + d + "')"
    planner.executeUpdate(cmd, tx)

qry = "select B,D from T1,T2 where A=C"
p = planner.createQueryPlan(qry, tx)
s = p.open()
while s.next():
    print(s.getString("B") + " " + s.getString("D"))
s.close()
tx.commit()

