# 📌 Jobs Tracker  
**A desktop tool to track and analyze your job applications during an active job search.**

> **Note:**  
> When you upload your project screenshot to the repository, replace the placeholder below with the RAW URL of your image.  
> ```md
> <!-- Replace this line with your image:
> ![Jobs Tracker Screenshot](URL_TO_YOUR_IMAGE)
> -->
> ```

---

## 📖 Overview  
**Jobs Tracker** is a desktop application built in **Python** that helps job seekers keep a detailed record of their job applications. It is designed for people who are unemployed or transitioning careers and want clear **metrics** about their job search: what’s working, what isn’t, and how to improve their strategy.

The tool allows you to register each application, attach a custom CV, track how many days have passed since applying, store salary ranges, and update the status of each opportunity.

---

## ✨ Key Features  
Currently implemented:

- ✔️ Register job applications  
- ✔️ Attach a **custom CV** per application  
- ✔️ Automatic calculation of **days since application**  
- ✔️ Store **salary ranges**  
- ✔️ Manage **application status** (applied, interview, rejected, etc.)  
- ✔️ **Desktop GUI** built with Tkinter  
- ✔️ Local database using **SQLite**  
- ✔️ Dependency validation via `test_setup.py`  

Planned features (not implemented yet):

- ⏳ Job offer scraping  
- ⏳ Dashboard and analytics  
- ⏳ Reminders and alerts  
- ⏳ API integrations (LinkedIn, Indeed, etc.)  
- ⏳ Web App version  

---

## 🛠️ Tech Stack  
- **Python 3.x**  
- **Tkinter** (GUI)  
- **SQLite** (local database)  
- Standard Python libraries  

---

## 📦 Installation  
1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/JobsTracker.git
cd JobsTracker
```

2. (Optional but recommended) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Run the dependency check script:

```bash
python test_setup.py
```

---

## ▶️ Usage  
Once dependencies are validated, launch the application:

```bash
python Jobs_tracker.py
```

This will open the graphical interface where you can:

- Add new job applications  
- Review your application history  
- Update statuses  
- Track basic metrics  
- Attach custom CVs  

---

## 📁 Project Structure  
*(If you want, I can auto-generate this section once you share your current folder tree.)*

---

## 🗺️ Roadmap  
- [ ] Job scraping  
- [ ] Analytics dashboard  
- [ ] Automated reminders  
- [ ] API integrations  
- [ ] Web App version  
- [ ] Advanced export options (CSV/Excel)  

---

## 🤝 Contributing  
Contributions are welcome.  
Feel free to open an **issue** or submit a **pull request**.

---

## 📄 License  
This project is licensed under the **MIT License**.

---

## 🙌 Credits  
Developed by **Roberto Solano** as a personal tool to optimize and measure the job search process.
