import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    client_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email VARCHAR(40) NOT NULL
                );
                """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS phone(
                    phone_id SERIAL PRIMARY KEY,
                    phone VARCHAR(12),
                    client_id INTEGER NOT NULL REFERENCES client(client_id)
                );
                """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING client_id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone_number in phones:
                cur.execute("""
                INSERT INTO phone(phone, client_id)
                VALUES(%s, %s);
                """, (phone_number, client_id))
                conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone(phone, client_id)
        VALUES(%s, %s); 
        """, (phone, client_id))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                UPDATE client
                SET first_name = %s
                WHERE client_id = %s; 
                """, (first_name, client_id))
            conn.commit()

        if last_name:
            cur.execute("""
                UPDATE client
                SET last_name = %s
                WHERE client_id = %s; 
                """, (last_name, client_id))
            conn.commit()

        if email:
            cur.execute("""
                UPDATE client
                SET email = %s
                WHERE client_id = %s; 
                """, (email, client_id))
            conn.commit()

        if phone:
            cur.execute("""
                UPDATE phone
                SET phone = %s
                WHERE client_id = %s; 
                """, (phone, client_id))
            conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone
            WHERE client_id = %s AND phone = %s; 
            """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phone
            WHERE client_id = %s; 
            """, (client_id))
        conn.commit()
        cur.execute("""
            DELETE FROM client
            WHERE client_id = %s; 
            """, (client_id))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT first_name, last_name, email, phone FROM client JOIN phone
            ON client.client_id = phone.client_id
            WHERE first_name = %s OR last_name = %s OR email = %s OR phone = %s;
            """, (first_name, last_name, email, phone))
        print(cur.fetchall())

with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    create_db(conn)

    add_client(conn, "Stive", "Rojers", "cap@yahoo.com", ["+01111111111"])
    add_client(conn, "Bruce", "Benner", "halk@rambler.com")
    add_client(conn, "Наташа", "Романова", "spy@yandex.ru", ["+71234567890"])
    add_client(conn, "Thor", "Hemsvort",
               "Valhalla@vrn.io", ["+00000000000", "+00000000001", "+00000000009"])
    add_client(conn, "Loki", "Lie", "lie@pravda.net", ["+88888888888"])

    add_phone(conn, 3, "+79876543210")

    change_client(conn=conn, client_id=2, email="halk@google.com")
    change_client(conn=conn, client_id=1, phone="+11111111111")

    delete_phone(conn, 4, "+00000000009")

    delete_client(conn, '5')

    find_client(conn=conn, phone="+71234567890")

conn.close()