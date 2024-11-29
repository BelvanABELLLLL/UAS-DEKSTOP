import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

# Membuat/membuka database SQLite
conn = sqlite3.connect("shopping_list.db")
cursor = conn.cursor()

# Membuat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS shopping_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_id INTEGER,
    name TEXT,
    status TEXT DEFAULT 'Belum Dibeli',
    FOREIGN KEY (day_id) REFERENCES days (id)
)
""")
conn.commit()

# Fungsi untuk menambah daftar hari
def tambah_hari():
    day_name = simpledialog.askstring("Tambah Hari", "Masukkan nama hari:")
    if not day_name:
        return
    cursor.execute("INSERT INTO days (date) VALUES (?)", (day_name,))
    conn.commit()
    refresh_hari()
    messagebox.showinfo("Sukses", f"Daftar untuk hari '{day_name}' berhasil dibuat.")

# Fungsi untuk memperbarui daftar hari
def refresh_hari():
    for item in tree_hari.get_children():
        tree_hari.delete(item)
    
    cursor.execute("SELECT id, date FROM days")
    for day_id, date in cursor.fetchall():
        tree_hari.insert("", "end", iid=day_id, text=date)

# Fungsi untuk menampilkan daftar belanja di hari tertentu
def tampilkan_belanja(event):
    selected_day = tree_hari.focus()
    if not selected_day:
        return
    day_id = int(selected_day)
    refresh_belanja(day_id)

def refresh_belanja(day_id, search_text=""):
    for item in tree_belanja.get_children():
        tree_belanja.delete(item)
    
    query = "SELECT id, name, status FROM shopping_items WHERE day_id = ?"
    params = [day_id]
    
    if search_text:
        query += " AND name LIKE ?"
        params.append(f"%{search_text}%")
    
    cursor.execute(query, params)
    for item_id, name, status in cursor.fetchall():
        tree_belanja.insert("", "end", iid=item_id, values=(name, status))

# Fungsi untuk menambah item belanja
def tambah_belanja(event=None):
    selected_day = tree_hari.focus()
    if not selected_day:
        messagebox.showwarning("Kesalahan", "Pilih hari terlebih dahulu.")
        return
    item = entry_belanja.get()
    if item:
        day_id = int(selected_day)
        cursor.execute("INSERT INTO shopping_items (day_id, name) VALUES (?, ?)", (day_id, item))
        conn.commit()
        refresh_belanja(day_id)
        entry_belanja.delete(0, tk.END)
        messagebox.showinfo("Sukses", "Item belanja berhasil ditambahkan.")
    else:
        messagebox.showwarning("Input Salah", "Masukkan nama item belanja!")

# Fungsi untuk menghapus item belanja
def hapus_belanja():
    selected_item = tree_belanja.focus()
    if not selected_item:
        messagebox.showwarning("Kesalahan", "Pilih item belanja yang ingin dihapus.")
        return
    item_id = int(selected_item)
    cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
    conn.commit()
    selected_day = tree_hari.focus()
    if selected_day:
        refresh_belanja(int(selected_day))
    messagebox.showinfo("Sukses", "Item belanja berhasil dihapus.")

# Fungsi untuk mengubah status belanja
def ubah_status():
    selected_item = tree_belanja.focus()
    if not selected_item:
        messagebox.showwarning("Kesalahan", "Pilih item belanja yang ingin diubah statusnya.")
        return
    item_id = int(selected_item)
    cursor.execute("SELECT status FROM shopping_items WHERE id = ?", (item_id,))
    current_status = cursor.fetchone()[0]
    new_status = "Sudah Dibeli" if current_status == "Belum Dibeli" else "Belum Dibeli"
    cursor.execute("UPDATE shopping_items SET status = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    selected_day = tree_hari.focus()
    if selected_day:
        refresh_belanja(int(selected_day))
    messagebox.showinfo("Sukses", f"Status item belanja berhasil diubah menjadi {new_status}.")

# Fungsi untuk mencari item belanja
def cari_belanja():
    search_text = entry_cari.get()
    selected_day = tree_hari.focus()
    if selected_day:
        day_id = int(selected_day)
        refresh_belanja(day_id, search_text)
    else:
        messagebox.showwarning("Kesalahan", "Pilih hari terlebih dahulu.")

# Fungsi untuk mengubah nama hari
def ubah_nama_hari():
    selected_day = tree_hari.focus()
    if not selected_day:
        messagebox.showwarning("Kesalahan", "Pilih hari yang ingin diubah namanya.")
        return
    new_name = simpledialog.askstring("Ubah Nama Hari", "Masukkan nama baru:")
    if new_name:
        day_id = int(selected_day)
        cursor.execute("UPDATE days SET date = ? WHERE id = ?", (new_name, day_id))
        conn.commit()
        refresh_hari()
        messagebox.showinfo("Sukses", f"Nama hari berhasil diubah menjadi '{new_name}'.")

# Fungsi untuk menghapus hari
def hapus_hari():
    selected_day = tree_hari.focus()
    if not selected_day:
        messagebox.showwarning("Kesalahan", "Pilih hari yang ingin dihapus.")
        return
    
    day_id = int(selected_day)
    confirmation = messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus hari ini beserta semua item belanja terkait?")
    if confirmation:
        # Hapus item belanja terkait terlebih dahulu
        cursor.execute("DELETE FROM shopping_items WHERE day_id = ?", (day_id,))
        # Hapus hari dari database
        cursor.execute("DELETE FROM days WHERE id = ?", (day_id,))
        conn.commit()
        refresh_hari()
        tree_belanja.delete(*tree_belanja.get_children())  # Kosongkan daftar belanja
        messagebox.showinfo("Sukses", "Hari dan item belanja terkait berhasil dihapus.")

# Antarmuka Tkinter
root = tk.Tk()
root.title("Aplikasi Daftar Belanja")
root.geometry("800x500")

# Frame untuk Daftar Hari
frame_hari = ttk.LabelFrame(root, text="Daftar Hari")
frame_hari.pack(side="left", fill="y", padx=10, pady=10)

btn_tambah_hari = ttk.Button(frame_hari, text="Tambah Hari", command=tambah_hari)
btn_tambah_hari.pack(fill="x", padx=5, pady=5)

btn_ubah_nama_hari = ttk.Button(frame_hari, text="Ubah Nama Hari", command=ubah_nama_hari)
btn_ubah_nama_hari.pack(fill="x", padx=5, pady=5)

btn_hapus_hari = ttk.Button(frame_hari, text="Hapus Hari", command=hapus_hari)
btn_hapus_hari.pack(fill="x", padx=5, pady=5)

tree_hari = ttk.Treeview(frame_hari, columns=(), show="tree")
tree_hari.pack(fill="y", expand=True, padx=5, pady=5)
tree_hari.bind("<<TreeviewSelect>>", tampilkan_belanja)

# Frame untuk Daftar Belanja
frame_belanja = ttk.LabelFrame(root, text="Daftar Belanja")
frame_belanja.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Entry untuk pencarian item
frame_cari = ttk.LabelFrame(frame_belanja, text="Cari Item")
frame_cari.pack(fill="x", padx=5, pady=5)

ttk.Label(frame_cari, text="Cari:").pack(side="left", padx=5, pady=5)
entry_cari = ttk.Entry(frame_cari)
entry_cari.pack(side="left", fill="x", expand=True, padx=5, pady=5)

btn_cari = ttk.Button(frame_cari, text="Cari", command=cari_belanja)
btn_cari.pack(side="right", padx=5, pady=5)

# Treeview untuk daftar belanja
tree_belanja = ttk.Treeview(frame_belanja, columns=("Nama", "Status"), show="headings")
tree_belanja.heading("Nama", text="Nama Item")
tree_belanja.heading("Status", text="Status")
tree_belanja.pack(fill="both", expand=True, padx=5, pady=5)

# Frame Input
frame_input = ttk.LabelFrame(root, text="Input Item Belanja")
frame_input.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_input, text="Item Belanja:").grid(row=0, column=0, padx=5, pady=5)
entry_belanja = ttk.Entry(frame_input)
entry_belanja.grid(row=0, column=1, padx=5, pady=5)

btn_tambah_belanja = ttk.Button(frame_input, text="Tambah Item", command=tambah_belanja)
btn_tambah_belanja.grid(row=0, column=2, padx=5, pady=5)

# Tombol Hapus Item
btn_hapus_belanja = ttk.Button(root, text="Hapus Item", command=hapus_belanja)
btn_hapus_belanja.pack(side="bottom", fill="x", padx=10, pady=5)

# Tombol Ubah Status
btn_ubah_status = ttk.Button(root, text="Ubah Status", command=ubah_status)
btn_ubah_status.pack(side="bottom", fill="x", padx=10, pady=5)

refresh_hari()

root.mainloop()
