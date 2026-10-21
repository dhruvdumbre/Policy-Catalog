import sqlite3
from pathlib import Path

# Storing the database beside this file.
DB_PATH = Path(__file__).resolve().parent / "policy_catalog.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    connection = get_connection()
    
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS policy_types(
                policy_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL
                    CHECK(category IN(
                        'Motor', 'Health','Life','Travel','Home','Other'
                    )),
                min_premium REAL NOT NULL
                    CHECK(min_premium > 0),
                max_premium REAL NOT NULL
                    CHECK(max_premium > min_premium),
                coverage_amount REAL NOT NULL
                    CHECK(coverage_amount > 0),
                UNIQUE(name, category)
            )               
        """)
        
        connection.commit()
        print("Database Initialized Successfully.")
        
    finally:
        connection.close()
        
if __name__ == "__main__":
    initialize_database()
   
def create_policy(name, category, min_premium, max_premium, coverage_amount):
    connection = get_connection()
    
    try:
        cursor = connection.execute(
            """
            INSERT INTO policy_types
                (name, category, min_premium, max_premium, coverage_amount)
            VALUES(?, ?, ?, ?, ?)
            """,
            (name, category, min_premium, max_premium, coverage_amount)
        ) 
        connection.commit()
        
        return cursor.lastrowid
    
    except sqlite3.IntegrityError as error:
        connection.rollback()
        
        if "UNIQUE constraint failed" in str(error):
            raise ValueError(
                "A policy with this name already exists in this category."
            )from error
            
        raise ValueError(
            "The database rejected the policy. Check the entered value."
        )from error
        
    finally:
        connection.close()
        
def get_all_policies():
    connection = get_connection()
    
    try:
        cursor = connection.execute("""
            SELECT policy_type_id, name, category, min_premium, max_premium, coverage_amount
            FROM policy_types
            ORDER BY policy_type_id                                
        """)
        
        return cursor.fetchall()
    
    finally:
        connection.close()
    
def get_policies_by_category(category):
    
    connection = get_connection()
    
    try:
        cursor = connection.execute("""
            SELECT policy_type_id, name, category, min_premium, max_premium, coverage_amount
            FROM policy_types
            WHERE category = ?
            ORDER BY policy_type_id
        """, 
        (category,))
        
        return cursor.fetchall()
    
    finally:
        connection.close()
        
def get_policy_by_id(policy_id):
    
    connection = get_connection()
    
    try:
        cursor = connection.execute(
            """
                SELECT policy_type_id, name, category, min_premium, max_premium, coverage_amount
                FROM policy_types
                WHERE policy_type_id = ?
                """,
                (policy_id,)
        )
        return cursor.fetchone()
    
    finally:
        connection.close()
        
def update_policy(policy_id, name, category, min_premium, max_premium, coverage_amount):
    
    connection = get_connection()
    
    try:
        cursor = connection.execute(
            """
            UPDATE policy_types
            SET name = ?,
                category = ?,
                min_premium = ?,
                max_premium = ?,
                coverage_amount = ?
            WHERE policy_type_id = ?
            """,
            (
                name, category, min_premium, max_premium, coverage_amount, policy_id
            )
        )
        
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError as error:
        raise ValueError(
            "Another policy with this name already exists "
            "in this category."
        ) from error
    
    finally:
        connection.close()
        
def delete_policy(policy_id):
    
    connection = get_connection()
    
    try:
        cursor = connection.execute(
            """
            DELETE FROM policy_types
            WHERE policy_type_id = ?
            """,
            (policy_id,)
        )
        
        connection.commit()
        
        return cursor.rowcount > 0
    
    finally:
        connection.close()