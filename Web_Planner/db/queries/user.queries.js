import pool from "../database.js";

// Find user by username
export async function getUserByUserName(userName) {
    const [rows] = await pool.query(`SELECT * FROM user WHERE userName = ?`, [userName]);
    return rows[0];
}

// Find user by ID
export async function getUserById(id) {
    const [rows] = await pool.query(`SELECT * FROM user WHERE id = ?`, [id]);
    return rows[0];
}

// Create a new user
export async function createUserInDb(userName, email, password) {
    const [result] = await pool.query(
        `INSERT INTO user (userName, email, password) VALUES (?, ?, ?)`,
        [userName, email, password]
    );
    return getUserById(result.insertId);
}
