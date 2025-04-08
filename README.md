# Rosetta Stone

**Author:** James Di Natale  
**Application:** Rosetta Stone – Real-Time Data Translator & Forwarder

---

## 📌 What is Rosetta Stone?

Rosetta Stone is a user-friendly, standalone Windows application that allows you to:

- 🛰️ Capture incoming UDP telemetry or data packets
- 💾 Log data to a local database
- 🔁 Dynamically transform data in real time
- 📤 Forward transformed data via UDP or TCP
- 🧑‍💻 Manually override XML fields before transmission
- 🧾 View messages and errors in a live feed

It’s designed for analysts, operators, and engineers who need to manipulate and route data streams quickly — without writing code.

---

## 🚀 How to Use (No Programming Needed)

### ✅ Requirements

- Windows 10 or later
- No Python installation required
- Just the provided `RosettaStone.exe` and the `assets` folder

---

### 📦 Steps to Launch

1. Locate the provided files:
   ``
   RosettaStone.exe
   /assets/
   ``
2. Double-click `RosettaStone.exe` to launch the program.

---

## 🧭 Key Features

### 🟢 Start Listening

- Set the UDP port you want to listen on
- Begin capturing real-time data

### 🧠 Live Transformation

- View one sample message immediately
- Customize how incoming fields are transformed before sending

### 🧑‍🔧 Manual Override

- Open the **Manual Override** window to edit any XML fields manually
- See a side-by-side preview of raw vs. modified data

### 🔄 Continuous Forwarding

- Choose TCP or UDP output
- Automatically stream transformed packets to another system

### 📝 Logging

- Errors and system messages appear in a scrollable log window
- All data is saved to a local SQLite database

---

## ❓ Troubleshooting

- If the application doesn’t start, ensure your antivirus isn’t blocking it
- Make sure the `assets` folder is next to `RosettaStone.exe`
- For network issues, verify your firewall or port settings

---

## 🛠 Support

Built by James Di Natale. For questions or feedback, reach out directly. 

[Link Text](https://github.com/dino-del/rosseta-stone.git)
