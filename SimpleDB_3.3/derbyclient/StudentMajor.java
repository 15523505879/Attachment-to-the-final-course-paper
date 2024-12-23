import java.sql.*;
import org.apache.derby.jdbc.ClientDriver;

public class StudentMajor {
   public static void main(String[] args) {
      String url = "jdbc:derby://localhost:1527/studentdb;create=true"; // 自动创建数据库
      try {
         Class.forName("org.apache.derby.jdbc.ClientDriver");
         try (Connection conn = DriverManager.getConnection(url)) {
            System.out.println("Connected to the database.");
            // 继续执行创建表、插入数据等操作...
         }
      } catch (ClassNotFoundException e) {
         System.err.println("Derby Client Driver not found.");
         e.printStackTrace();
      } catch (SQLException e) {
         System.err.println("SQL Exception occurred.");
         e.printStackTrace();
      }
   }

   
   private static void printSchema(ResultSet rs) throws SQLException {
      System.out.println("\nHere is the schema:");
      ResultSetMetaData md = rs.getMetaData();
      for(int i=1; i<=md.getColumnCount(); i++) {
         String name  = md.getColumnName(i);
         int size     = md.getColumnDisplaySize(i);
         int typecode = md.getColumnType(i);
         String type;
         if (typecode == Types.INTEGER)
            type = "int";
         else if (typecode == Types.VARCHAR)
            type = "string";
         else
            type = "other";
         System.out.println("  " + name + "\t" + type + "\t" + size);
      }
   }
}
