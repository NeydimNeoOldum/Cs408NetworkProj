# Cloud File Storage and Publishing System

## CS 408 - Computer Networks - Fall 2024

### Project Overview
This project implements a **Client-Server Cloud File Storage and Publishing System** using **TCP sockets**. The system allows clients to **upload, download, delete, and manage** text files stored on a central server. It features a **Graphical User Interface (GUI)** for both the server and client applications.

---

## Features

### Server
- Handles **multiple simultaneous client connections**.
- Stores uploaded files in a **user-specified directory**.
- Maintains a **persistent file list** (files remain available even after the server restarts).
- Supports **file ownership tracking** and ensures **unique filenames per client**.
- Displays **real-time logs** of all operations in the GUI.
- Prevents **duplicate usernames** during client connections.
- Allows clients to request a **file list** with corresponding owner information.
- Properly handles **disconnections** and ensures no crashes.

### Client
- Connects to the server via **TCP sockets**.
- Allows users to **upload, download, and delete** text files.
- Ensures **unique usernames** while connecting.
- Displays all **server-side error messages and operations** in the GUI.
- Provides **real-time notifications** when a file is downloaded by another user.
- Saves downloaded files to a **user-specified directory**.
- Can **disconnect and reconnect** at any time.
