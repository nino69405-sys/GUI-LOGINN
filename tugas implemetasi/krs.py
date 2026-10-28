# Mengimpor modul mysql.connector untuk koneksi ke database MySQL
import mysql.connector
# Mengimpor modul dasar tkinter untuk komponen GUI
import tkinter as tk
# Mengimpor ttk (untuk Treeview/tabel) dan messagebox untuk dialog notifikasi
from tkinter import ttk, messagebox
 
# Konfigurasi koneksi database MySQL (dipakai bersama oleh login & dashboard)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'siakad'
}
 
 
# ======================================================================
# JENDELA LOGIN
# ======================================================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - SIAKAD")
        self.root.geometry("380x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
 
        self.db_config = DB_CONFIG
 
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
 
        lbl_title = tk.Label(
            main_frame,
            text="SIAKAD LOGIN",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="black"
        )
        lbl_title.pack(pady=(0, 20))
 
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack()
 
        # Username (NIP)
        lbl_user = tk.Label(form_frame, text="Username:", font=("Arial", 10),
                            bg="#f0f0f0", anchor="e", width=10)
        lbl_user.grid(row=0, column=0, padx=5, pady=6, sticky="e")
        self.entry_nip = tk.Entry(form_frame, font=("Arial", 10), width=22,
                                  relief=tk.SOLID, bd=1)
        self.entry_nip.grid(row=0, column=1, padx=5, pady=6)
        self.entry_nip.focus()
 
        # Password (Email)
        lbl_pass = tk.Label(form_frame, text="Password:", font=("Arial", 10),
                            bg="#f0f0f0", anchor="e", width=10)
        lbl_pass.grid(row=1, column=0, padx=5, pady=6, sticky="e")
        self.entry_email = tk.Entry(form_frame, font=("Arial", 10), width=22,
                                    show="*", relief=tk.SOLID, bd=1)
        self.entry_email.grid(row=1, column=1, padx=5, pady=6)
 
        btn_login = tk.Button(
            main_frame,
            text="Login",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            width=15,
            bd=1,
            cursor="hand2",
            command=self.proses_login
        )
        btn_login.pack(pady=(20, 0))
 
        self.root.bind('<Return>', lambda event: self.proses_login())
 
    def proses_login(self):
        nip = self.entry_nip.get().strip()
        email = self.entry_email.get().strip()
 
        if not nip or not email:
            messagebox.showwarning("Peringatan", "Username (NIP) dan Password (Email) wajib diisi!")
            return
 
        conn = None
        cursor = None
 
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
 
            query = "SELECT nip, nama_dosen, email FROM dosen WHERE nip = %s AND email = %s"
            cursor.execute(query, (nip, email))
            user = cursor.fetchone()
 
            if user:
                messagebox.showinfo("Berhasil", f"Login berhasil!\nSelamat datang, {user['nama_dosen']}.")
                self.buka_dashboard(user)
            else:
                messagebox.showerror("Gagal", "Login gagal! Username atau Password salah.")
 
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Koneksi database bermasalah:\n{err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
 
    def buka_dashboard(self, user):
        # Tutup jendela login, lalu buka jendela baru berisi data KRS
        self.root.destroy()
        dash_root = tk.Tk()
        DashboardKRS(dash_root, user)
        dash_root.mainloop()
 
 
# ======================================================================
# JENDELA DASHBOARD: MENAMPILKAN ISI TABEL `krs`
# ======================================================================
class DashboardKRS:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("SIAKAD - Data KRS")
        self.root.geometry("820x380")
        self.root.configure(bg="#f0f0f0")
 
        # Judul + info dosen yang login
        lbl_title = tk.Label(root, text="DATA KRS", font=("Arial", 14, "bold"),
                             bg="#f0f0f0")
        lbl_title.pack(pady=(15, 0))
        lbl_user = tk.Label(root, text=f"Login sebagai: {user['nama_dosen']} ({user['nip']})",
                            font=("Arial", 9), bg="#f0f0f0", fg="#555555")
        lbl_user.pack(pady=(0, 10))
 
        # Frame tabel + scrollbar
        frame_tabel = tk.Frame(root, bg="#f0f0f0")
        frame_tabel.pack(expand=True, fill=tk.BOTH, padx=15, pady=(0, 10))
 
        # Kolom sesuai struktur tabel krs
        kolom = ("id_krs", "nim", "kode_mk", "semester_ambil",
                 "tahun_ajaran", "nilai_huruf", "nilai_angka")
        self.tree = ttk.Treeview(frame_tabel, columns=kolom, show="headings")
 
        # Judul kolom, lebar, dan perataan
        pengaturan = {
            "id_krs":         ("id_krs", 60, "center"),
            "nim":            ("nim", 100, "center"),
            "kode_mk":        ("kode_mk", 90, "center"),
            "semester_ambil": ("semester_ambil", 120, "center"),
            "tahun_ajaran":   ("tahun_ajaran", 110, "center"),
            "nilai_huruf":    ("nilai_huruf", 100, "center"),
            "nilai_angka":    ("nilai_angka", 100, "e"),
        }
        for k in kolom:
            teks, lebar, rata = pengaturan[k]
            self.tree.heading(k, text=teks)
            self.tree.column(k, width=lebar, anchor=rata)
 
        scroll = ttk.Scrollbar(frame_tabel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
 
        # Baris selang-seling agar mirip tampilan phpMyAdmin
        self.tree.tag_configure("genap", background="#e0e0e0")
        self.tree.tag_configure("ganjil", background="#ffffff")
 
        # Tombol segarkan & keluar
        frame_btn = tk.Frame(root, bg="#f0f0f0")
        frame_btn.pack(pady=(0, 15))
        tk.Button(frame_btn, text="Segarkan", width=12, command=self.muat_data).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Keluar", width=12, command=self.root.destroy).pack(side=tk.LEFT, padx=5)
 
        # Muat data saat jendela dibuka
        self.muat_data()
 
    def muat_data(self):
        # Kosongkan tabel terlebih dahulu
        for item in self.tree.get_children():
            self.tree.delete(item)
 
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_krs, nim, kode_mk, semester_ambil, tahun_ajaran, "
                "nilai_huruf, nilai_angka FROM krs ORDER BY id_krs"
            )
            for i, baris in enumerate(cursor.fetchall()):
                id_krs, nim, kode_mk, smt, tahun, huruf, angka = baris
                # Format nilai angka dengan 2 desimal (4.00, 3.75, dst.)
                angka_str = f"{float(angka):.2f}" if angka is not None else ""
                tag = "genap" if i % 2 else "ganjil"
                self.tree.insert("", tk.END,
                                 values=(id_krs, nim, kode_mk, smt, tahun, huruf, angka_str),
                                 tags=(tag,))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Gagal memuat data KRS:\n{err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
 