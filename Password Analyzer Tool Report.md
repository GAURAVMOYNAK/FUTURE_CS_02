# Password Analyzer Tool: Algorithm and Effectiveness Report

## 1. Introduction
The Password Analyzer Tool is designed to assess the strength of user-provided passwords and provide feedback on their security. It employs various criteria—including length, character diversity, and checks against common weak passwords—to determine the robustness of a password. While an entropy-based approach is often used to quantify password strength mathematically, this tool uses a rule-based scoring system.

## 2. Algorithm Explanation
The Password Analyzer Tool follows a step-by-step algorithm to evaluate password strength:

### **Step 1: Input Collection**
- The user inputs a password (and optionally a username) for analysis.

### **Step 2: Length Evaluation**
- The password length is checked and categorized:
  - **Weak:** Less than 8 characters
  - **Moderate:** 8–11 characters
  - **Strong:** 12 or more characters

### **Step 3: Character Composition Analysis**
- The password is analyzed for the presence of different character types:
  - **Lowercase letters** (a–z)
  - **Uppercase letters** (A–Z)
  - **Digits** (0–9)
  - **Special characters** (e.g., `!@#$%^&*(),.?":{}|<>`)
- A password that includes a mix of these character types is considered stronger.

### **Step 4: Dictionary Word Check**
- The password is compared against a dictionary of commonly used or weak passwords (e.g., "password", "123456", "qwerty").
- If the password is found in this dictionary, it is immediately flagged as weak.

### **Step 5: Username Inclusion Check**
- If the username (if provided) appears within the password, the password is marked as weak.

### **Step 6: Scoring System**
- Points are assigned based on the criteria above:
  - **Length:** +3 points for 12+ characters, +2 points for 8–11 characters, and insufficient length prompts a suggestion.
  - **Character Diversity:** +2 points each for the presence of both uppercase and lowercase letters, at least one digit, and at least one special character.
- The final score categorizes the password as:
  - **Weak:** 0–2 points
  - **Moderate:** 3–6 points
  - **Strong:** 7 or more points

### **Step 7: Strength Scoring and Feedback**
- Based on the total score, the tool provides feedback, such as:
  - “Your password is weak. Consider adding numbers and special characters.”
  - “Your password is strong. Keep it safe!”
