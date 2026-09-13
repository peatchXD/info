import sys
import subprocess
import importlib

# ----------------------------------------------------
# [AUTO-INSTALLER] ระบบตรวจสอบและติดตั้ง Library อัตโนมัติ
# ----------------------------------------------------
REQUIRED_PACKAGES = {
    "PIL": "Pillow",
    "psycopg2": "psycopg2-binary",
    "supabase": "supabase",
    "websockets": "websockets"
}

def auto_setup_dependencies():
    """ตรวจเช็กและติดตั้ง Packages ที่จำเป็นให้อัตโนมัติหากพบว่าในเครื่องยังไม่มี"""
    missing_packages = []
    
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(package_name)
            
    if missing_packages:
        print("=" * 60)
        print(" ⚡ ECU REMAP SYSTEM - AUTOMATIC DEPENDENCY SETUP")
        print("=" * 60)
        print(f"[*] พบ Library ที่ยังไม่ได้ติดตั้ง: {', '.join(missing_packages)}")
        print("[*] กำลังทำการติดตั้งให้อัตโนมัติ กรุณารอสักครู่...\n")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for package in missing_packages:
                print(f"--> กำลังติดตั้ง {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
            print("\n[+] ติดตั้ง Library ทั้งหมดเรียบร้อยแล้ว! กำลังเริ่มโปรแกรม...\n")
            print("=" * 60)
        except Exception as e:
            print(f"\n[!] เกิดข้อผิดพลาดในการติดตั้งอัตโนมัติ: {e}")

auto_setup_dependencies()

# ----------------------------------------------------
# Import โมดูลหลัก
# ----------------------------------------------------
import os
import json
import sqlite3
import datetime
import math
import time
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk
from supabase import create_client, Client

# ----------------------------------------------------
# 0. CONFIG & SUPABASE ONLINE LICENSE VERIFICATION
# ----------------------------------------------------
APP_VERSION = "1.0.3"
CONFIG_FILE = "config.json"

# Supabase Credentials (ใช้ Publishable key สำหรับฝั่ง Client)
SUPABASE_URL = "https://chtxisriybejpsyulxsq.supabase.co"
SUPABASE_KEY = "sb_publishable_HU_Fcc6TXI8REsqioep3TQ_pvemjLEq" 
DEFAULT_CLOUD_URL = "postgresql://postgres.chtxisriybejpsyulxsq:peatch2524131944!@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres"

try:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    supabase_client = None

def verify_online_license_key(user_key):
    """ตรวจสอบ License Key กับระบบ Supabase Cloud"""
    if not supabase_client:
        return False, "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ยึดสิทธิ์ License ได้"

    try:
        res = supabase_client.table("license_keys").select("*").eq("license_key", user_key).execute()
        
        if not res.data:
            return False, "❌ ไม่พบ License Key นี้ในระบบ!"

        key_info = res.data[0]
        
        if not key_info.get("is_active", False):
            return False, "❌ License Key นี้ถูกยกเลิกการใช้งานแล้ว!"

        expires_at_str = key_info.get("expires_at")
        if expires_at_str:
            expires_at = datetime.datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            if now_utc > expires_at:
                return False, f"❌ License Key หมดอายุแล้วเมื่อ ({expires_at.strftime('%Y-%m-%d')})"

        return True, "⚡ ถอดรหัสและเปิดใช้งานโปรแกรมเรียบร้อยแล้ว!"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการตรวจสอบสิทธิ์: {str(e)}"

def verify_saved_license():
    """ตรวจเช็กไฟล์ license.lic ในเครื่องเดิม"""
    license_file = "license.lic"
    if not os.path.exists(license_file):
        return False

    try:
        with open(license_file, "r") as f:
            saved_key = f.read().strip()
        
        is_valid, _ = verify_online_license_key(saved_key)
        return is_valid
    except Exception:
        return False

def show_license_popup():
    """หน้าต่างป๊อปอัพให้ลูกค้ากรอก Key เพื่อ Activate"""
    lic_root = tk.Tk()
    lic_root.title("🔒 ECU REMAP - ONLINE LICENSE ACTIVATION")
    
    win_w, win_h = 460, 280
    scr_w = lic_root.winfo_screenwidth()
    scr_h = lic_root.winfo_screenheight()
    x = int((scr_w / 2) - (win_w / 2))
    y = int((scr_h / 2) - (win_h / 2))
    lic_root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    lic_root.configure(bg="#030712")
    lic_root.resizable(False, False)
    lic_root.attributes("-topmost", True)

    is_activated = [False]

    border_frame = tk.Frame(lic_root, bg="#1e293b", highlightthickness=1, highlightbackground="#00f2fe")
    border_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    main_container = tk.Frame(border_frame, bg="#030712")
    main_container.pack(fill="both", expand=True, padx=2, pady=2)

    tk.Label(
        main_container,
        text="⚡ ONLINE LICENSE ACTIVATION ⚡",
        font=("Segoe UI", 11, "bold"),
        fg="#00f2fe",
        bg="#030712",
    ).pack(pady=(20, 2))

    tk.Label(
        main_container,
        text="กรอก LICENSE KEY ที่ได้รับจากผู้ให้บริการเพื่อเปิดใช้งาน",
        font=("Segoe UI", 8),
        fg="#94a3b8",
        bg="#030712",
    ).pack(pady=(0, 15))

    tk.Label(
        main_container,
        text="ENTER YOUR LICENSE KEY:",
        font=("Segoe UI", 8, "bold"),
        fg="#e2e8f0",
        bg="#030712",
    ).pack(anchor="w", padx=35)

    entry_key = tk.Entry(
        main_container,
        font=("Consolas", 11, "bold"),
        justify="center",
        bg="#020617",
        fg="#10b981",
        insertbackground="#00f2fe",
        relief="flat",
        highlightthickness=1,
        highlightbackground="#1e293b",
        highlightcolor="#00f2fe"
    )
    entry_key.pack(fill="x", padx=35, pady=(4, 20), ipady=5)
    entry_key.focus_set()

    def save_and_activate():
        input_key = entry_key.get().strip()
        if not input_key:
            messagebox.showwarning("WARNING", "กรุณากรอก License Key", parent=lic_root)
            return

        success, msg = verify_online_license_key(input_key)

        if success:
            with open("license.lic", "w") as f:
                f.write(input_key)
            messagebox.showinfo("ACTIVATION SUCCESS", msg, parent=lic_root)
            is_activated[0] = True
            lic_root.destroy()
        else:
            messagebox.showerror("ACCESS DENIED", msg, parent=lic_root)

    tk.Button(
        main_container,
        text="⚡ ACTIVATE SYSTEM",
        font=("Segoe UI", 9, "bold"),
        bg="#0284c7",
        fg="white",
        activebackground="#38bdf8",
        activeforeground="#030712",
        relief="flat",
        cursor="hand2",
        command=save_and_activate
    ).pack(pady=5, ipadx=15, ipady=4)

    lic_root.mainloop()
    return is_activated[0]

def check_or_prompt_license():
    if verify_saved_license():
        return True
    return show_license_popup()

# ----------------------------------------------------
# 1. จัดการฐานข้อมูล (Cloud PostgreSQL หรือ Local SQLite)
# ----------------------------------------------------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {"use_cloud": True, "cloud_db_url": DEFAULT_CLOUD_URL}
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"use_cloud": True, "cloud_db_url": DEFAULT_CLOUD_URL}

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

app_config = load_config()
USE_CLOUD = app_config.get("use_cloud", True)
CLOUD_DB_URL = app_config.get("cloud_db_url", DEFAULT_CLOUD_URL)
is_connected_cloud = False

def get_connection():
    global is_connected_cloud, USE_CLOUD, CLOUD_DB_URL
    if USE_CLOUD and CLOUD_DB_URL.strip():
        import psycopg2
        conn = psycopg2.connect(CLOUD_DB_URL, connect_timeout=5)
        is_connected_cloud = True
        return conn
    else:
        conn = sqlite3.connect("remap_database.db")
        is_connected_cloud = False
        return conn

