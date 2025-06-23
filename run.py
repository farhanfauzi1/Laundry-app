from app import app, db
import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ini akan membuat tabel jika belum ada
        print("Database tables created/checked.")
    app.run(debug=True)