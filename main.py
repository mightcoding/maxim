import sqlite3
from tkinter import *
from tkinter import messagebox

def create_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            user TEXT NOT NULL,
            product_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        products = [
            ('Футболка VLONE', 'Футболки', 120),
            ('Футболка Adidas', 'Футболки', 70),
            ('Шорты BAPE', 'Шорты', 200),
            ('Шорты Corteiz', 'Шорты', 170),
            ('Штаны Chrome hearts', 'Штаны', 2000),
            ('Штаны Nike Tech', 'Штаны', 600),
            ('Nike Dunk Low SE', 'Обувь', 150),
            ('Air Max 95', 'Обувь', 180)
        ]
        c.executemany('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', products)
        conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    db_password = c.fetchone()
    conn.close()
    return db_password and db_password[0] == password

def login_or_register(app):
    def perform_login():
        username = username_var.get()
        password = password_var.get()
        if check_user(username, password):
            messagebox.showinfo("Успех", "Вы успешно вошли в систему!")
            login_window.destroy()
            show_categories(username)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
        
    def perform_register():
        username = username_var.get()
        password = password_var.get()
        if register_user(username, password):
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            login_window.destroy()
            show_categories(username)
        else:
            messagebox.showerror("Ошибка", "Такой пользователь уже существует.")
    
    login_window = Toplevel(app)
    login_window.title("Вход / Регистрация")
    username_var = StringVar()
    password_var = StringVar()
    Label(login_window, text="Имя пользователя:").pack()
    Entry(login_window, textvariable=username_var).pack()
    Label(login_window, text="Пароль:").pack()
    Entry(login_window, textvariable=password_var, show='*').pack()
    Button(login_window, text="Войти", command=perform_login).pack(side=LEFT)
    Button(login_window, text="Регистрация", command=perform_register).pack(side=RIGHT)

def show_categories(user):
    category_window = Toplevel()
    category_window.title("Категории товаров")
    categories = ["Футболки", "Шорты", "Штаны", "Обувь"]
    for category in categories:
        Button(category_window, text=category, command=lambda c=category: show_products(user, c)).pack()
    Button(category_window, text="Посмотреть корзину", command=lambda: view_cart(user)).pack()

def show_products(user, category):
    products_window = Toplevel()
    products_window.title(f"Товары: {category}")
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT id, name, price FROM products WHERE category = ?', (category,))
    products = c.fetchall()
    conn.close()
    for product in products:
        product_frame = Frame(products_window)
        product_frame.pack()
        Label(product_frame, text=f"{product[1]} - {product[2]} $.").pack(side=LEFT)
        Button(product_frame, text="Добавить в корзину", command=lambda p=product[0]: add_to_cart(user, p)).pack(side=RIGHT)

def add_to_cart(user, product_id):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('INSERT INTO cart (user, product_id) VALUES (?, ?)', (user, product_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Товар добавлен в корзину!")

def view_cart(user):
    cart_window = Toplevel()
    cart_window.title("Корзина")
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('SELECT p.id, p.name, p.price FROM products p JOIN cart c ON p.id = c.product_id WHERE c.user = ?', (user,))
    cart_items = c.fetchall()
    conn.close()
    total = 0
    for item in cart_items:
        item_frame = Frame(cart_window)
        item_frame.pack(fill='x', padx=10, pady=5)
        Label(item_frame, text=f"{item[1]} - {item[2]} $.").pack(side=LEFT)
        Button(item_frame, text="Удалить", command=lambda product_id=item[0]: remove_from_cart(user, product_id, cart_window)).pack(side=RIGHT)
        total += item[2]

    Label(cart_window, text=f"Общая сумма: {total} $.").pack(pady=10)
    Button(cart_window, text="Оформить заказ", command=lambda: place_order(user, cart_window)).pack(side=LEFT)
    Button(cart_window, text="Вернуться", command=cart_window.destroy).pack(side=RIGHT)

def remove_from_cart(user, product_id, window):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user = ? AND product_id = ?', (user, product_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", "Товар удален из корзины")
    window.destroy()
    view_cart(user)

def place_order(user, window):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user = ?', (user,))
    conn.commit()
    conn.close()
    window.destroy()
    messagebox.showinfo("Заказ оформлен", "Ваш заказ успешно оформлен!")

def init_gui():
    app = Tk()
    app.title('Магазин одежды')
    login_or_register(app)
    app.mainloop()

create_db()
init_gui()
