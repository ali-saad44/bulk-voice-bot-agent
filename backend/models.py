import sqlite3
import os
from datetime import datetime
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Campaigns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            total_numbers INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Calls table - tracks each number's status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            phone_number TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            twilio_sid TEXT,
            duration INTEGER DEFAULT 0,
            answered_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    
    # Call status values: pending, initiated, ringing, answered, no-answer, busy, failed, voicemail, completed
    
    conn.commit()
    conn.close()

def create_campaign(name, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO campaigns (name, message) VALUES (?, ?)',
        (name, message)
    )
    campaign_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

def add_call(campaign_id, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO calls (campaign_id, phone_number) VALUES (?, ?)',
        (campaign_id, phone_number)
    )
    call_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return call_id

def update_call_status(call_id, status, twilio_sid=None, duration=None, error_message=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = ['status = ?']
    params = [status]
    
    if twilio_sid:
        updates.append('twilio_sid = ?')
        params.append(twilio_sid)
    if duration is not None:
        updates.append('duration = ?')
        params.append(duration)
    if error_message:
        updates.append('error_message = ?')
        params.append(error_message)
    if status in ['answered', 'completed']:
        updates.append('answered_at = CURRENT_TIMESTAMP')
    if status in ['completed', 'failed', 'no-answer', 'busy']:
        updates.append('completed_at = CURRENT_TIMESTAMP')
    
    params.append(call_id)
    
    query = f"UPDATE calls SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_campaign_stats(campaign_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'answered' THEN 1 ELSE 0 END) as answered,
            SUM(CASE WHEN status = 'no-answer' THEN 1 ELSE 0 END) as no_answer,
            SUM(CASE WHEN status = 'busy' THEN 1 ELSE 0 END) as busy,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'voicemail' THEN 1 ELSE 0 END) as voicemail,
            SUM(CASE WHEN status IN ('pending', 'initiated', 'ringing') THEN 1 ELSE 0 END) as pending
        FROM calls WHERE campaign_id = ?
    ''', (campaign_id,))
    
    stats = dict(cursor.fetchone())
    conn.close()
    return stats

def get_campaign_calls(campaign_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM calls WHERE campaign_id = ? ORDER BY id',
        (campaign_id,)
    )
    calls = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return calls

def update_campaign_status(campaign_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE campaigns SET status = ? WHERE id = ?',
        (status, campaign_id)
    )
    conn.commit()
    conn.close()

def get_all_campaigns():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
    campaigns = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return campaigns