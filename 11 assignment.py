# -*- coding: utf-8 -*-
import psycopg2
import csv
import os

DB_CONFIG = {
    'host': 'localhost',
    'database': 'asdasd',
    'user': 'postgres',
    'password': 'beastBread1',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS phonebook (
                                                            id SERIAL PRIMARY KEY,
                                                            username VARCHAR(100) UNIQUE NOT NULL,
                       first_name VARCHAR(100) NOT NULL,
                       last_name VARCHAR(100),
                       phone VARCHAR(20) UNIQUE NOT NULL,
                       email VARCHAR(100),
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )
                   ''')

    conn.commit()
    cursor.close()
    conn.close()

def init_functions_and_procedures():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE OR REPLACE FUNCTION search_by_pattern(pattern TEXT)
        RETURNS TABLE(
            id INTEGER,
            username VARCHAR,
            first_name VARCHAR,
            last_name VARCHAR,
            phone VARCHAR,
            email VARCHAR,
            created_at TIMESTAMP
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT phonebook.id, phonebook.username, phonebook.first_name, 
                   phonebook.last_name, phonebook.phone, phonebook.email, 
                   phonebook.created_at
            FROM phonebook
            WHERE phonebook.username ILIKE '%' || pattern || '%'
               OR phonebook.first_name ILIKE '%' || pattern || '%'
               OR phonebook.last_name ILIKE '%' || pattern || '%'
               OR phonebook.phone ILIKE '%' || pattern || '%'
            ORDER BY phonebook.username;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    cursor.execute('''
        CREATE OR REPLACE FUNCTION insert_or_update_user(
            p_username VARCHAR,
            p_first_name VARCHAR,
            p_phone VARCHAR
        )
        RETURNS VOID AS $$
        BEGIN
            IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_username) THEN
                UPDATE phonebook 
                SET phone = p_phone, first_name = p_first_name
                WHERE username = p_username;
            ELSE
                INSERT INTO phonebook (username, first_name, phone)
                VALUES (p_username, p_first_name, p_phone);
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    cursor.execute('''
        DROP TYPE IF EXISTS incorrect_phone_data CASCADE;
        CREATE TYPE incorrect_phone_data AS (
            username VARCHAR,
            phone VARCHAR,
            reason TEXT
        );
    ''')

    cursor.execute('''
        CREATE OR REPLACE FUNCTION insert_many_users(
            users_data TEXT[][]
        )
        RETURNS TABLE(
            username VARCHAR,
            phone VARCHAR,
            reason TEXT
        ) AS $$
        DECLARE
            user_record TEXT[];
            phone_valid BOOLEAN;
            incorrect_records incorrect_phone_data[];
            i INTEGER;
        BEGIN
            incorrect_records := ARRAY[]::incorrect_phone_data[];
            
            FOR i IN 1..array_length(users_data, 1) LOOP
                user_record := users_data[i];
                
                phone_valid := user_record[2] ~ '^[\d\+\-\(\)\s]+$' 
                                AND length(replace(replace(replace(user_record[2], '+', ''), '-', ''), ' ', '')) >= 7;
                
                IF phone_valid THEN
                    BEGIN
                        IF EXISTS (SELECT 1 FROM phonebook WHERE username = user_record[1]) THEN
                            UPDATE phonebook 
                            SET phone = user_record[2], first_name = COALESCE(user_record[3], user_record[1])
                            WHERE username = user_record[1];
                        ELSE
                            INSERT INTO phonebook (username, first_name, phone)
                            VALUES (user_record[1], COALESCE(user_record[3], user_record[1]), user_record[2]);
                        END IF;
                    EXCEPTION WHEN OTHERS THEN
                        incorrect_records := array_append(incorrect_records, 
                            ROW(user_record[1], user_record[2], 'Database error: ' || SQLERRM)::incorrect_phone_data);
                    END;
                ELSE
                    incorrect_records := array_append(incorrect_records, 
                        ROW(user_record[1], user_record[2], 'Invalid phone format')::incorrect_phone_data);
                END IF;
            END LOOP;
            
            FOR i IN 1..array_length(incorrect_records, 1) LOOP
                username := incorrect_records[i].username;
                phone := incorrect_records[i].phone;
                reason := incorrect_records[i].reason;
                RETURN NEXT;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    cursor.execute('''
        CREATE OR REPLACE FUNCTION get_contacts_paginated(
            p_limit INTEGER,
            p_offset INTEGER
        )
        RETURNS TABLE(
            id INTEGER,
            username VARCHAR,
            first_name VARCHAR,
            last_name VARCHAR,
            phone VARCHAR,
            email VARCHAR,
            created_at TIMESTAMP
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT phonebook.id, phonebook.username, phonebook.first_name, 
                   phonebook.last_name, phonebook.phone, phonebook.email, 
                   phonebook.created_at
            FROM phonebook
            ORDER BY phonebook.username
            LIMIT p_limit
            OFFSET p_offset;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    cursor.execute('''
        CREATE OR REPLACE FUNCTION delete_by_username_or_phone(
            p_username VARCHAR DEFAULT NULL,
            p_phone VARCHAR DEFAULT NULL
        )
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            IF p_username IS NOT NULL THEN
                DELETE FROM phonebook WHERE username = p_username;
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
            ELSIF p_phone IS NOT NULL THEN
                DELETE FROM phonebook WHERE phone = p_phone;
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
            ELSE
                deleted_count := 0;
            END IF;
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def search_by_pattern(pattern):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM search_by_pattern(%s)', (pattern,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def insert_or_update_user(username, first_name, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT insert_or_update_user(%s, %s, %s)', (username, first_name, phone))
    conn.commit()
    cursor.close()
    conn.close()

def insert_many_users(users_list):
    conn = get_connection()
    cursor = conn.cursor()
    users_array = []
    for user in users_list:
        if len(user) >= 2:
            first_name = str(user[2]) if len(user) > 2 else str(user[0])
            users_array.append([str(user[0]), str(user[1]), first_name])
    
    cursor.execute("SELECT * FROM insert_many_users(%s::TEXT[][])", (users_array,))
    incorrect = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return incorrect

def insert_many_from_console():
    users = []
    print("Enter users (format: username,phone,first_name). Type 'done' to finish:")
    while True:
        line = input("> ")
        if line.lower() == 'done':
            break
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 2:
            users.append(parts)
        else:
            print("Invalid format. Use: username,phone,first_name")
    
    if not users:
        print("No users to insert")
        return
    
    incorrect = insert_many_users(users)
    
    if incorrect:
        print("\nIncorrect data:")
        print("Username | Phone | Reason")
        print("-" * 50)
        for row in incorrect:
            print(f"{row[0]} | {row[1]} | {row[2]}")
    else:
        print("All users inserted successfully")

def get_contacts_paginated(limit, offset):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM get_contacts_paginated(%s, %s)', (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def delete_by_username_or_phone(username=None, phone=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT delete_by_username_or_phone(%s, %s)', (username, phone))
    deleted_count = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_count

def insert_from_csv(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found")
        return

    conn = get_connection()
    cursor = conn.cursor()

    with open(filename, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        for row in csv_reader:
            try:
                cursor.execute('''
                               INSERT INTO phonebook (username, first_name, last_name, phone, email)
                               VALUES (%s, %s, %s, %s, %s)
                               ''', (row['username'], row['first_name'], row.get('last_name', ''),
                                     row['phone'], row.get('email', '')))
                count += 1
            except psycopg2.Error as e:
                print(f"Error inserting {row.get('username', 'unknown')}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {count} records from CSV")

def insert_from_console():
    username = input("Username: ")
    first_name = input("First name: ")
    phone = input("Phone: ")

    try:
        insert_or_update_user(username, first_name, phone)
        print("Contact added/updated successfully")
    except psycopg2.Error as e:
        print(f"Error: {e}")

def update_contact():
    username = input("Enter username to update: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM phonebook WHERE username = %s', (username,))
    contact = cursor.fetchone()

    if not contact:
        print("Contact not found")
        cursor.close()
        conn.close()
        return

    print(f"Current: {contact[2]} {contact[3]} - {contact[4]}")

    new_first_name = input("New first name (press Enter to skip): ")
    new_phone = input("New phone (press Enter to skip): ")

    if new_first_name:
        cursor.execute('UPDATE phonebook SET first_name = %s WHERE username = %s',
                       (new_first_name, username))

    if new_phone:
        try:
            cursor.execute('UPDATE phonebook SET phone = %s WHERE username = %s',
                           (new_phone, username))
        except psycopg2.Error as e:
            print(f"Error updating phone: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return

    conn.commit()
    print("Contact updated successfully")
    cursor.close()
    conn.close()

def query_contacts():
    print("\n1. Show all contacts")
    print("2. Search by pattern")
    print("3. Paginated view")

    choice = input("Choose option: ")

    if choice == '1':
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM phonebook ORDER BY username')
        results = cursor.fetchall()
        cursor.close()
        conn.close()
    elif choice == '2':
        pattern = input("Enter search pattern: ")
        results = search_by_pattern(pattern)
    elif choice == '3':
        try:
            limit = int(input("Enter limit: "))
            offset = int(input("Enter offset: "))
            results = get_contacts_paginated(limit, offset)
        except ValueError:
            print("Invalid input")
            return
    else:
        print("Invalid option")
        return

    if not results:
        print("No contacts found")
    else:
        print("\nID | Username | First Name | Last Name | Phone | Email")
        print("-" * 80)
        for row in results:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3] or ''} | {row[4]} | {row[5] or ''}")

def delete_contact():
    print("Delete by:")
    print("1. Username")
    print("2. Phone")

    choice = input("Choose option: ")

    if choice == '1':
        username = input("Enter username: ")
        deleted = delete_by_username_or_phone(username=username)
    elif choice == '2':
        phone = input("Enter phone: ")
        deleted = delete_by_username_or_phone(phone=phone)
    else:
        print("Invalid option")
        return

    if deleted > 0:
        print(f"Deleted {deleted} contact(s)")
    else:
        print("Contact not found")

def main_menu():
    while True:
        print("\n=== PHONEBOOK ===")
        print("1. Insert/update contact")
        print("2. Insert many contacts")
        print("3. Upload contacts from CSV")
        print("4. Update contact")
        print("5. Query contacts")
        print("6. Delete contact")
        print("7. Exit")

        choice = input("\nChoose option: ")

        if choice == '1':
            insert_from_console()
        elif choice == '2':
            insert_many_from_console()
        elif choice == '3':
            filename = input("Enter CSV filename: ")
            insert_from_csv(filename)
        elif choice == '4':
            update_contact()
        elif choice == '5':
            query_contacts()
        elif choice == '6':
            delete_contact()
        elif choice == '7':
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    init_database()
    init_functions_and_procedures()
    main_menu()

