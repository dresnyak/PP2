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
    last_name = input("Last name (optional): ")
    phone = input("Phone: ")
    email = input("Email (optional): ")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO phonebook (username, first_name, last_name, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, first_name, last_name, phone, email))
        conn.commit()
        print("Contact added successfully")
    except psycopg2.Error as e:
        print(f"Error: {e}")
    
    cursor.close()
    conn.close()

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
    print("2. Search by username")
    print("3. Search by first name")
    print("4. Search by phone")
    
    choice = input("Choose option: ")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if choice == '1':
        cursor.execute('SELECT * FROM phonebook ORDER BY username')
    elif choice == '2':
        username = input("Enter username: ")
        cursor.execute('SELECT * FROM phonebook WHERE username ILIKE %s', (f'%{username}%',))
    elif choice == '3':
        first_name = input("Enter first name: ")
        cursor.execute('SELECT * FROM phonebook WHERE first_name ILIKE %s', (f'%{first_name}%',))
    elif choice == '4':
        phone = input("Enter phone: ")
        cursor.execute('SELECT * FROM phonebook WHERE phone ILIKE %s', (f'%{phone}%',))
    else:
        print("Invalid option")
        cursor.close()
        conn.close()
        return
    
    results = cursor.fetchall()
    
    if not results:
        print("No contacts found")
    else:
        print("\nID | Username | First Name | Last Name | Phone | Email")
        print("-" * 80)
        for row in results:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
    
    cursor.close()
    conn.close()

def delete_contact():
    print("Delete by:")
    print("1. Username")
    print("2. Phone")
    
    choice = input("Choose option: ")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if choice == '1':
        username = input("Enter username: ")
        cursor.execute('DELETE FROM phonebook WHERE username = %s', (username,))
    elif choice == '2':
        phone = input("Enter phone: ")
        cursor.execute('DELETE FROM phonebook WHERE phone = %s', (phone,))
    else:
        print("Invalid option")
        cursor.close()
        conn.close()
        return
    
    deleted = cursor.rowcount
    conn.commit()
    
    if deleted > 0:
        print(f"Deleted {deleted} contact(s)")
    else:
        print("Contact not found")
    
    cursor.close()
    conn.close()

def main_menu():
    while True:
        print("\n=== PHONEBOOK ===")
        print("1. Insert contact from console")
        print("2. Upload contacts from CSV")
        print("3. Update contact")
        print("4. Query contacts")
        print("5. Delete contact")
        print("6. Exit")
        
        choice = input("\nChoose option: ")
        
        if choice == '1':
            insert_from_console()
        elif choice == '2':
            filename = input("Enter CSV filename: ")
            insert_from_csv(filename)
        elif choice == '3':
            update_contact()
        elif choice == '4':
            query_contacts()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    init_database()
    main_menu()

