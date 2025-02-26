# Password Analyzer Tool

**Password Analyzer Tool** is a simple yet powerful password strength analyzer and manager built with Python and Tkinter. It helps you assess the strength of your passwords in real time, securely save and manage them, and control access using a passphrase.

---

## Features

- **Real-Time Analysis:**  
  As you type a password, the application checks its length, mix of uppercase and lowercase letters, numbers, and special characters. It then displays a strength rating along with suggestions for improvement.

- **Encryption & Security:**  
  Passwords are hashed using SHA-256 with your passphrase as a salt. This ensures that even if two users have the same password, their stored hashes will differ.

- **Data Persistence:**  
  - The passphrase is stored in a `passphrase.txt` file.
  - Saved passwords are recorded in a CSV file named `saved_passwords.csv`.

- **User-Friendly Interface:**  
  The application has three main views:
  - **Analyzer:** Evaluate password strength and save passwords.
  - **Manager:** View saved passwords (requires passphrase authentication).
  - **Settings:** Set, change, or delete your passphrase. The Settings view displays a horizontal bar with “Guest1” on the left and icon buttons for account actions on the right.

- **Icons:**  
  External icon images (`change_icon.png` and `delete_icon.png`) are used for a polished look. If these are not found, text buttons are used as a fallback.

---

## How It Works

1. **Password Analysis:**
   - **Criteria:**  
     - **Length:** Minimum of 8 characters (12+ recommended).  
     - **Character Variety:** Must include uppercase, lowercase, digits, and special characters.
   - **Scoring:**  
     Each criterion contributes to a score that categorizes the password as Weak, Moderate, or Strong.
   - **Feedback:**  
     Suggestions are provided to help improve the password’s strength.

2. **Encryption:**
   - The password is concatenated with your passphrase (acting as a salt) and then hashed using SHA-256.
   - This ensures that your password is stored securely and that even if someone accesses the CSV file, they cannot easily retrieve your plaintext password.

3. **Data Storage:**
   - The passphrase is stored in `passphrase.txt`.
   - Saved passwords are stored in `saved_passwords.csv` with columns for the username, plaintext password (for demonstration purposes), and the encrypted version.

4. **Manager & Authentication:**
   - The Manager view requires your passphrase for login.
   - Upon successful login, your saved passwords are displayed.

---

## Usage

### Analyzer View

- **Input:**  
  - Enter a username (optional) and a password.
  - The application analyzes the password in real time and displays its strength, along with suggestions for improvement.
  
- **Action:**  
  - Click **Save Password** to store the password (only if a passphrase is set).

### Manager View

- **Access:**  
  - Click the **Manager** button in the navigation bar.
  
- **Authentication:**  
  - If not already logged in, you will see centered login controls at the bottom.
  - Enter your passphrase and click **Login**.
  
- **Result:**  
  - On successful login, your saved passwords are displayed.

### Settings View

- **Access:**  
  - Click the **⚙** button in the navigation bar.
  
- **If No Passphrase Is Set:**  
  - Enter a passphrase and click **Set Passphrase**.
  
- **If a Passphrase Exists:**  
  - A horizontal bar appears with "Guest1" on the left and icon buttons on the right.
  - **Change Icon:** Click to update your passphrase.
  - **Delete Icon:** Click to remove your passphrase and clear all saved data.

---

## Security Considerations

- **Encryption:**  
  Passwords are securely hashed using SHA-256 along with your passphrase as a salt, making it harder for attackers to reverse-engineer the stored data.

- **Local Storage:**  
  All data is stored locally in text and CSV files. For enhanced security in production, consider using secure databases and additional encryption measures.

- **Passphrase Protection:**  
  Your passphrase is critical for both encryption and authentication. Choose a strong, unique passphrase and keep it confidential.

---

## Installation

### Prerequisites

- **Python 3.x** is required.
- **Tkinter** is bundled with Python (install via your package manager if necessary).

### Setup Steps

1. **Clone or Download:**
   - Clone the repository or download the source code.

2. **Place Icon Files:**
   - Ensure that `change_icon.png` and `delete_icon.png` are in the same directory as `password_analyzer.py`.

3. **(Optional) Weak Passwords File:**
   - Place a `weak_passwords.txt` file in the directory with one weak/common password per line. If not provided, a default set is used.

### Running the Application

Open a terminal in the project directory and run:

```bash
python password_analyzer.py
