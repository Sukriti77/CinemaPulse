import sqlite3

conn = sqlite3.connect('cinema_pulse.db')
cursor = conn.cursor()

print("=== ALL FEEDBACK ===")
cursor.execute('''
    SELECT f.id, m.title, f.user_email, f.rating, f.comment, f.timestamp
    FROM feedback f
    JOIN movies m ON f.movie_id = m.id
    ORDER BY f.timestamp DESC
''')

for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"Movie: {row[1]}")
    print(f"User: {row[2]}")
    print(f"Rating: {row[3]}/5")
    print(f"Comment: {row[4]}")
    print(f"Time: {row[5]}")
    print("-" * 50)

conn.close()