def init_db():
    global is_connected_cloud
    try:
        conn = get_connection()
        cursor = conn.cursor()
        auto_inc = "SERIAL" if USE_CLOUD else "INTEGER PRIMARY KEY AUTOINCREMENT"
        pk_stmt = f"id {auto_inc} PRIMARY KEY" if USE_CLOUD else "id INTEGER PRIMARY KEY AUTOINCREMENT"
        blob_type = "BYTEA" if USE_CLOUD else "BLOB"

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS customers (
                {pk_stmt},
                date TEXT, customer_name TEXT, phone TEXT, car_brand TEXT, car_model TEXT, engine_spec TEXT,
                plate_number TEXT, ecu_type TEXT, remap_stage TEXT, price REAL, note TEXT,
                bin_filename TEXT, bin_data {blob_type}, xdf_filename TEXT, xdf_data {blob_type}
            )
        """)

        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN engine_spec TEXT;")
            conn.commit()
        except Exception:
            conn.rollback()

        columns_to_add = [
            ("bin_filename", "TEXT"), ("bin_data", blob_type),
            ("xdf_filename", "TEXT"), ("xdf_data", blob_type),
        ]

        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except Exception:
                conn.rollback()

        conn.close()
    except Exception as e:
        is_connected_cloud = False
        messagebox.showerror("Database Error", f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้:\n{e}")

def insert_data(date, name, phone, brand, model, engine_spec, plate, ecu, stage, price, note, bin_filename="", bin_data=None, xdf_filename="", xdf_data=None):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"

    if USE_CLOUD:
        import psycopg2
        if bin_data: bin_data = psycopg2.Binary(bin_data)
        if xdf_data: xdf_data = psycopg2.Binary(xdf_data)

    query = f"""
        INSERT INTO customers (date, customer_name, phone, car_brand, car_model, engine_spec, plate_number, ecu_type, remap_stage, price, note, bin_filename, bin_data, xdf_filename, xdf_data)
        VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})
    """
    cursor.execute(query, (date, name, phone, brand, model, engine_spec, plate, ecu, stage, price, note, bin_filename, bin_data, xdf_filename, xdf_data))
    conn.commit()
    conn.close()

def update_data(customer_id, date, name, phone, brand, model, engine_spec, plate, ecu, stage, price, note, bin_filename=None, bin_data=None, xdf_filename=None, xdf_data=None, update_bin=False, update_xdf=False):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"

    fields = [
        f"date = {param}", f"customer_name = {param}", f"phone = {param}",
        f"car_brand = {param}", f"car_model = {param}", f"engine_spec = {param}",
        f"plate_number = {param}", f"ecu_type = {param}", f"remap_stage = {param}",
        f"price = {param}", f"note = {param}"
    ]
    values = [date, name, phone, brand, model, engine_spec, plate, ecu, stage, price, note]

    if update_bin:
        fields.append(f"bin_filename = {param}")
        fields.append(f"bin_data = {param}")
        if USE_CLOUD and bin_data:
            import psycopg2
            bin_data = psycopg2.Binary(bin_data)
        values.extend([bin_filename, bin_data])

    if update_xdf:
        fields.append(f"xdf_filename = {param}")
        fields.append(f"xdf_data = {param}")
        if USE_CLOUD and xdf_data:
            import psycopg2
            xdf_data = psycopg2.Binary(xdf_data)
        values.extend([xdf_filename, xdf_data])

    values.append(customer_id)
    query = f"UPDATE customers SET {', '.join(fields)} WHERE id = {param}"
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()

def delete_data(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"
    cursor.execute(f"DELETE FROM customers WHERE id = {param}", (customer_id,))
    conn.commit()
    conn.close()

def clear_all_database_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers")
    conn.commit()
    conn.close()

def reset_database_id_sequence():
    conn = get_connection()
    cursor = conn.cursor()
    if USE_CLOUD:
        cursor.execute("ALTER SEQUENCE customers_id_seq RESTART WITH 1")
    else:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
    conn.commit()
    conn.close()

def fetch_all_data(query_str=""):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"

    if query_str:
        q = f"%{query_str}%"
        query = f"""
            SELECT id, date, customer_name, phone, car_brand, car_model, engine_spec, plate_number, ecu_type, remap_stage, price, note, bin_filename, xdf_filename 
            FROM customers 
            WHERE customer_name LIKE {param} OR phone LIKE {param} OR plate_number LIKE {param} OR car_brand LIKE {param} OR engine_spec LIKE {param} OR ecu_type LIKE {param} OR bin_filename LIKE {param} OR xdf_filename LIKE {param}
            ORDER BY id DESC
        """
        cursor.execute(query, (q, q, q, q, q, q, q, q))
    else:
        query = """
            SELECT id, date, customer_name, phone, car_brand, car_model, engine_spec, plate_number, ecu_type, remap_stage, price, note, bin_filename, xdf_filename 
            FROM customers ORDER BY id DESC
        """
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_bin_file(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"
    cursor.execute(f"SELECT bin_filename, bin_data FROM customers WHERE id = {param}", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def fetch_xdf_file(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    param = "%s" if USE_CLOUD else "?"
    cursor.execute(f"SELECT xdf_filename, xdf_data FROM customers WHERE id = {param}", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return row


# ----------------------------------------------------
# 2. Custom UI Components (ขอบมน & ปรับสีตาม Theme)
# ----------------------------------------------------
class RoundedCanvasCard(tk.Canvas):
    def __init__(
        self,
        parent,
        bg_color="#0b1329",
        border_color="#1e293b",
        radius=14,
        *args,
        **kwargs,
    ):
        super().__init__(
            parent, bg=parent["bg"], highlightthickness=0, *args, **kwargs
        )
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.bind("<Configure>", self._draw)

    def set_colors(self, bg_color, border_color):
        self.bg_color = bg_color
        self.border_color = border_color
        self.config(bg=self.master["bg"])
        self._draw()

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self.radius

        self.create_arc(
            0,
            0,
            2 * r,
            2 * r,
            start=90,
            extent=90,
            fill=self.bg_color,
            outline=self.bg_color,
        )
        self.create_arc(
            w - 2 * r,
            0,
            w,
            2 * r,
            start=0,
            extent=90,
            fill=self.bg_color,
            outline=self.bg_color,
        )
        self.create_arc(
            w - 2 * r,
            h - 2 * r,
            w,
            h,
            start=270,
            extent=90,
            fill=self.bg_color,
            outline=self.bg_color,
        )
        self.create_arc(
            0,
            h - 2 * r,
            2 * r,
            h,
            start=180,
            extent=90,
            fill=self.bg_color,
            outline=self.bg_color,
        )

        self.create_rectangle(
            r, 0, w - r, h, fill=self.bg_color, outline=self.bg_color
        )
        self.create_rectangle(
            0, r, w, h - r, fill=self.bg_color, outline=self.bg_color
        )

        # Border Lines
        self.create_arc(
            0,
            0,
            2 * r,
            2 * r,
            start=90,
            extent=90,
            style=tk.ARC,
            outline=self.border_color,
            width=1.5,
        )
        self.create_arc(
            w - 2 * r,
            0,
            w,
            2 * r,
            start=0,
            extent=90,
            style=tk.ARC,
            outline=self.border_color,
            width=1.5,
        )
        self.create_arc(
            w - 2 * r,
            h - 2 * r,
            w,
            h,
            start=270,
            extent=90,
            style=tk.ARC,
            outline=self.border_color,
            width=1.5,
        )
        self.create_arc(
            0,
            h - 2 * r,
            2 * r,
            h,
            start=180,
            extent=90,
            style=tk.ARC,
            outline=self.border_color,
            width=1.5,
        )

        self.create_line(
            r, 0, w - r, 0, fill=self.border_color, width=1.5
        )
        self.create_line(
            w, r, w, h - r, fill=self.border_color, width=1.5
        )
        self.create_line(
            r, h, w - r, h, fill=self.border_color, width=1.5
        )
        self.create_line(
            0, r, 0, h - r, fill=self.border_color, width=1.5
        )


class ModernRoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command=None,
        bg="#0ea5e9",
        hover_bg="#38bdf8",
        fg="#ffffff",
        radius=8,
        font=("Segoe UI", 8, "bold"),
        width=95,
        height=26,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.text = text
        self.bg_color = bg
        self.hover_color = hover_bg
        self.current_bg = bg
        self.fg_color = fg
        self.radius = radius
        self.font = font
        self.btn_width = width
        self.btn_height = height

        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def set_bg(self, bg, hover_bg):
        self.bg_color = bg
        self.hover_color = hover_bg
        self.current_bg = bg
        self.config(bg=self.master["bg"])
        self._draw()

    def set_text(self, text):
        self.text = text
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.btn_width, self.btn_height
        r = self.radius

        self.create_arc(
            0,
            0,
            2 * r,
            2 * r,
            start=90,
            extent=90,
            fill=self.current_bg,
            outline=self.current_bg,
        )
        self.create_arc(
            w - 2 * r,
            0,
            w,
            2 * r,
            start=0,
            extent=90,
            fill=self.current_bg,
            outline=self.current_bg,
        )
        self.create_arc(
            w - 2 * r,
            h - 2 * r,
            w,
            h,
            start=270,
            extent=90,
            fill=self.current_bg,
            outline=self.current_bg,
        )
        self.create_arc(
            0,
            h - 2 * r,
            2 * r,
            h,
            start=180,
            extent=90,
            fill=self.current_bg,
            outline=self.current_bg,
        )

        self.create_rectangle(
            r, 0, w - r, h, fill=self.current_bg, outline=self.current_bg
        )
        self.create_rectangle(
            0, r, w, h - r, fill=self.current_bg, outline=self.current_bg
        )

        self.create_text(
            w / 2,
            h / 2,
            text=self.text,
            fill=self.fg_color,
            font=self.font,
        )

    def _on_enter(self, e):
        self.current_bg = self.hover_color
        self._draw()

    def _on_leave(self, e):
        self.current_bg = self.bg_color
        self._draw()

    def _on_click(self, e):
        if self.command:
            self.command()


# ----------------------------------------------------
# 3. ธีมสี (Themes Palette)
# ----------------------------------------------------
THEMES = {
    "Cyberpunk (ฟ้า-เข้ม)": {
        "BG_MAIN": "#030712",
        "CARD_BG": "#0b1329",
        "ACCENT_CYAN": "#00f2fe",
        "ACCENT_BLUE": "#38bdf8",
        "BORDER_COLOR": "#1e293b",
        "ENTRY_BG": "#020617",
    },
    "Deep Space (ม่วง-นีออน)": {
        "BG_MAIN": "#0b0914",
        "CARD_BG": "#161224",
        "ACCENT_CYAN": "#c084fc",
        "ACCENT_BLUE": "#a855f7",
        "BORDER_COLOR": "#2e2344",
        "ENTRY_BG": "#0a0712",
    },
    "Emerald Dark (เขียว-มินิมอล)": {
        "BG_MAIN": "#022c22",
        "CARD_BG": "#064e3b",
        "ACCENT_CYAN": "#34d399",
        "ACCENT_BLUE": "#10b981",
        "BORDER_COLOR": "#047857",
        "ENTRY_BG": "#022c22",
    },
}

current_theme = THEMES["Cyberpunk (ฟ้า-เข้ม)"].copy()

# ----------------------------------------------------
# 4. ตรวจสอบสิทธิ์ LICENSE ก่อนสร้างแอปหลัก (Pre-Execution Guard)
# ----------------------------------------------------
if not check_or_prompt_license():
    sys.exit(0)

# ----------------------------------------------------
# 5. หน้าโหลดโปรแกรมรายละเอียด (Splash Screen with % Progress Bar)
# ----------------------------------------------------
splash = tk.Tk()
splash.overrideredirect(True)
splash_w, splash_h = 500, 280
s_scr_w = splash.winfo_screenwidth()
s_scr_h = splash.winfo_screenheight()
splash_x = int((s_scr_w / 2) - (splash_w / 2))
splash_y = int((s_scr_h / 2) - (splash_h / 2))
splash.geometry(f"{splash_w}x{splash_h}+{splash_x}+{splash_y}")
splash.configure(bg="#030712")

canvas_splash = tk.Canvas(splash, bg="#030712", highlightthickness=0)
canvas_splash.pack(fill="both", expand=True)

# กรอบเรืองแสง
canvas_splash.create_rectangle(5, 5, splash_w - 5, splash_h - 5, outline="#1e293b", width=2)
canvas_splash.create_text(
    splash_w / 2, 60, text="⚡ ECU REMAP PERFORMANCE", fill="#00f2fe", font=("Segoe UI", 16, "bold")
)
canvas_splash.create_text(
    splash_w / 2, 90, text="INITIALIZING SYSTEM DATA CENTER...", fill="#64748b", font=("Consolas", 9, "bold")
)

lbl_splash_status = tk.Label(splash, text="กำลังเตรียมความพร้อมของระบบ...", fg="#38bdf8", bg="#030712", font=("Segoe UI", 9))
lbl_splash_status.place(x=50, y=145)

lbl_splash_percent = tk.Label(splash, text="0%", fg="#00f2fe", bg="#030712", font=("Consolas", 11, "bold"))
lbl_splash_percent.place(x= splash_w - 90, y=145)

# Progress bar container
canvas_splash.create_rectangle(50, 175, splash_w - 50, 190, outline="#1e293b", fill="#020617", width=1.5)
progress_bar = canvas_splash.create_rectangle(52, 177, 52, 188, fill="#00f2fe", outline="")

loading_steps = [
    (15, "กำลังตรวจสอบและยืนยันสิทธิ์ License HWID..."),
    (35, "กำลังตรวจสอบและสร้างตารางฐานข้อมูล..."),
    (65, "กำลังทดสอบการเชื่อมต่อฐานข้อมูล (Supabase Cloud)..."),
    (85, "กำลังโหลดการตั้งค่า UI และระบบธีมสี Cyberpunk..."),
    (100, "ระบบพร้อมใช้งานแล้ว! กำลังเข้าสู่โปรแกรมหลัก..."),
]

for p, status in loading_steps:
    lbl_splash_status.config(text=status)
    lbl_splash_percent.config(text=f"{p}%")
    
    start_x = 52
    target_x = 52 + int(((splash_w - 104) * p) / 100)
    canvas_splash.coords(progress_bar, start_x, 177, target_x, 188)
    splash.update()
    
    if p == 35:
        init_db()
    time.sleep(0.35)

splash.destroy()

# ----------------------------------------------------
# 6. ฟังก์ชันการทำงานของ GUI หลัก
# ----------------------------------------------------
selected_bin_path = None
selected_xdf_path = None
current_selected_id = None  # สำหรับอ้างอิง ID รายการที่กำลังแก้ไข


def select_bin_file():
    global selected_bin_path
    filepath = filedialog.askopenfilename(
        title="เลือกไฟล์ Bin ของลูกค้า",
        filetypes=[
            ("BIN / ECU Files", "*.bin *.hex *.ori *.mod"),
            ("All Files", "*.*"),
        ],
    )
    if filepath:
        selected_bin_path = filepath
        filename = os.path.basename(filepath)
        entry_bin_file.config(state="normal")
        entry_bin_file.delete(0, tk.END)
        entry_bin_file.insert(0, filename)
        entry_bin_file.config(state="readonly")


def select_xdf_file():
    global selected_xdf_path
    filepath = filedialog.askopenfilename(
        title="เลือกไฟล์ XDF MAP Definition",
        filetypes=[("XDF Files", "*.xdf"), ("All Files", "*.*")],
    )
    if filepath:
        selected_xdf_path = filepath
        filename = os.path.basename(filepath)
        entry_xdf_file.config(state="normal")
        entry_xdf_file.delete(0, tk.END)
        entry_xdf_file.insert(0, filename)
        entry_xdf_file.config(state="readonly")


def save_customer():
    global selected_bin_path, selected_xdf_path, current_selected_id
    date = entry_date.get().strip()
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    brand = entry_brand.get().strip()
    model = entry_model.get().strip()
    engine_spec = entry_engine.get().strip()
    plate = entry_plate.get().strip()
    ecu = entry_ecu.get().strip()
    stage = combo_stage.get()
    price = entry_price.get().strip()
    note = text_note.get("1.0", tk.END).strip()

    if not name or not phone or not plate:
        messagebox.showwarning(
            "แจ้งเตือน", "กรุณากรอก ชื่อลูกค้า, เบอร์โทร/FB/IG และทะเบียนรถ"
        )
        return

    try:
        price_val = float(price) if price else 0.0
    except ValueError:
        messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกราคาเป็นตัวเลข")
        return

    bin_filename = ""
    bin_data = None
    update_bin = False
    if selected_bin_path and os.path.exists(selected_bin_path):
        bin_filename = os.path.basename(selected_bin_path)
        with open(selected_bin_path, "rb") as f:
            bin_data = f.read()
        update_bin = True

    xdf_filename = ""
    xdf_data = None
    update_xdf = False
    if selected_xdf_path and os.path.exists(selected_xdf_path):
        xdf_filename = os.path.basename(selected_xdf_path)
        with open(selected_xdf_path, "rb") as f:
            xdf_data = f.read()
        update_xdf = True

    try:
        if current_selected_id:
            # โหมดแก้ไขข้อมูลเดิม
            update_data(
                current_selected_id,
                date,
                name,
                phone,
                brand,
                model,
                engine_spec,
                plate,
                ecu,
                stage,
                price_val,
                note,
                bin_filename,
                bin_data,
                xdf_filename,
                xdf_data,
                update_bin=update_bin,
                update_xdf=update_xdf,
            )
            messagebox.showinfo(
                "SYSTEM ONLINE", f"⚡ อัปเดตข้อมูล ID #{current_selected_id} เรียบร้อยแล้ว!"
            )
        else:
            # โหมดเพิ่มข้อมูลใหม่
            insert_data(
                date,
                name,
                phone,
                brand,
                model,
                engine_spec,
                plate,
                ecu,
                stage,
                price_val,
                note,
                bin_filename,
                bin_data,
                xdf_filename,
                xdf_data,
            )
            messagebox.showinfo(
                "SYSTEM ONLINE", "⚡ บันทึกข้อมูลและไฟล์เรียบร้อยแล้ว!"
            )

        clear_fields()
        load_table_data()
    except Exception as e:
        messagebox.showerror(
            "Database Error", f"ไม่สามารถบันทึก/แก้ไขข้อมูลได้:\n{e}"
        )


def download_selected_bin():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning(
            "แจ้งเตือน", "กรุณาคลิกเลือกรายการที่ต้องการดาวน์โหลดไฟล์ Bin"
        )
        return

    item_data = tree.item(selected_item[0])["values"]
    customer_id = item_data[0]

    res = fetch_bin_file(customer_id)
    if not res or not res[1]:
        messagebox.showinfo(
            "Information", "รายการนี้ไม่มีไฟล์ Bin แนบไว้อยู่ในระบบ"
        )
        return

    filename, bin_bytes = res[0], res[1]
    if isinstance(bin_bytes, memoryview):
        bin_bytes = bytes(bin_bytes)

    save_path = filedialog.asksaveasfilename(
        initialfile=filename,
        title="บันทึกไฟล์ Bin ลงในคอมพิวเตอร์",
        filetypes=[("BIN Files", "*.bin"), ("All Files", "*.*")],
    )

    if save_path:
        with open(save_path, "wb") as f:
            f.write(bin_bytes)
        messagebox.showinfo(
            "DOWNLOAD SUCCESS", f"ดาวน์โหลดไฟล์สำเร็จ:\n{save_path}"
        )


def download_selected_xdf():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning(
            "แจ้งเตือน", "กรุณาคลิกเลือกรายการที่ต้องการดาวน์โหลดไฟล์ XDF"
        )
        return

    item_data = tree.item(selected_item[0])["values"]
    customer_id = item_data[0]

    res = fetch_xdf_file(customer_id)
    if not res or not res[1]:
        messagebox.showinfo(
            "Information", "รายการนี้ไม่มีไฟล์ XDF แนบไว้อยู่ในระบบ"
        )
        return

    filename, xdf_bytes = res[0], res[1]
    if isinstance(xdf_bytes, memoryview):
        xdf_bytes = bytes(xdf_bytes)

    save_path = filedialog.asksaveasfilename(
        initialfile=filename,
        title="บันทึกไฟล์ XDF ลงในคอมพิวเตอร์",
        filetypes=[("XDF Files", "*.xdf"), ("All Files", "*.*")],
    )

    if save_path:
        with open(save_path, "wb") as f:
            f.write(xdf_bytes)
        messagebox.showinfo(
            "DOWNLOAD SUCCESS", f"ดาวน์โหลดไฟล์สำเร็จ:\n{save_path}"
        )


def delete_selected_customer():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning(
            "แจ้งเตือน", "กรุณาคลิกเลือกรายการที่ต้องการลบในตารางก่อน"
        )
        return

    item_data = tree.item(selected_item[0])
    customer_id = item_data["values"][0]
    customer_name = item_data["values"][2]
    car_plate = item_data["values"][7]

    confirm = messagebox.askyesno(
        "CONFIRM DELETE",
        f"คุณต้องการลบประวัติของ '{customer_name}'\nทะเบียนรถ: {car_plate}\nยืนยันหรือไม่?",
        icon="warning",
    )

    if confirm:
        delete_data(customer_id)
        messagebox.showinfo("SUCCESS", "ลบข้อมูลประวัติลูกค้าเรียบร้อยแล้ว")
        clear_fields()
        load_table_data()


def reset_database_id():
    """ฟังก์ชันสำหรับกดปุ่ม Reset ID ลำดับรายการใหม่"""
    confirm = messagebox.askyesno(
        "CONFIRM RESET ID",
        "คุณต้องการ Reset Sequence ของ ID กลับไปเริ่มที่ 1 ใช่หรือไม่?",
        icon="warning",
    )
    if confirm:
        try:
            reset_database_id_sequence()
            messagebox.showinfo("SUCCESS", "รีเซ็ต ID เรียบร้อยแล้ว")
            load_table_data()
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถรีเซ็ต ID ได้:\n{e}")


def clear_all_data():
    """ฟังก์ชันสำหรับกดปุ่มล้างข้อมูลทั้งหมด"""
    confirm = messagebox.askyesno(
        "DANGER: CLEAR ALL DATA",
        "⚠️ คุณแน่ใจหรือไม่ที่จะลบข้อมูลประวัติลูกค้าทั้งหมดในฐานข้อมูล?\n\nการกระทำนี้ไม่สามารถย้อนกลับได้!",
        icon="error",
    )
    if confirm:
        try:
            clear_all_database_records()
            try:
                reset_database_id_sequence()
            except Exception:
                pass
            messagebox.showinfo("SUCCESS", "ล้างข้อมูลทั้งหมดในฐานข้อมูลเรียบร้อยแล้ว")
            clear_fields()
            load_table_data()
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถล้างข้อมูลได้:\n{e}")


def on_tree_double_click(event):
    global current_selected_id
    selected_item = tree.selection()
    if not selected_item:
        return

    item_data = tree.item(selected_item[0])["values"]
    clear_fields()

    # ดึง ID บันทึกไว้เพื่ออัปเดต
    current_selected_id = item_data[0]

    entry_date.delete(0, tk.END)
    entry_date.insert(0, str(item_data[1]))
    entry_name.insert(0, str(item_data[2]))
    entry_phone.insert(0, str(item_data[3]))
    entry_brand.insert(0, str(item_data[4]))
    entry_model.insert(0, str(item_data[5]))
    entry_engine.insert(0, str(item_data[6]))
    entry_plate.insert(0, str(item_data[7]))
    entry_ecu.insert(0, str(item_data[8]))
    combo_stage.set(str(item_data[9]))

    price_clean = str(item_data[10]).replace(",", "")
    entry_price.insert(0, price_clean)
    text_note.insert("1.0", str(item_data[11]))

    bin_name = (
        str(item_data[12])
        if len(item_data) > 12 and item_data[12] is not None
        else ""
    )
    entry_bin_file.config(state="normal")
    entry_bin_file.delete(0, tk.END)
    entry_bin_file.insert(0, bin_name)
    entry_bin_file.config(state="readonly")

    xdf_name = (
        str(item_data[13])
        if len(item_data) > 13 and item_data[13] is not None
        else ""
    )
    entry_xdf_file.config(state="normal")
    entry_xdf_file.delete(0, tk.END)
    entry_xdf_file.insert(0, xdf_name)
    entry_xdf_file.config(state="readonly")

    # เปลี่ยนชื่อหัวข้อฟอร์มและปุ่มบันทึกเพื่อแสดงสถานะแก้ไข
    form_title_lbl.config(text=f"✏️ แก้ไขข้อมูลลูกค้า (ID: {current_selected_id})")
    btn_save.set_text("💾 บันทึกแก้ไข")


def clear_fields():
    global selected_bin_path, selected_xdf_path, current_selected_id
    selected_bin_path = None
    selected_xdf_path = None
    current_selected_id = None

    form_title_lbl.config(text="🛠️ กรอกข้อมูลรถและประวัติการจูน")
    btn_save.set_text("💾 บันทึกข้อมูล")

    entry_date.delete(0, tk.END)
    entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_brand.delete(0, tk.END)
    entry_model.delete(0, tk.END)
    entry_engine.delete(0, tk.END)
    entry_plate.delete(0, tk.END)
    entry_ecu.delete(0, tk.END)
    combo_stage.current(0)
    entry_price.delete(0, tk.END)
    text_note.delete("1.0", tk.END)

    entry_bin_file.config(state="normal")
    entry_bin_file.delete(0, tk.END)
    entry_bin_file.config(state="readonly")

    entry_xdf_file.config(state="normal")
    entry_xdf_file.delete(0, tk.END)
    entry_xdf_file.config(state="readonly")


pulse_state = True


def toggle_pulse_status():
    global pulse_state
    pulse_state = not pulse_state
    if USE_CLOUD and is_connected_cloud:
        color = "#10b981" if pulse_state else "#059669"
        lbl_status.config(text="🟢 ONLINE (CLOUD)", fg=color)
    else:
        color = "#f43f5e" if pulse_state else "#9f1239"
        lbl_status.config(text="🔴 OFFLINE (LOCAL)", fg=color)
    root.after(800, toggle_pulse_status)


def load_table_data(query_str=""):
    for item in tree.get_children():
        tree.delete(item)

    try:
        data = fetch_all_data(query_str)
        total_cars = len(data)
        total_revenue = 0.0

        for i, row in enumerate(data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            formatted_row = list(row)
            if isinstance(formatted_row[10], (int, float)):
                total_revenue += formatted_row[10]
                formatted_row[10] = f"{formatted_row[10]:,.2f}"

            if formatted_row[12] is None:
                formatted_row[12] = ""
            if formatted_row[13] is None:
                formatted_row[13] = ""

            tree.insert("", tk.END, values=formatted_row, tags=(tag,))

        lbl_kpi_count.config(text=f"{total_cars} คัน")
        lbl_kpi_revenue.config(text=f"฿ {total_revenue:,.2f}")

    except Exception as e:
        messagebox.showerror(
            "Error", f"ไม่สามารถดึงข้อมูลจากฐานข้อมูลได้:\n{e}"
        )


def on_search(event=None):
    search_term = entry_search.get().strip()
    load_table_data(search_term)


# ----------------------------------------------------
# 7. ฟังก์ชันตั้งค่าสี และ โลโก้ (Settings Modal)
# ----------------------------------------------------
lbl_img_global = None


def upload_logo():
    filepath = filedialog.askopenfilename(
        title="เลือกรูปภาพโลโก้อู่/ร้าน",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg"),
            ("All Files", "*.*"),
        ],
    )
    if filepath:
        try:
            shutil.copy(filepath, "logo.png")
            messagebox.showinfo("SUCCESS", "อัปเดตโลโก้ร้านเรียบร้อยแล้ว!")
            load_garage_logo()
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถเปลี่ยนโลโก้ได้:\n{e}")


def reset_logo():
    """ฟังก์ชันคืนค่าโลโก้เดิม (แอนิเมชันเข็มไมล์มาตรฐาน)"""
    confirm = messagebox.askyesno(
        "ยืนยัน", "คุณต้องการคืนค่าโลโก้เดิม (แอนิเมชันเข็มไมล์) หรือไม่?"
    )
    if confirm:
        for name in ["logo.png", "logo.jpg", "logo.jpeg"]:
            if os.path.exists(name):
                try:
                    os.remove(name)
                except Exception:
                    pass
        messagebox.showinfo("SUCCESS", "คืนค่าโลโก้มาตรฐานเรียบร้อยแล้ว!")
        load_garage_logo()


def reset_theme():
    """ฟังก์ชันคืนค่าสีเดิม (Cyberpunk Standard Theme)"""
    global current_theme
    current_theme = THEMES["Cyberpunk (ฟ้า-เข้ม)"].copy()
    apply_theme()
    messagebox.showinfo("SUCCESS", "คืนค่าสีธีมเดิมเรียบร้อยแล้ว!")


def pick_color(key_name, title_name):
    color = colorchooser.askcolor(title=f"เลือก{title_name}")[1]
    if color:
        current_theme[key_name] = color
        apply_theme()


def change_theme_event(theme_name):
    global current_theme
    current_theme = THEMES[theme_name].copy()
    apply_theme()


def apply_theme():
    bg_m = current_theme["BG_MAIN"]
    bg_c = current_theme["CARD_BG"]
    cyan = current_theme["ACCENT_CYAN"]
    border = current_theme["BORDER_COLOR"]
    entry_bg = current_theme["ENTRY_BG"]

    root.configure(bg=bg_m)
    header_frame.configure(bg="#020617")
    middle_container.configure(bg=bg_m)

    card_form_bg.set_colors(bg_c, border)
    card_logo_bg.set_colors(bg_c, border)
    card_table_bg.set_colors(bg_c, border)

    frame_form.configure(bg=bg_c)
    btn_frame.configure(bg=bg_c)
    search_frame.configure(bg=bg_c)
    table_container.configure(bg=bg_c)

    lbl_title.config(fg=cyan)
    form_title_lbl.config(fg=cyan, bg=bg_c)
    table_title_lbl.config(fg=cyan, bg=bg_c)

    # Style Treeview
    style.configure(
        "Treeview",
        background=entry_bg,
        foreground="#e2e8f0",
        fieldbackground=entry_bg,
    )
    style.configure("Treeview.Heading", background=border, foreground=cyan)

    load_garage_logo()


def open_settings_window():
    win = tk.Toplevel(root)
    win.title("⚙️ ตั้งค่าระบบ (SYSTEM SETTINGS)")
    win.geometry("400x440")
    win.configure(bg=current_theme["CARD_BG"])
    win.resizable(False, False)
    win.grab_set()

    tk.Label(
        win,
        text="⚙️ ตั้งค่าและปรับแต่งระบบ",
        font=("Segoe UI", 11, "bold"),
        fg=current_theme["ACCENT_CYAN"],
        bg=current_theme["CARD_BG"],
    ).pack(pady=10)

    # Zone Preset Theme
    frame_theme = tk.Frame(win, bg=current_theme["CARD_BG"])
    frame_theme.pack(fill="x", padx=20, pady=5)

    tk.Label(
        frame_theme,
        text="🎨 เลือกธีมสำเร็จรูป:",
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=current_theme["CARD_BG"],
    ).pack(anchor="w")

    combo_theme = ttk.Combobox(
        frame_theme,
        values=list(THEMES.keys()),
        state="readonly",
        font=("Segoe UI", 9),
    )
    combo_theme.pack(fill="x", pady=4)
    combo_theme.set("Cyberpunk (ฟ้า-เข้ม)")
    combo_theme.bind(
        "<<ComboboxSelected>>", lambda e: change_theme_event(combo_theme.get())
    )

    # Zone Custom Colors
    frame_custom = tk.Frame(win, bg=current_theme["CARD_BG"])
    frame_custom.pack(fill="x", padx=20, pady=8)

    tk.Label(
        frame_custom,
        text="🖌️ ปรับแต่งสีเอง (Custom Colors):",
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=current_theme["CARD_BG"],
    ).pack(anchor="w", pady=(0, 4))

    custom_btn_box = tk.Frame(frame_custom, bg=current_theme["CARD_BG"])
    custom_btn_box.pack(fill="x")

    ModernRoundedButton(
        custom_btn_box,
        text="สีพื้นหลัง (BG)",
        bg="#334155",
        hover_bg="#475569",
        fg="white",
        command=lambda: pick_color("BG_MAIN", "สีพื้นหลัง"),
        width=110,
        height=26,
    ).pack(side="left", padx=2)

    ModernRoundedButton(
        custom_btn_box,
        text="สีการ์ด (Card)",
        bg="#334155",
        hover_bg="#475569",
        fg="white",
        command=lambda: pick_color("CARD_BG", "สีการ์ด"),
        width=110,
        height=26,
    ).pack(side="left", padx=2)

    ModernRoundedButton(
        custom_btn_box,
        text="สีไฮไลต์ (Accent)",
        bg="#0284c7",
        hover_bg="#38bdf8",
        fg="white",
        command=lambda: pick_color("ACCENT_CYAN", "สีไฮไลต์"),
        width=110,
        height=26,
    ).pack(side="left", padx=2)

    # ปุ่มคืนค่าสีเดิม
    frame_reset_color = tk.Frame(win, bg=current_theme["CARD_BG"])
    frame_reset_color.pack(fill="x", padx=20, pady=(2, 8))

    ModernRoundedButton(
        frame_reset_color,
        text="🔄 คืนค่าสีเดิม",
        bg="#eab308",
        hover_bg="#fde047",
        fg="#020617",
        command=reset_theme,
        width=345,
        height=26,
    ).pack(fill="x")

    # Zone Logo
    frame_logo = tk.Frame(win, bg=current_theme["CARD_BG"])
    frame_logo.pack(fill="x", padx=20, pady=8)

    tk.Label(
        frame_logo,
        text="🖼️ จัดการโลโก้อู่/ร้าน:",
        font=("Segoe UI", 9, "bold"),
        fg="white",
        bg=current_theme["CARD_BG"],
    ).pack(anchor="w", pady=(0, 6))

    logo_btn_box = tk.Frame(frame_logo, bg=current_theme["CARD_BG"])
    logo_btn_box.pack(fill="x")

    btn_up = ModernRoundedButton(
        logo_btn_box,
        text="📂 เปลี่ยนโลโก้",
        bg="#059669",
        hover_bg="#10b981",
        fg="white",
        command=lambda: [upload_logo(), win.destroy()],
        width=165,
        height=35,
    )
    btn_up.pack(side="left", padx=(0, 5))

    btn_del = ModernRoundedButton(
        logo_btn_box,
        text="🔄 คืนค่าโลโก้เดิม",
        bg="#dc2626",
        hover_bg="#f43f5e",
        fg="white",
        command=lambda: [reset_logo(), win.destroy()],
        width=165,
        height=35,
    )
    btn_del.pack(side="left")


# ----------------------------------------------------
# 8. หน้าตาโปรแกรมหลัก (Cyberpunk Main Window Interface)
# ----------------------------------------------------
root = tk.Tk()
root.title(f"🏎️ ECU REMAP TUNING PERFORMANCE SYSTEM - VERSION -{APP_VERSION}")

window_width = 1260
window_height = 660
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width / 2) - (window_width / 2))
center_y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

root.configure(bg=current_theme["BG_MAIN"])

# Treeview Style
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#020617",
    foreground="#e2e8f0",
    fieldbackground="#020617",
    rowheight=26,
    font=("Segoe UI", 9),
    borderwidth=0,
)
style.configure(
    "Treeview.Heading",
    background="#1e293b",
    foreground=current_theme["ACCENT_CYAN"],
    font=("Segoe UI", 9, "bold"),
    relief="flat",
)
style.map("Treeview", background=[("selected", "#0284c7")])

# ----------------- UI Layout -----------------

# 1. Header Bar
header_frame = tk.Frame(root, bg="#020617", height=50)
header_frame.pack(fill="x")

lbl_title = tk.Label(
    header_frame,
    text="⚡ ECU REMAP PERFORMANCE DATA CENTER",
    font=("Segoe UI", 13, "bold"),
    fg=current_theme["ACCENT_CYAN"],
    bg="#020617",
)
lbl_title.pack(side="left", padx=15, pady=8)

lbl_status = tk.Label(
    header_frame,
    text="CONNECTING...",
    font=("Consolas", 9, "bold"),
    fg="#64748b",
    bg="#020617",
)
lbl_status.pack(side="left", padx=10, pady=8)

# ปุ่มตั้งค่าด้านบนขวา
btn_settings = ModernRoundedButton(
    header_frame,
    text="⚙️ ตั้งค่าระบบ",
    bg="#334155",
    hover_bg="#475569",
    fg="white",
    command=open_settings_window,
    width=90,
    height=26,
    radius=6,
)
btn_settings.pack(side="right", padx=15, pady=8)

# KPI Cards ขอบมนบน Header
kpi_frame = tk.Frame(header_frame, bg="#020617")
kpi_frame.pack(side="right", padx=10, pady=4)

kpi_card1 = RoundedCanvasCard(
    kpi_frame,
    bg_color="#0f172a",
    border_color="#334155",
    radius=8,
    width=110,
    height=40,
)
kpi_card1.pack(side="left", padx=4)

lbl_k1_title = tk.Label(
    kpi_card1,
    text="TOTAL TUNED",
    font=("Segoe UI", 7, "bold"),
    fg="#64748b",
    bg="#0f172a",
)
lbl_k1_title.place(relx=0.5, rely=0.25, anchor="center")
lbl_kpi_count = tk.Label(
    kpi_card1,
    text="0 คัน",
    font=("Consolas", 10, "bold"),
    fg=current_theme["ACCENT_CYAN"],
    bg="#0f172a",
)
lbl_kpi_count.place(relx=0.5, rely=0.70, anchor="center")

kpi_card2 = RoundedCanvasCard(
    kpi_frame,
    bg_color="#0f172a",
    border_color="#334155",
    radius=8,
    width=120,
    height=40,
)
kpi_card2.pack(side="left", padx=4)

lbl_k2_title = tk.Label(
    kpi_card2,
    text="TOTAL REVENUE",
    font=("Segoe UI", 7, "bold"),
    fg="#64748b",
    bg="#0f172a",
)
lbl_k2_title.place(relx=0.5, rely=0.25, anchor="center")
lbl_kpi_revenue = tk.Label(
    kpi_card2,
    text="฿ 0.00",
    font=("Consolas", 10, "bold"),
    fg="#10b981",
    bg="#0f172a",
)
lbl_kpi_revenue.place(relx=0.5, rely=0.70, anchor="center")

# 2. Main Middle Container
middle_container = tk.Frame(root, bg=current_theme["BG_MAIN"])
middle_container.pack(fill="x", padx=12, pady=6)

# 2.1 Left Form Canvas Card
card_form_bg = RoundedCanvasCard(
    middle_container,
    bg_color=current_theme["CARD_BG"],
    border_color=current_theme["BORDER_COLOR"],
    radius=14,
    height=220,
)
card_form_bg.pack(side="left", fill="both", expand=True, padx=(0, 8))

form_title_lbl = tk.Label(
    card_form_bg,
    text="🛠️ กรอกข้อมูลรถและประวัติการจูน",
    font=("Segoe UI", 10, "bold"),
    fg=current_theme["ACCENT_CYAN"],
    bg=current_theme["CARD_BG"],
)
form_title_lbl.place(x=15, y=6)

frame_form = tk.Frame(card_form_bg, bg=current_theme["CARD_BG"])
frame_form.place(x=10, y=30, relwidth=0.98, relheight=0.83)

frame_form.columnconfigure(1, weight=1)
frame_form.columnconfigure(3, weight=1)
frame_form.columnconfigure(5, weight=1)

label_options = {
    "bg": current_theme["CARD_BG"],
    "fg": "#94a3b8",
    "font": ("Segoe UI", 8, "bold"),
}
entry_options = {
    "bg": current_theme["ENTRY_BG"],
    "fg": "white",
    "insertbackground": current_theme["ACCENT_CYAN"],
    "relief": "flat",
    "highlightthickness": 1,
    "highlightbackground": "#1e293b",
    "highlightcolor": current_theme["ACCENT_CYAN"],
    "font": ("Consolas", 9),
}

# Row 0
tk.Label(frame_form, text="วันที่บันทึก:", **label_options).grid(
    row=0, column=0, sticky="e", pady=2, padx=2
)
entry_date = tk.Entry(frame_form, **entry_options)
entry_date.grid(row=0, column=1, sticky="ew", pady=2)
entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

tk.Label(frame_form, text="ชื่อลูกค้า:", **label_options).grid(
    row=0, column=2, sticky="e", pady=2, padx=2
)
entry_name = tk.Entry(frame_form, **entry_options)
entry_name.grid(row=0, column=3, sticky="ew", pady=2)

tk.Label(frame_form, text="เบอร์/FB/IG:", **label_options).grid(
    row=0, column=4, sticky="e", pady=2, padx=2
)
entry_phone = tk.Entry(frame_form, **entry_options)
entry_phone.grid(row=0, column=5, sticky="ew", pady=2)

# Row 1
tk.Label(frame_form, text="รุ่นรถ:", **label_options).grid(
    row=1, column=0, sticky="e", pady=2, padx=2
)
entry_brand = tk.Entry(frame_form, **entry_options)
entry_brand.grid(row=1, column=1, sticky="ew", pady=2)

tk.Label(frame_form, text="ปี:", **label_options).grid(
    row=1, column=2, sticky="e", pady=2, padx=2
)
entry_model = tk.Entry(frame_form, **entry_options)
entry_model.grid(row=1, column=3, sticky="ew", pady=2)

tk.Label(frame_form, text="สเปกเครื่อง:", **label_options).grid(
    row=1, column=4, sticky="e", pady=2, padx=2
)
entry_engine = tk.Entry(frame_form, **entry_options)
entry_engine.grid(row=1, column=5, sticky="ew", pady=2)

# Row 2
tk.Label(frame_form, text="ทะเบียนรถ:", **label_options).grid(
    row=2, column=0, sticky="e", pady=2, padx=2
)
entry_plate = tk.Entry(frame_form, **entry_options)
entry_plate.grid(row=2, column=1, sticky="ew", pady=2)

tk.Label(frame_form, text="ID ECU:", **label_options).grid(
    row=2, column=2, sticky="e", pady=2, padx=2
)
entry_ecu = tk.Entry(frame_form, **entry_options)
entry_ecu.grid(row=2, column=3, sticky="ew", pady=2)

tk.Label(frame_form, text="จูนสเต็ป:", **label_options).grid(
    row=2, column=4, sticky="e", pady=2, padx=2
)
combo_stage = ttk.Combobox(
    frame_form,
    values=[
        "รถเดิม/ข้างโอเพ่น",
        "รถทำเครื่องมาแล้ว/เต็มระบบ",
        "จูนแก้",
        "จูนหอบ/เดินหอบ",
        "ปลดรอบ",
        "จูนยิง/ผ่อนยิง/ไฟออกท่อ",
        "แก้เบาดับ/แก้รอบสวิง",
        "ลบโค้ด/ปรับจูนเพิ่ม",
        "คืนค่าไฟล์เดิมโรงงาน",
    ],
    state="readonly",
    font=("Segoe UI", 8),
)
combo_stage.current(0)
combo_stage.grid(row=2, column=5, sticky="ew", pady=2)

# Row 3 - Price & Files
tk.Label(frame_form, text="ค่าบริการ (บาท):", **label_options).grid(
    row=3, column=0, sticky="e", pady=2, padx=2
)
entry_price = tk.Entry(frame_form, **entry_options)
entry_price.grid(row=3, column=1, sticky="ew", pady=2)

tk.Label(frame_form, text="ไฟล์ Bin แนบ:", **label_options).grid(
    row=3, column=2, sticky="e", pady=2, padx=2
)
entry_bin_file = tk.Entry(frame_form, state="readonly", **entry_options)
entry_bin_file.grid(row=3, column=3, sticky="ew", pady=2)

btn_attach_bin = ModernRoundedButton(
    frame_form,
    text="📁 แนบ Bin",
    bg="#334155",
    hover_bg="#475569",
    fg="white",
    command=select_bin_file,
    width=75,
    height=22,
    radius=6,
)
btn_attach_bin.grid(row=3, column=3, sticky="e", padx=3)

tk.Label(frame_form, text="ไฟล์ XDF แนบ:", **label_options).grid(
    row=3, column=4, sticky="e", pady=2, padx=2
)
entry_xdf_file = tk.Entry(frame_form, state="readonly", **entry_options)
entry_xdf_file.grid(row=3, column=5, sticky="ew", pady=2)

btn_attach_xdf = ModernRoundedButton(
    frame_form,
    text="📁 แนบ XDF",
    bg="#0284c7",
    hover_bg="#38bdf8",
    fg="white",
    command=select_xdf_file,
    width=75,
    height=22,
    radius=6,
)
btn_attach_xdf.grid(row=3, column=5, sticky="e", padx=3)

# Row 4 - Note
tk.Label(frame_form, text="หมายเหตุ:", **label_options).grid(
    row=4, column=0, sticky="ne", pady=2, padx=2
)
text_note = tk.Text(
    frame_form,
    height=2,
    bg=current_theme["ENTRY_BG"],
    fg="white",
    insertbackground=current_theme["ACCENT_CYAN"],
    relief="flat",
    highlightthickness=1,
    highlightbackground="#1e293b",
    highlightcolor=current_theme["ACCENT_CYAN"],
    font=("Segoe UI", 8),
)
text_note.grid(row=4, column=1, columnspan=5, sticky="ew", pady=2)

# Control Buttons - Row 5
btn_frame = tk.Frame(frame_form, bg=current_theme["CARD_BG"])
btn_frame.grid(row=5, column=0, columnspan=6, sticky="e", pady=(4, 0))

btn_clear = ModernRoundedButton(
    btn_frame,
    text="🧹 ล้างฟอร์ม",
    bg="#334155",
    hover_bg="#475569",
    fg="white",
    command=clear_fields,
    width=85,
    height=26,
    radius=8,
)
btn_clear.pack(side="left", padx=3)

btn_refresh = ModernRoundedButton(
    btn_frame,
    text="🔄 รีเฟรช",
    bg="#0284c7",
    hover_bg="#38bdf8",
    fg="white",
    command=load_table_data,
    width=85,
    height=26,
    radius=8,
)
btn_refresh.pack(side="left", padx=3)

btn_save = ModernRoundedButton(
    btn_frame,
    text="💾 บันทึกข้อมูล",
    bg="#059669",
    hover_bg="#10b981",
    fg="white",
    command=save_customer,
    width=100,
    height=26,
    radius=8,
)
btn_save.pack(side="left", padx=3)

# 2.2 Right LOGO Banner Card
card_logo_bg = RoundedCanvasCard(
    middle_container,
    bg_color=current_theme["CARD_BG"],
    border_color=current_theme["BORDER_COLOR"],
    radius=14,
    width=310,
    height=220,
)
card_logo_bg.pack(side="right", fill="both", expand=False)
card_logo_bg.pack_propagate(False)

gauge_angle = 0
anim_timer = None


def animate_speedometer(canvas):
    global gauge_angle, anim_timer

    if not canvas.winfo_exists():
        return

    canvas.delete("gauge_needle")
    gauge_angle = (gauge_angle + 0.05) % (math.pi * 2)

    angle = math.radians(-135 + (math.sin(gauge_angle) + 1) * 135)
    cx, cy, r = 145, 80, 42
    nx = cx + r * math.cos(angle)
    ny = cy + r * math.sin(angle)

    canvas.create_line(
        cx,
        cy,
        nx,
        ny,
        fill="#f43f5e",
        width=3,
        tags="gauge_needle",
        capstyle=tk.ROUND,
    )
    canvas.create_oval(
        cx - 5,
        cy - 5,
        cx + 5,
        cy + 5,
        fill=current_theme["ACCENT_CYAN"],
        outline="",
        tags="gauge_needle",
    )

    anim_timer = root.after(50, lambda: animate_speedometer(canvas))


def load_garage_logo():
    global lbl_img_global, anim_timer

    if anim_timer is not None:
        root.after_cancel(anim_timer)
        anim_timer = None

    for widget in card_logo_bg.winfo_children():
        widget.destroy()

    logo_filename = None
    for name in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(name):
            logo_filename = name
            break

    if logo_filename:
        try:
            img = Image.open(logo_filename)
            img = img.resize((290, 190), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl_img_global = tk.Label(
                card_logo_bg, image=photo, bg=current_theme["CARD_BG"]
            )
            lbl_img_global.image = photo
            lbl_img_global.place(relx=0.5, rely=0.5, anchor="center")
            return
        except Exception:
            pass

    banner_canvas = tk.Canvas(
        card_logo_bg, bg=current_theme["ENTRY_BG"], highlightthickness=0
    )
    banner_canvas.place(x=10, y=10, width=290, height=200)

    for i in range(0, 290, 20):
        banner_canvas.create_line(i, 0, i, 200, fill="#0f172a", width=1)
    for j in range(0, 200, 20):
        banner_canvas.create_line(0, j, 290, j, fill="#0f172a", width=1)

    banner_canvas.create_arc(
        145 - 55,
        80 - 55,
        145 + 55,
        80 + 55,
        start=-45,
        extent=270,
        style=tk.ARC,
        outline="#1e293b",
        width=6,
    )
    banner_canvas.create_arc(
        145 - 55,
        80 - 55,
        145 + 55,
        80 + 55,
        start=30,
        extent=180,
        style=tk.ARC,
        outline=current_theme["ACCENT_CYAN"],
        width=6,
    )

    banner_canvas.create_text(
        145,
        142,
        text="🏎️ TUNING SHOP",
        fill=current_theme["ACCENT_CYAN"],
        font=("Segoe UI", 11, "bold"),
    )
    banner_canvas.create_text(
        145,
        162,
        text="ECU REMAP DATA CENTER",
        fill="#64748b",
        font=("Consolas", 7, "bold"),
    )

    animate_speedometer(banner_canvas)


load_garage_logo()

# 3. Table Canvas Card
card_table_bg = RoundedCanvasCard(
    root,
    bg_color=current_theme["CARD_BG"],
    border_color=current_theme["BORDER_COLOR"],
    radius=14,
)
card_table_bg.pack(fill="both", expand=True, padx=12, pady=(0, 10))

table_title_lbl = tk.Label(
    card_table_bg,
    text="📋 ประวัติการบริการลูกค้า (Double-Click เพื่อดึงข้อมูลลงฟอร์มและแก้ไข)",
    font=("Segoe UI", 10, "bold"),
    fg=current_theme["ACCENT_CYAN"],
    bg=current_theme["CARD_BG"],
)
table_title_lbl.place(x=15, y=6)

search_frame = tk.Frame(card_table_bg, bg=current_theme["CARD_BG"])
search_frame.place(x=15, y=30, relwidth=0.97)

tk.Label(search_frame, text="🔎 ค้นหาด่วน:", **label_options).pack(
    side="left", padx=(0, 4)
)
entry_search = tk.Entry(search_frame, width=22, **entry_options)
entry_search.pack(side="left", padx=4)
entry_search.bind("<KeyRelease>", on_search)

# ปุ่มสั่งการด้านขวาตาราง
btn_clear_all = ModernRoundedButton(
    search_frame,
    text="💥 ล้างข้อมูลทั้งหมด",
    bg="#7f1d1d",
    hover_bg="#991b1b",
    fg="white",
    command=clear_all_data,
    width=115,
    height=24,
    radius=6,
)
btn_clear_all.pack(side="right", padx=(3, 0))

btn_reset_id = ModernRoundedButton(
    search_frame,
    text="🔢 Reset ID",
    bg="#d97706",
    hover_bg="#f59e0b",
    fg="white",
    command=reset_database_id,
    width=80,
    height=24,
    radius=6,
)
btn_reset_id.pack(side="right", padx=(3, 0))

btn_delete = ModernRoundedButton(
    search_frame,
    text="🗑️ ลบรายการ",
    bg="#dc2626",
    hover_bg="#f43f5e",
    fg="white",
    command=delete_selected_customer,
    width=90,
    height=24,
    radius=6,
)
btn_delete.pack(side="right", padx=(3, 0))

btn_download_bin = ModernRoundedButton(
    search_frame,
    text="💾 โหลด Bin",
    bg="#059669",
    hover_bg="#10b981",
    fg="white",
    command=download_selected_bin,
    width=100,
    height=24,
    radius=6,
)
btn_download_bin.pack(side="right", padx=(3, 0))

btn_download_xdf = ModernRoundedButton(
    search_frame,
    text="🗺️ โหลด XDF",
    bg="#0284c7",
    hover_bg="#38bdf8",
    fg="white",
    command=download_selected_xdf,
    width=100,
    height=24,
    radius=6,
)
btn_download_xdf.pack(side="right", padx=(3, 0))

# Table Container
table_container = tk.Frame(card_table_bg, bg=current_theme["CARD_BG"])
table_container.place(x=15, y=60, relwidth=0.97, relheight=0.78)

columns = (
    "ID",
    "วันที่",
    "ชื่อลูกค้า",
    "เบอร์โทร/FB/IG",
    "รุ่นรถ",
    "ปี",
    "สเปกเครื่อง",
    "ทะเบียน",
    "ID ECU",
    "จูนสเต็ป",
    "ราคา",
    "หมายเหตุ",
    "ไฟล์ Bin",
    "ไฟล์ XDF",
)
tree = ttk.Treeview(table_container, columns=columns, show="headings")

tree.tag_configure("evenrow", background="#070a12")
tree.tag_configure("oddrow", background="#0b1329")

col_widths = {
    "ID": 35,
    "วันที่": 80,
    "ชื่อลูกค้า": 110,
    "เบอร์โทร/FB/IG": 100,
    "รุ่นรถ": 70,
    "ปี": 80,
    "สเปกเครื่อง": 90,
    "ทะเบียน": 75,
    "ID ECU": 80,
    "จูนสเต็ป": 110,
    "ราคา": 75,
    "หมายเหตุ": 120,
    "ไฟล์ Bin": 95,
    "ไฟล์ XDF": 95,
}

for col in columns:
    tree.heading(col, text=col)
    tree.column(
        col,
        width=col_widths.get(col, 85),
        anchor="center"
        if col not in ["หมายเหตุ", "ไฟล์ Bin", "ไฟล์ XDF"]
        else "w",
    )

tree.bind("<Double-1>", on_tree_double_click)

scrollbar = ttk.Scrollbar(
    table_container, orient="vertical", command=tree.yview
)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

# เริ่มต้นระบบ
load_table_data()
toggle_pulse_status()

root.mainloop()
