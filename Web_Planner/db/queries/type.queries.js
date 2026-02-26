import pool from "../database.js";

// Create a new event type
export async function createTypeInDb(name, importance, color) {
    const [result] = await pool.query(
        `INSERT INTO type (name, importance, color)
         VALUES (?, ?, ?)`,
        [name, importance, color]
    );

    const [rows] = await pool.query(`SELECT * FROM type WHERE id = ?`, [result.insertId]);
    return rows[0];
}

// Get all types
export async function getTypesFromDb() {
    const [rows] = await pool.query(`SELECT * FROM type`);
    return rows;
}
