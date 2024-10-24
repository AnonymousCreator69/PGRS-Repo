import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='SUMIT',
    password='Sumit@280104',
    database='GrievanceSystem'
)
cursor = conn.cursor()

# Function to send email notifications
def send_email(receiver_email, subject, body):
    sender_email = "sc905735@gmail.com"
    sender_password = "#Sumit@01"

# Setup of the MIME
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Body of the email
msg.attach(MIMEText(body, 'plain'))

# Sending the email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
except Exception as e:
    messagebox.showwarning("Error", f"Failed to send email: {str(e)}")

# Function to register a new user
def register():
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    if name and email and password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            send_email(email, "Registration Successful", "Welcome to the Grievance Redressal System.")
        except mysql.connector.Error as err:
            messagebox.showwarning("Error", f"Error: {err}")
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

# Function to authenticate user login
def login():
    email = email_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        messagebox.showinfo("Success", "Login successful!")
        open_grievance_portal(user[0], user[1], email)
    else:
        messagebox.showwarning("Login Error", "Invalid email or password.")

# Function to lodge a grievance
def lodge_grievance(user_id, email):
    grievance = grievance_entry.get("1.0", "end-1c")
    
    if grievance:
        cursor.execute("INSERT INTO grievances (user_id, grievance_text, status) VALUES (%s, %s, %s)", (user_id, grievance, 'Pending'))
        conn.commit()
        messagebox.showinfo("Success", "Grievance lodged successfully!")
        send_email(email, "Grievance Lodged", "Your grievance has been successfully lodged and is pending resolution.")
        grievance_entry.delete("1.0", tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter your grievance.")

# Function for admin to view grievances
def admin_panel():
    admin_password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
    
    if admin_password == "Admin123":
        admin_window = tk.Toplevel()
        admin_window.title("Admin Panel")

        cursor.execute("SELECT grievances.id, users.name, grievances.grievance_text, grievances.status FROM grievances JOIN users ON grievances.user_id = users.id")
        grievances = cursor.fetchall()

        for grievance in grievances:
            grievance_label = tk.Label(admin_window, text=f"Grievance {grievance[0]} by {grievance[1]}: {grievance[2]} (Status: {grievance[3]})")
            grievance_label.pack()

            if grievance[3] == "Pending":
                resolve_button = tk.Button(admin_window, text="Mark as Resolved", command=lambda g=grievance: mark_resolved(g[0], g[1]))
                resolve_button.pack()
    else:
        messagebox.showwarning("Error", "Incorrect Admin Password")

# Function to mark a grievance as resolved
def mark_resolved(grievance_id, user_name):
    cursor.execute("UPDATE grievances SET status = %s WHERE id = %s", ('Resolved', grievance_id))
    conn.commit()
    messagebox.showinfo("Resolved", f"Grievance {grievance_id} marked as resolved.")
    send_email(user_name, "Grievance Resolved", "Your grievance has been resolved.")

# Function to open grievance portal after successful login
def open_grievance_portal(user_id, name, email):
    grievance_window = tk.Toplevel()
    grievance_window.title("Grievance Portal")

    tk.Label(grievance_window, text=f"Welcome, {name}").pack()

    tk.Label(grievance_window, text="Enter your grievance:").pack(pady=(10, 0))
    global grievance_entry
    grievance_entry = tk.Text(grievance_window, width=50, height=5)
    grievance_entry.pack(pady=(0, 10))

    lodge_button = tk.Button(grievance_window, text="Lodge Grievance", command=lambda: lodge_grievance(user_id, email))
    lodge_button.pack()

# Main User Interface
def main_app():
    global name_entry, email_entry, password_entry
    
    root = tk.Tk()
    root.title("Public Grievance Redressal System")

    tk.Label(root, text="Name:").pack(pady=(10, 0))
    name_entry = tk.Entry(root, width=40)
    name_entry.pack(pady=(0, 10))

    tk.Label(root, text="Email:").pack(pady=(10, 0))
    email_entry = tk.Entry(root, width=40)
    email_entry.pack(pady=(0, 10))

    tk.Label(root, text="Password:").pack(pady=(10, 0))
    password_entry = tk.Entry(root, show='*', width=40)
    password_entry.pack(pady=(0, 10))

    register_button = tk.Button(root, text="Register", command=register)
    register_button.pack(pady=(10, 5))

    login_button = tk.Button(root, text="Login", command=login)
    login_button.pack(pady=(0, 10))

    admin_button = tk.Button(root, text="Admin Access", command=admin_panel)
    admin_button.pack(pady=(0, 10))

    root.mainloop()

if __name__ == "__main__":
    main_app()
