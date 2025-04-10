# Rosetta Stone

Rosetta Stone is a PySide6-powered GUI application designed for receiving, transforming, and forwarding XML telemetry data over UDP. It provides tools to override fields manually or define custom transformation templates for various formats including Simdis XML, Cursor-on-Target XML, JSON, and raw XML.

---

## 🚀 How to Use (Executable)

### 🖥️ Main Interface Overview

| **Button**              | **Function**                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------------|
| **Start Listening**     | Begins listening for incoming UDP messages on the specified port.                             |
| **Stop**                | Stops the listener and disables automatic processing.                                          |
| **Send Message**        | Sends the latest transformed message to the configured destination using TCP/UDP.             |
| **Start Auto-Forwarding / Pause Auto-Forwarding** | Toggles continuous forwarding of received packets after transformation.                  |
| **Manual Override**     | Opens an XML editor where users can adjust the contents of the incoming XML before transform. |
| **Custom Template Builder** | (If enabled) Allows crafting a transformation template from historical packet data.          |
| **About**               | Shows information about the application, version, author, and legal disclaimers.              |

### 📡 Network Settings

- **UDP Listen Port**: Set which port the app will listen to for incoming data.
- **Dest IP / Dest Port**: The destination address where transformed data will be forwarded.
- **Send Protocol**: Choose between TCP and UDP for sending transformed messages.

### 🧭 Output Format

Choose how the incoming XML gets transformed:
- `Simdis XML`
- `CoT XML`
- `JSON`
- `Raw XML` (no transformation)

### ✏️ Manual Overrides

Use the fields for UID, Lat, Lon, and Alt to override corresponding values in the transformation process.

---

## 🧰 Code Explanation

---

### 🗂️ File Structure

```
backend/
│
├── listener.py       # UDP listener for receiving packets
├── forwarder.py      # Sends data over TCP/UDP
├── transform.py      # Converts XML into different formats
├── database.py       # SQLite interaction for packet storage
├── logger.py         # Logs transformation and system errors
├── models.py         # Defines data models for packets and overrides

gui/
│
├── main_window.py           # Primary user interface
├── manual_override_window.py # Manual override editor with XML highlighting
├── about_window.py          # About dialog
```

---

### 🧠 How It Works

#### 🔄 main.py

Starts a PySide6 `QApplication` and shows the `MainWindow`.

#### 🧩 main_window.py

- Connects to the `UDPListener` and receives telemetry messages.
- Allows user configuration for override fields and transformation output.
- Displays:
  - Raw incoming XML.
  - Transformed output.
  - Message logs and status updates.
- Forwards data via the `Forwarder` to a user-defined IP and port using either TCP or UDP.
- Supports optional manual XML override and real-time forwarding.

#### 📥 listener.py

Listens for UDP traffic on the specified port in a background thread and emits the received XML, IP, and timestamp to the main window.

#### 🚚 forwarder.py

Handles outgoing transmission via:
- **TCP**: Re-uses a persistent connection.
- **UDP**: Creates a socket per message and sends datagrams.

#### 🧬 transform.py

Supports transformations from standard `<event>`-style XML into:
- Simdis-compatible `<simdis>` format
- Cursor-on-Target (CoT) XML
- JSON
- Or outputs raw XML directly

Overrides are inserted at transformation time if specified.

#### 🗃️ database.py

Initializes a SQLite database (`udp_data_log.db`) and supports inserting or updating packet logs:
- Stores IP, port, raw XML, and timestamps.

#### 📝 manual_override_window.py

A PySide6 dialog that presents:
- **Left Pane**: Incoming XML (read-only)
- **Right Pane**: Editable override
- Includes real-time syntax highlighting and XML validation before saving.

#### 🧾 about_window.py

Simple "About" dialog with title, version, legal disclaimers, and developer information.

---

### 🧪 Requirements

- Python 3.8+
- PySide6
- (Optional) PyInstaller for packaging as `.exe`

---

## 🛠 Developer Notes

- Missing modules for cross-platform builds are logged in `warn-RosettaStone.txt`
- All transformation errors are written to `udp_data_errors.log`

---

## 📎 License

This software is provided "as is" with no warranty.  
© 2025 James Di Natale
