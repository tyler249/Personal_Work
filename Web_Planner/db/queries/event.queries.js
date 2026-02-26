import pool from "../database.js";

// Create a new event
export async function createEventInDb(name, description, date, time, userId, typeId) {
    const [result] = await pool.query(
        `INSERT INTO event (name, description, date, time, user_id, type_id)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [name, description, date, time, userId, typeId]
    );

    const [rows] = await pool.query(`SELECT * FROM event WHERE id = ?`, [result.insertId]);
    return rows[0];
}

// Get events for a user on a specific date
export async function getUserEventsFromDb(userId, date) {
    const [rows] = await pool.query(
        `SELECT event.id, event.name, event.description, event.time, type.importance, type.color
         FROM event
         JOIN type ON event.type_id = type.id
         WHERE event.user_id = ? AND event.date = ?
         ORDER BY event.time ASC`,
        [userId, date]
    );

    return rows;
}
