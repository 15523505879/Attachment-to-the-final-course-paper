from Page import Page
from FileMgr import FileMgr
from LogMgr import LogMgr


# 输出日志文件中的日志记录
def printLogRecords(msg):
    print(msg)
    iter = lm.iterator()
    while iter.hasNext():
        rec = iter.next()
        p = Page(rec)
        s = p.getString(0)
        npos = Page.maxLength(len(s))
        val = p.getInt(npos)
        print("[" + s + ", " + str(val) + "]")


# 创建日志记录
def createLogRecord(s, n):
    spos = 0
    # 存储s后的位置
    npos = spos + Page.maxLength(len(s))
    b = bytes(npos + 4)
    p = Page(b)
    p.setString(spos, s)
    p.setInt(npos, n)
    b = bytes(p.contents())
    return b


if __name__ == "__main__":
    # 创建logtest目录
    fm = FileMgr("logtest", 400)
    lm = LogMgr(fm, "simpledb.log")
    print("The initial empty log file:")
    iter = lm.iterator()
    while iter.hasNext():
        rec = iter.next()
        p = Page(rec)
        s = p.getString(0)
        npos = Page.maxLength(len(s))
        val = p.getInt(npos)
        print("[" + s + ", " + str(val) + "]")
    print("done")
    print("Creating records: ")
    for i in range(1, 36):
        record_str = "record" + str(i)
        rec = createLogRecord(record_str, 100 + i)
        lsn = lm.append(rec)
        print(lsn, " ")
    printLogRecords("The log file now has these records:")