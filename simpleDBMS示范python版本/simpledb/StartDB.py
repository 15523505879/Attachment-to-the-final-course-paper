from EmbeddedDriver import EmbeddedDriver
from EmbeddedStatement import EmbeddedStatement
from EmbeddedMetaData import EmbeddedMetaData
from EmbeddedResultSet import EmbeddedResultSet
from sqlite3 import Error


def doQuery(stmt: EmbeddedStatement, cmd):
    try:
        rs: EmbeddedResultSet = stmt.executeQuery(cmd)
        md: EmbeddedMetaData = rs.getMetaData()
        numcols = md.getColumnCount()
        totalwidth = 0

        for i in range(1, numcols + 1):
            fldname = md.getColumnName(i)
            width = md.getColumnDisplaySize(i)
            totalwidth += width
            fmt = "%" + str(width) + "s"
            print(fmt % fldname, end="")
        print()
        for i in range(totalwidth):
            print("-", end="")
        print()

        while rs.next():
            for i in range(1, numcols + 1):
                fldname = md.getColumnName(i)
                fldtype = md.getColumnType(i)
                fmt = "%" + str(md.getColumnDisplaySize(i))
                if fldtype == 4:
                    ival = rs.getInt(fldname)
                    print((fmt + "d") % ival, end="")
                else:
                    sval = rs.getString(fldname)
                    print((fmt + "s") % sval, end="")
            print()
        for i in range(totalwidth):
            print("-", end="")
        print()
        # else:
        #     tableList = stmt.executeQuery(cmd)
        #     tableList.remove("tbl cat")
        #     tableList.remove("fld cat")
        #     tableList.remove("view cat")
        #     print("Tables in " + dbname)
        #     print("----------")
        #     for i in tableList:
        #         print(i)
        #     print("----------")
    except Error as e:
        print("SQL Exception:", e)


def doUpdate(stmt: EmbeddedStatement, cmd: str):
    try:
        howmany = stmt.executeUpdate(cmd)
        print(howmany, "records processed")
    except Error as e:
        print("SQL Exception:", e)


def printHelp():
    f = open("help.txt", 'r', encoding='utf-8')
    print(f.read())


if __name__ == "__main__":
    dbname = "test"
    driver = EmbeddedDriver()
    try:
        conn = driver.connect(dbname)
        stmt = conn.createStatement()
        print("输入 -help- 查看帮助")
        while True:
            cmd = input("SQL> ")
            if cmd.startswith("exit"):
                break
            elif cmd == "-help-":
                printHelp()
            elif cmd.startswith("select"):
                doQuery(stmt, cmd)
            else:
                doUpdate(stmt, cmd)
    except Error as e:
        print("SQL Exception:", e)









