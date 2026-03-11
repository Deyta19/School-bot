import sqlite3

conn = sqlite3.connect("school.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jadwal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hari TEXT,
    mata_pelajaran TEXT
)
""")

conn.commit()


def tambah_jadwal(hari, mata_pelajaran):
    cursor.execute(
        "INSERT INTO jadwal (hari, mata_pelajaran) VALUES (?, ?)",
        (hari, mata_pelajaran)
    )
    conn.commit()


def ambil_jadwal(hari):
    cursor.execute(
        "SELECT mata_pelajaran FROM jadwal WHERE hari = ?",
        (hari,)
    )
    return cursor.fetchall()


def hapus_jadwal(hari, mata_pelajaran):
    cursor.execute(
        "DELETE FROM jadwal WHERE hari = ? AND mata_pelajaran = ?",
        (hari, mata_pelajaran)
    )
    conn.commit()

# ===============================
# TABEL ULANGAN / TUGAS
# ===============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS ulangan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    mata_pelajaran TEXT,
    deskripsi TEXT
)
""")

conn.commit()


def tambah_ulangan(tanggal, mapel, deskripsi):
    cursor.execute(
        "INSERT INTO ulangan (tanggal, mata_pelajaran, deskripsi) VALUES (?, ?, ?)",
        (tanggal, mapel, deskripsi)
    )
    conn.commit()


def ambil_ulangan():
    cursor.execute("SELECT * FROM ulangan")
    return cursor.fetchall()


def hapus_ulangan(id_ulangan):
    cursor.execute(
        "DELETE FROM ulangan WHERE id = ?",
        (id_ulangan,)
    )
    conn.commit()