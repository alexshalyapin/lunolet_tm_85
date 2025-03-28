import requests
import sqlite3
import json
from math import fabs

url = 'http://185.18.54.154:8000/myapp/receive_data/'
url2 = 'http://185.18.54.154:8000/myapp/clear_data/'

def clear_table():
    global url2
    response = requests.get(url2)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)


def sync_high_scores(player_name, x, u, V_h, m, i, _s0):
    """
    Synchronizes high scores between local SQLite database and remote server.

    Args:
        player_name (str): Current player's name
        x (list): List of x positions
        u (list): List of horizontal velocities
        V_h (list): List of vertical velocities
        m (list): List of remaining fuel masses
        i (int): Current iteration index
        _s0 (float): Target distance
    """
    # Local database setup
    url = 'http://185.18.54.154:8000/myapp/receive_tab_rec'
    local_db = 'hi_res.db'

    # 1. Create local database if it doesn't exist
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()

    # Create table if not exists (with correct schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS high_scores (
            name TEXT,
            c REAL,  # Deviation (s in server terms)
            y REAL,   # Vertical speed (u in server terms)
            m REAL,   # Remaining fuel
            v REAL    # Horizontal speed
        )
    ''')
    conn.commit()

    try:
        # 2. Check if all local records exist on server
        local_records = cursor.execute('SELECT name, c, y, m, v FROM high_scores').fetchall()

        for record in local_records:
            name, c, y, m_local, v = record
            # Check if record exists on server
            server_response = requests.get(url)
            if server_response.status_code == 200:
                server_data = server_response.json().get('table', [])
                found = False
                for entry in server_data:
                    if (entry['name'] == name and
                            abs(float(entry['s']) == abs(c) and
                                abs(float(entry['u'])) == abs(y) and
                                abs(float(entry['v'])) == abs(v) and
                                abs(float(entry['m'])) == abs(m_local))):
                        found = True
                        break

                if not found:
                    # Add missing record to server
                    data = {
                        'name': name,
                        's': c,
                        'u': y,
                        'v': v,
                        'm': m_local
                    }
                    json_data = json.dumps(data)
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, data=json_data, headers=headers)

        # 3. Check if all server records exist locally
        server_response = requests.get(url)
        if server_response.status_code == 200:
            server_data = server_response.json().get('table', [])
            for entry in server_data:
                # Check if record exists locally
                cursor.execute('''
                    SELECT 1 FROM high_scores 
                    WHERE name = ? AND c = ? AND y = ? AND m = ? AND v = ?
                ''', (
                    entry['name'],
                    float(entry['s']),
                    float(entry['u']),
                    float(entry['m']),
                    float(entry['v'])
                ))
                if not cursor.fetchone():
                    # Add missing record to local database
                    cursor.execute('''
                        INSERT INTO high_scores (name, c, y, m, v)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        entry['name'],
                        float(entry['s']),
                        float(entry['u']),
                        float(entry['m']),
                        float(entry['v'])
                    ))
            conn.commit()

        # 4. Add current player's score if not already present
        current_s = fabs(x[i - 1] - _s0)
        current_u = u[i - 1]
        current_v = V_h[i - 1]
        current_m = m[i - 1]

        cursor.execute('''
            SELECT 1 FROM high_scores 
            WHERE name = ? AND c = ? AND y = ? AND m = ? AND v = ?
        ''', (player_name, current_s, current_u, current_m, current_v))

        if not cursor.fetchone():
            # Add to local database
            cursor.execute('''
                INSERT INTO high_scores (name, c, y, m, v)
                VALUES (?, ?, ?, ?, ?)
            ''', (player_name, current_s, current_u, current_m, current_v))
            conn.commit()

            # Add to server
            data = {
                'name': player_name,
                's': current_s,
                'u': current_u,
                'v': current_v,
                'm': current_m
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json_data, headers=headers)

    except Exception as e:
        print(f"Error during synchronization: {str(e)}")
    finally:
        conn.close()


response = requests.get(url)

if response.status_code == 200:
    table = response.json().get('table', [])
    print("Received Table:")
    for entry in table:
        print(entry)
else:
    print(f"Error: {response.status_code}")
    print(response.text)