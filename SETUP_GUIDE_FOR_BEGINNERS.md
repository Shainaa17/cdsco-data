# 📖 Easy Beginner Setup Guide (No Technical Experience Needed)

Welcome! If someone sent you this project folder as a `.zip` file, this guide is written especially for you. You don't need any coding or programming experience to run this application on your computer.

Just follow these step-by-step instructions.

---

## 🕒 Quick Summary (What You Will Do)
1. **Unzip the folder** to your desktop.
2. **Install Python** on your computer (takes 2 minutes).
3. **Double-click `run_dashboard.bat`** to start the app.
4. The dashboard will automatically open in your web browser!

---

## 📂 Step 1: Unzip the Project Folder

If you downloaded a `.zip` file (like `cdsco-weekly-tracker.zip`):
1. **Right-click** on the `.zip` file.
2. Click **Extract All...** (or "Extract Here").
3. Choose a location on your computer (for example, your **Desktop** or **Documents** folder) and click **Extract**.
4. Open the extracted folder named `cdsco-weekly-tracker`.

> ⚠️ **Important:** Do NOT run files from inside the `.zip` preview. Make sure you extract it first!

---

## 🐍 Step 2: Install Python (One-Time Setup)

If you already have Python installed, you can skip to Step 3. Otherwise:

1. Open your web browser and go to: **[https://www.python.org/downloads/](https://www.python.org/downloads/)**
2. Click the yellow button that says **Download Python 3.x**.
3. Once the installer finishes downloading, double-click it to run it.
4. 🔴 **CRITICAL STEP**: At the very bottom of the installer window, check the box that says:
   > ☑ **Add python.exe to PATH** *(or "Add Python to PATH")*
   *(If you forget this checkbox, the app will not know where to find Python!)*
5. Click **Install Now**.
6. Wait 1-2 minutes until it says **Setup was successful**, then click **Close**.

---

## ⚙️ Step 3: Check the Settings File (`.env`)

Inside the project folder, there is a configuration file named `.env`.

- If the person who sent you this project **already configured the database connection** inside `.env`, you do not need to change anything!
- If you need to connect to a cloud database or your own PostgreSQL database, open `.env` using Notepad and check the following lines:
  - `DATABASE_URL=...` *(Cloud database link)*
  - `GEMINI_API_KEY=...` *(AI key)*
  - `TAVILY_API_KEY=...` *(Search key)*

*(If in doubt, ask the person who provided this folder if `.env` is already configured for you.)*

---

## 🚀 Step 4: Start the Application (One-Click)

1. Open the project folder (`cdsco-weekly-tracker`).
2. Look for the file named **`run_dashboard.bat`**.
3. **Double-click `run_dashboard.bat`**.

### What happens now?
- A black window (command prompt) will open.
- On your first run, it will automatically set up the environment and install necessary components. This might take 1–3 minutes.
- Once ready, your web browser will automatically open with the dashboard:
  👉 **`http://localhost:8501`**

---

## 🖥️ Step 5: Using the Dashboard

Once the page loads in your browser:
- **KPI Cards**: See total drugs, newly added updates, manufacturers, and categories.
- **Filters**: Use the sidebar on the left to filter by drug name, manufacturer, approval category, or formulation type.
- **Excel Download**: Click the **"Download Latest Excel Report"** button to get the styled `.xlsx` spreadsheet on your computer.
- **Live Update**: Clicking **"🔄 Update from CDSCO"** checks the CDSCO portal for newly published drug approvals.

---

## 🛑 How to Stop the Dashboard

When you are done using the tracker:
1. Go back to the black command window.
2. Simply **close the window** (click the `X` button in the top right corner) or press `Ctrl + C` on your keyboard.

The dashboard will stop running. Whenever you want to use it again in the future, just double-click **`run_dashboard.bat`**!

---

## ❓ Frequently Asked Questions & Help

### Q1: The black window says "Python is not recognized as an internal or external command"
**Fix:** You installed Python without checking the **"Add python.exe to PATH"** checkbox.
1. Download Python again from [python.org](https://www.python.org/downloads/).
2. Run the installer and choose **Modify** or **Reinstall**.
3. Make sure to check the box: ☑ **Add python.exe to PATH**.

### Q2: It says "Database connection failed" or "could not connect to server"
**Fix:** The application needs access to PostgreSQL.
- If you are using a cloud database, make sure your computer has an active Internet connection.
- Check with the project owner that the database credentials in the `.env` file are active and up to date.

### Q3: How do I open it if my browser didn't open automatically?
**Fix:** Open Google Chrome, Microsoft Edge, or Safari, and type this address in the top bar:
`http://localhost:8501`

---
*Created for Kraftland Intelligence • CDSCO Weekly Tracker*
