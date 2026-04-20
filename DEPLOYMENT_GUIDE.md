# Pharmacy Management System Deployment Guide

This guide explains how to deploy and run the Pharmacy Management System in two modes: **Online/Server** and **Standalone/Desktop**.

---

## 🖥️ Standalone / Desktop Mode (Windows)

Use this mode if you want to run the system on a single laptop/PC without an internet connection.

### First-Time Setup
1.  **Install Python**: Ensure Python 3.12 or newer is installed on your PC. You can download it from [python.org](https://www.python.org/). **Crucial**: During installation, check the box **"Add Python to PATH"**.
2.  **Run Setup**: Double-click the `setup_desktop.bat` file. This will:
    - Create a local environment for the app.
    - Install necessary components.
    - Prepare the database.
    - Ask you to create an administrator account.

### Running the App
1.  Double-click `run_pharmacy.bat`.
2.  The system will start a secure internal server.
3.  Your web browser will automatically open to the dashboard.
4.  **To Stop**: Close the command window or press `Ctrl+C`.

---

## 🌐 Online / Server Deployment

Use this mode to host the system on the internet for multiple users to access.

### Using Docker (Recommended)
The system is ready for Docker-based platforms like Railway, DigitalOcean, or AWS.
1.  **Build the Image**: `docker build -t pharmacy-system .`
2.  **Run with Environment Variables**:
    - `SECRET_KEY`: A random string for security.
    - `ALLOWED_HOSTS`: Set to your domain name.
    - `DATABASE_URL`: (Optional) Connection string for PostgreSQL. Defaults to SQLite.

### Using Render.com
1.  Connect your GitHub repository to Render.
2.  Render will detect the `render.yaml` file and configure everything automatically (Web Service + Database).
3.  Add your environment variables in the Render dashboard.

---

## 📂 Maintenance
- **Backups**: Periodically copy the `db.sqlite3` file to a safe location. This file contains all your data.
- **Updates**: If you receive a new versions of the code, replace the folders but keep your `db.sqlite3` file.
