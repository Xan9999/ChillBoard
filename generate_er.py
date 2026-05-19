"""Generate a .dot ER diagram from db.sqlite3, excluding Django internal tables."""
import sqlite3
import subprocess
import re
import sys

IGNORE = {
    'django_migrations', 'django_content_type',
    'auth_permission', 'auth_group', 'auth_group_permissions',
    'auth_user_groups', 'auth_user_user_permissions',
    'django_admin_log', 'django_session',
    'sqlite_sequence',
}

def get_tables(conn):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [r[0] for r in cur if r[0] not in IGNORE]

def get_columns(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return cur.fetchall()  # (cid, name, type, notnull, dflt, pk)

def get_foreign_keys(conn, table):
    cur = conn.execute(f"PRAGMA foreign_key_list({table})")
    return cur.fetchall()  # (id, seq, table, from, to, ...)

def dot_label(table, columns):
    rows = ''.join(
        f'<TR><TD ALIGN="LEFT"><B>{c[1]}</B></TD>'
        f'<TD ALIGN="LEFT">{c[2] or "TEXT"}{"  PK" if c[5] else ""}</TD></TR>'
        for c in columns
    )
    return (
        f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
        f'<TR><TD COLSPAN="2" BGCOLOR="#4466aa"><FONT COLOR="white"><B>{table}</B></FONT></TD></TR>'
        f'{rows}</TABLE>>'
    )

def main():
    db_path = 'db.sqlite3'
    out_dot = 'ER-Shema.dot'
    out_png = 'ER-Shema.png'

    conn = sqlite3.connect(db_path)
    tables = get_tables(conn)

    lines = [
        'digraph ER {',
        '  graph [rankdir=LR, fontname="Helvetica", bgcolor="#1a1a2e"];',
        '  node [shape=none, fontname="Helvetica", fontcolor="white", fontsize=11];',
        '  edge [color="#aaaacc", fontname="Helvetica", fontsize=10, fontcolor="#ccccee"];',
    ]

    for table in tables:
        cols = get_columns(conn, table)
        label = dot_label(table, cols)
        lines.append(f'  {table} [label={label}];')

    lines.append('')
    for table in tables:
        for fk in get_foreign_keys(conn, table):
            from_col = fk[3]
            to_table = fk[2]
            to_col = fk[4]
            lines.append(f'  {table} -> {to_table} [label="{from_col} -&gt; {to_col}"];')

    lines.append('}')
    dot_src = '\n'.join(lines)

    with open(out_dot, 'w', encoding='utf-8') as f:
        f.write(dot_src)
    print(f"Written {out_dot}")

    result = subprocess.run(['dot', '-Tpng', f'-o{out_png}', out_dot], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Generated {out_png}")
    else:
        print("dot error:", result.stderr, file=sys.stderr)
        sys.exit(1)

    conn.close()

if __name__ == '__main__':
    main()
