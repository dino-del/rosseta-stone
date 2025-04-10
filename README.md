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
