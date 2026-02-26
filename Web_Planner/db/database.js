import mysql from "mysql2/promise";
import dotenv from "dotenv";

dotenv.config();

// Create MySQL pool
const pool = mysql.createPool({
    host: process.env.MYSQL_HOST,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PASSWORD,
    database: process.env.MYSQL_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Verify connection on startup
async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log("✅ Database Connected Successfully");
        connection.release();
    } catch (error) {
        console.error("❌ Database Connection Failed:", error);
        process.exit(1);
    }
}

testConnection();

export default pool;
