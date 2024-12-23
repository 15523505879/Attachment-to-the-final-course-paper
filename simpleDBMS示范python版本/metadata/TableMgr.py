from Transaction import Transaction
from Layout import Layout
from Schema import Schema
from TableScan import TableScan


class TableMgr:
    """表管理器

    用于创建表、将元数据保存到目录并获取先前创建表的元数据。

    Attributes:
        MAX_NAME: 表名或字段名的最大长度。
        __tcatLayout: 记录表名和表中槽的大小。
        __fcatLayout: 记录表中字段的详细信息。
    """

    MAX_NAME = 16

    def __init__(self, isNew: bool, tx: Transaction):
        tcatSchema = Schema()
        tcatSchema.addStringField("tblname", self.MAX_NAME)
        tcatSchema.addIntField("slotsize")
        self.__tcatLayout = Layout(tcatSchema)

        fcatSchema = Schema()
        fcatSchema.addStringField("tblname", self.MAX_NAME)
        fcatSchema.addStringField("fldname", self.MAX_NAME)
        fcatSchema.addIntField("type")
        fcatSchema.addIntField("length")
        fcatSchema.addIntField("offset")
        self.__fcatLayout = Layout(fcatSchema)

        if isNew:
            self.createTable("tblcat", tcatSchema, tx)
            self.createTable("fldcat", fcatSchema, tx)

    def createTable(self, tblname: str, sch: Schema, tx: Transaction):
        """创建一个具有指定名称和模式的新表

        Args:
            :param tblname: 新表的名称
            :param sch: 表的模式
            :param tx: 创建表的事务
        """
        layout = Layout(sch)
        # 向tblcat插入一条记录
        tcat = TableScan(tx, "tblcat", self.__tcatLayout)
        tcat.insert()
        tcat.setString("tblname", tblname)
        tcat.setInt("slotsize", layout.slotSize())
        tcat.close()
        # 为每个字段向fldcat插入一条记录
        fcat = TableScan(tx, "fldcat", self.__fcatLayout)
        for fldname in sch.fields():
            fcat.insert()
            fcat.setString("tblname", tblname)
            fcat.setString("fldname", fldname)
            fcat.setInt("type", sch.type(fldname))
            fcat.setInt("length", sch.length(fldname))
            fcat.setInt("offset", layout.offset(fldname))
        fcat.close()

    def getLayout(self, tblname: str, tx: Transaction) -> Layout:
        """从目录检索指定表的布局

        Args:
            :param tblname: 表的名称
            :param tx: 事务

        Returns:
            :return 表的元数据
        """
        size = -1
        tcat = TableScan(tx, "tblcat", self.__tcatLayout)
        while tcat.next():
            if tcat.getString("tblname") == tblname:
                size = tcat.getInt("slotsize")
                break
        tcat.close()

        sch = Schema()
        offsets = {}
        fcat = TableScan(tx, "fldcat", self.__fcatLayout)
        while fcat.next():
            if fcat.getString("tblname") == tblname:
                fldname = fcat.getString("fldname")
                fldtype = fcat.getInt("type")
                fldlen = fcat.getInt("length")
                offset = fcat.getInt("offset")
                offsets[fldname] = offset
                sch.addField(fldname, fldtype, fldlen)
        fcat.close()
        return Layout(sch, offsets, size)

    # # 获取数据库中的表名
    # def getTableNames(self, tx):
    #     tableNames = []
    #     tcat = TableScan(tx, "tblcat", self.__tcatLayout)
    #     while tcat.next():
    #         tableNames.append(tcat.getString("tblname"))
    #     return tableNames

