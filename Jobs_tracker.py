import customtkinter as tk
import sqlite3
from datetime import datetime
import webbrowser
import os
import tkinter.messagebox
import tkinter.filedialog
import csv

class JobTracker:
    def __init__(self):
        # Set appearance mode and color theme
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        # Initialize database
        self.db = sqlite3.connect('job_tracker.db')
        self.create_table()
        
        # Create main window
        self.root = tk.CTk()
        self.root.title("Job Application Tracker")
        self.root.geometry("1200x700")
        
        # Create GUI
        self.create_widgets()
        self.refresh_applications()
        
    def create_table(self):
        """Create the applications table if it doesn't exist"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT NOT NULL,
                url TEXT,
                company TEXT NOT NULL,
                date_applied TEXT NOT NULL,
                salary TEXT,
                status TEXT NOT NULL,
                recruiter_dm TEXT,
                team_member_dm TEXT,
                hiring_manager_dm TEXT,
                priority TEXT DEFAULT 'Medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add priority column if it doesn't exist (for existing databases)
        cursor.execute("PRAGMA table_info(applications)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE applications ADD COLUMN priority TEXT DEFAULT 'Medium'")
        self.db.commit()
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        self.main_frame = tk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.CTkLabel(self.main_frame, text="Job Application Tracker", 
                                font=("Arial", 24, "bold"))
        title_label.pack(pady=10)
        
        # Applications list panel
        self.list_frame = tk.CTkFrame(self.main_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # List title and controls
        list_header = tk.CTkFrame(self.list_frame)
        list_header.pack(fill=tk.X, padx=10, pady=5)
        
        list_title = tk.CTkLabel(list_header, text="Applications", 
                               font=("Arial", 16, "bold"))
        list_title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Add New Application button
        add_btn = tk.CTkButton(list_header, text="Add New Application", 
                              command=self.open_add_dialog)
        add_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Export to CSV button
        export_btn = tk.CTkButton(list_header, text="Export CSV", 
                                 command=self.export_to_csv)
        export_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Search and filter controls
        controls_frame = tk.CTkFrame(list_header)
        controls_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.search_entry = tk.CTkEntry(controls_frame, placeholder_text="Search...")
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.CTkButton(controls_frame, text="Search", 
                                command=self.search_applications, width=80)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        status_filter = tk.CTkComboBox(controls_frame, values=["All", "Applied", 
                                     "Interview Scheduled", "Interviewed", 
                                     "Offer Received", "Rejected", "Withdrawn"])
        status_filter.pack(side=tk.LEFT, padx=5)
        status_filter.set("All")
        
        sort_label = tk.CTkLabel(controls_frame, text="Sort by:")
        sort_label.pack(side=tk.LEFT, padx=5)
        
        self.sort_combo = tk.CTkComboBox(controls_frame, values=["Date Applied", "Priority"])
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.set("Date Applied")
        self.sort_combo.configure(command=lambda value: self.refresh_applications())
        
        # Applications list
        self.create_applications_list()
        
        # Status update panel
        self.create_status_panel()
        
        # Stats label
        self.stats_label = tk.CTkLabel(self.list_frame, text="", font=("Arial", 12))
        self.stats_label.pack(pady=(5, 10))
    
    def open_add_dialog(self):
        """Open dialog for adding new application"""
        # Create dialog window
        dialog = tk.CTkToplevel(self.root)
        dialog.title("Add New Application")
        dialog.geometry("400x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form title
        title_label = tk.CTkLabel(dialog, text="Add New Application", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Scrollable frame for form
        scroll_frame = tk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Job Name
        tk.CTkLabel(scroll_frame, text="Job Title:").pack(anchor="w", pady=(10, 0))
        job_name_entry = tk.CTkEntry(scroll_frame, width=350)
        job_name_entry.pack(pady=(0, 10))
        
        # Company
        tk.CTkLabel(scroll_frame, text="Company:").pack(anchor="w", pady=(10, 0))
        company_entry = tk.CTkEntry(scroll_frame, width=350)
        company_entry.pack(pady=(0, 10))
        
        # Job URL
        tk.CTkLabel(scroll_frame, text="Job URL:").pack(anchor="w", pady=(10, 0))
        url_frame = tk.CTkFrame(scroll_frame)
        url_frame.pack(pady=(0, 10))
        
        url_entry = tk.CTkEntry(url_frame, width=300)
        url_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        open_url_btn = tk.CTkButton(url_frame, text="Open", width=40, 
                                   command=lambda: self.open_job_url(url_entry.get()))
        open_url_btn.pack(side=tk.RIGHT)
        
        # Date Applied
        tk.CTkLabel(scroll_frame, text="Date Applied:").pack(anchor="w", pady=(10, 0))
        date_entry = tk.CTkEntry(scroll_frame, width=350, 
                                placeholder_text="YYYY-MM-DD or 'today'")
        date_entry.pack(pady=(0, 10))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Salary
        tk.CTkLabel(scroll_frame, text="Salary:").pack(anchor="w", pady=(10, 0))
        salary_entry = tk.CTkEntry(scroll_frame, width=350, 
                                  placeholder_text="e.g., $80,000 - $100,000")
        salary_entry.pack(pady=(0, 10))
        
        # Status
        tk.CTkLabel(scroll_frame, text="Status:").pack(anchor="w", pady=(10, 0))
        status_combo = tk.CTkComboBox(scroll_frame, width=350,
                                     values=["Pending","Applied", "Interview Scheduled", 
                                           "Interviewed", "Offer Received", 
                                           "Rejected", "Withdrawn"])
        status_combo.pack(pady=(0, 10))
        status_combo.set("Pending")
        
        # Recruiter DM
        tk.CTkLabel(scroll_frame, text="Recruiter Contact:").pack(anchor="w", pady=(10, 0))
        recruiter_entry = tk.CTkEntry(scroll_frame, width=350, 
                                     placeholder_text="Email, LinkedIn, phone...")
        recruiter_entry.pack(pady=(0, 10))
        
        # Team Member DM
        tk.CTkLabel(scroll_frame, text="Team Member Contact:").pack(anchor="w", pady=(10, 0))
        team_entry = tk.CTkEntry(scroll_frame, width=350, 
                                placeholder_text="Email, LinkedIn, phone...")
        team_entry.pack(pady=(0, 10))
        
        # Hiring Manager DM
        tk.CTkLabel(scroll_frame, text="Hiring Manager Contact:").pack(anchor="w", pady=(10, 0))
        hiring_manager_entry = tk.CTkEntry(scroll_frame, width=350,
                                          placeholder_text="Email, LinkedIn, phone...")
        hiring_manager_entry.pack(pady=(0, 10))
        
        # Priority
        tk.CTkLabel(scroll_frame, text="Priority:").pack(anchor="w", pady=(10, 0))
        priority_combo = tk.CTkComboBox(scroll_frame, width=350,
                                       values=["Low", "Medium", "High"])
        priority_combo.pack(pady=(0, 15))
        priority_combo.set("Medium")
        
        # Buttons
        button_frame = tk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_and_close():
            self.add_application_from_dialog(dialog, job_name_entry.get().strip(), 
                                           company_entry.get().strip(), url_entry.get().strip(),
                                           date_entry.get().strip(), salary_entry.get().strip(),
                                           status_combo.get(), recruiter_entry.get().strip(),
                                           team_entry.get().strip(), hiring_manager_entry.get().strip(),
                                           priority_combo.get())
        
        add_btn = tk.CTkButton(button_frame, text="Add Application", 
                              command=add_and_close)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.CTkButton(button_frame, text="Cancel", 
                                 command=dialog.destroy, fg_color="gray")
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def add_application_from_dialog(self, dialog, job_name, company, url, date_text, salary, status, recruiter, team_member, hiring_manager, priority):
        """Add application from dialog data"""
        # Validate required fields
        if not job_name or not company:
            tkinter.messagebox.showerror("Error", "Job title and company are required!")
            return
        
        # Handle date
        if date_text.lower() == "today":
            date_applied = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
                date_applied = date_text
            except ValueError:
                tkinter.messagebox.showerror("Error", "Please use YYYY-MM-DD format for date!")
                return
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO applications (job_name, url, company, date_applied, 
                                       salary, status, recruiter_dm, team_member_dm, 
                                       hiring_manager_dm, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (job_name, url, company, date_applied, salary, status, 
                  recruiter, team_member, hiring_manager, priority))
            
            self.db.commit()
            self.refresh_applications()
            tkinter.messagebox.showinfo("Success", "Application added successfully!")
            dialog.destroy()
            
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to add application: {str(e)}")
    
    def create_applications_list(self):
        """Create the applications list display"""
        # Create main container with explicit scrollbar
        list_container = tk.CTkFrame(self.list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable frame with scrollbar
        self.applications_frame = tk.CTkScrollableFrame(list_container)
        self.applications_frame.pack(fill=tk.BOTH, expand=True)
        
        # Empty state label
        self.empty_label = tk.CTkLabel(self.applications_frame, 
                                    text="No applications yet. Add your first application!",
                                    font=("Arial", 14))
        self.empty_label.pack(pady=50)

    def create_status_panel(self):
        """Create status update panel"""
        self.status_frame = tk.CTkFrame(self.list_frame)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.selected_app_label = tk.CTkLabel(self.status_frame, text="No application selected")
        self.selected_app_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        update_frame = tk.CTkFrame(self.status_frame)
        update_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.status_update_combo = tk.CTkComboBox(update_frame, width=150,
                                                values=["Applied", "Interview Scheduled", 
                                                      "Interviewed", "Offer Received", 
                                                      "Rejected", "Withdrawn"])
        self.status_update_combo.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.CTkButton(update_frame, text="Update Status", 
                                command=self.update_status, width=100)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.CTkButton(update_frame, text="Delete", fg_color="red",
                                command=self.delete_application, width=80)
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    def open_job_url(self, url=None):
        """Open the job URL in default browser"""
        if url is None:
            url = self.url_entry.get()
        if url:
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Could not open URL: {e}")
    
    def refresh_applications(self):
        """Refresh the applications list display"""
        # Clear existing applications
        for widget in self.applications_frame.winfo_children():
            widget.destroy()
        
        # Recreate empty_label
        self.empty_label = tk.CTkLabel(self.applications_frame, 
                                     text="No applications yet. Add your first application!",
                                     font=("Arial", 14))
        
        # Get applications from database
        cursor = self.db.cursor()
        sort_by = self.sort_combo.get()
        if sort_by == "Priority":
            order_by = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, date_applied DESC"
        else:  # Date Applied
            order_by = "date_applied DESC"
        
        cursor.execute(f'''
            SELECT id, job_name, company, date_applied, status, url, priority
            FROM applications ORDER BY {order_by}
        ''')
        
        applications = cursor.fetchall()
        
        if not applications:
            self.empty_label.pack(pady=50)
            return
        
        # Create application cards
        for app in applications:
            self.create_application_card(app)
        
        # Update stats
        self.update_stats()
    
    def create_application_card(self, app_data):
        """Create a card for a single application"""
        app_id, job_name, company, date_applied, status, url, priority = app_data
        
        # Determine background color based on status
        if status == "Applied":
            bg_color = "#d4edda"  # Light green
        elif status == "Rejected":
            bg_color = "#f8d7da"  # Light red
        elif status == "Pending":
            bg_color = "#fff3cd"  # Light yellow
        else:
            bg_color = None
        
        # Card frame
        card = tk.CTkFrame(self.applications_frame, fg_color=bg_color)
        card.pack(fill=tk.X, pady=5)
        
        # Left side - main info
        info_frame = tk.CTkFrame(card, fg_color=bg_color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Job title and company
        title_label = tk.CTkLabel(info_frame, text=f"{job_name} at {company}", 
                                font=("Arial", 14, "bold"), fg_color=bg_color)
        title_label.pack(anchor="w")
        
        # Date, status and priority
        date_status = tk.CTkLabel(info_frame, 
                                text=f"Applied: {date_applied} | Status: {status} | Priority: {priority}",
                                font=("Arial", 10), fg_color=bg_color)
        date_status.pack(anchor="w")
        
        # Right side - actions
        actions_frame = tk.CTkFrame(card, fg_color=bg_color)
        actions_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Customized CV checkbox
        cv_checkbox = tk.CTkCheckBox(actions_frame, text="Customized CV", fg_color=bg_color)
        cv_checkbox.pack(side=tk.LEFT, padx=2)
        
        if url:
            open_btn = tk.CTkButton(actions_frame, text="Open", width=60,
                                  command=lambda u=url: webbrowser.open(u))
            open_btn.pack(side=tk.LEFT, padx=2)
        
        edit_btn = tk.CTkButton(actions_frame, text="Edit", width=60,
                              command=lambda i=app_id: self.edit_application(i))
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        select_btn = tk.CTkButton(actions_frame, text="Select", width=60,
                                command=lambda i=app_id, j=job_name, c=company: 
                                self.select_application(i, j, c))
        select_btn.pack(side=tk.LEFT, padx=2)
    
    def edit_application(self, app_id):
        """Edit an existing application"""
        # Get application data
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
        app = cursor.fetchone()
        
        if not app:
            tkinter.messagebox.showerror("Error", "Application not found!")
            return
        
        # Open edit dialog with pre-filled data
        self.open_edit_dialog(app_id, app)
    
    def open_edit_dialog(self, app_id, app_data):
        """Open dialog for editing application"""
        # Create dialog window
        dialog = tk.CTkToplevel(self.root)
        dialog.title("Edit Application")
        dialog.geometry("400x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form title
        title_label = tk.CTkLabel(dialog, text="Edit Application", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Scrollable frame for form
        scroll_frame = tk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Job Name
        tk.CTkLabel(scroll_frame, text="Job Title:").pack(anchor="w", pady=(10, 0))
        job_name_entry = tk.CTkEntry(scroll_frame, width=350)
        job_name_entry.pack(pady=(0, 10))
        job_name_entry.insert(0, app_data[1])  # job_name
        
        # Company
        tk.CTkLabel(scroll_frame, text="Company:").pack(anchor="w", pady=(10, 0))
        company_entry = tk.CTkEntry(scroll_frame, width=350)
        company_entry.pack(pady=(0, 10))
        company_entry.insert(0, app_data[3])  # company
        
        # Job URL
        tk.CTkLabel(scroll_frame, text="Job URL:").pack(anchor="w", pady=(10, 0))
        url_frame = tk.CTkFrame(scroll_frame)
        url_frame.pack(pady=(0, 10))
        
        url_entry = tk.CTkEntry(url_frame, width=300)
        url_entry.pack(side=tk.LEFT, padx=(0, 5))
        url_entry.insert(0, app_data[2] or "")  # url
        
        open_url_btn = tk.CTkButton(url_frame, text="Open", width=40, 
                                   command=lambda: self.open_job_url(url_entry.get()))
        open_url_btn.pack(side=tk.RIGHT)
        
        # Date Applied
        tk.CTkLabel(scroll_frame, text="Date Applied:").pack(anchor="w", pady=(10, 0))
        date_entry = tk.CTkEntry(scroll_frame, width=350, 
                                placeholder_text="YYYY-MM-DD or 'today'")
        date_entry.pack(pady=(0, 10))
        date_entry.insert(0, app_data[4])  # date_applied
        
        # Salary
        tk.CTkLabel(scroll_frame, text="Salary:").pack(anchor="w", pady=(10, 0))
        salary_entry = tk.CTkEntry(scroll_frame, width=350, 
                                  placeholder_text="e.g., $80,000 - $100,000")
        salary_entry.pack(pady=(0, 10))
        salary_entry.insert(0, app_data[5] or "")  # salary
        
        # Status
        tk.CTkLabel(scroll_frame, text="Status:").pack(anchor="w", pady=(10, 0))
        status_combo = tk.CTkComboBox(scroll_frame, width=350,
                                     values=["Applied", "Interview Scheduled", 
                                           "Interviewed", "Offer Received", 
                                           "Rejected", "Withdrawn"])
        status_combo.pack(pady=(0, 10))
        status_combo.set(app_data[6])  # status
        
        # Recruiter DM
        tk.CTkLabel(scroll_frame, text="Recruiter Contact:").pack(anchor="w", pady=(10, 0))
        recruiter_entry = tk.CTkEntry(scroll_frame, width=350, 
                                     placeholder_text="Email, LinkedIn, phone...")
        recruiter_entry.pack(pady=(0, 10))
        recruiter_entry.insert(0, app_data[7] or "")  # recruiter_dm
        
        # Team Member DM
        tk.CTkLabel(scroll_frame, text="Team Member Contact:").pack(anchor="w", pady=(10, 0))
        team_entry = tk.CTkEntry(scroll_frame, width=350, 
                                placeholder_text="Email, LinkedIn, phone...")
        team_entry.pack(pady=(0, 10))
        team_entry.insert(0, app_data[8] or "")  # team_member_dm
        
        # Hiring Manager DM
        tk.CTkLabel(scroll_frame, text="Hiring Manager Contact:").pack(anchor="w", pady=(10, 0))
        hiring_manager_entry = tk.CTkEntry(scroll_frame, width=350,
                                          placeholder_text="Email, LinkedIn, phone...")
        hiring_manager_entry.pack(pady=(0, 10))
        hiring_manager_entry.insert(0, app_data[9] or "")  # hiring_manager_dm
        
        # Priority
        tk.CTkLabel(scroll_frame, text="Priority:").pack(anchor="w", pady=(10, 0))
        priority_combo = tk.CTkComboBox(scroll_frame, width=350,
                                       values=["Low", "Medium", "High"])
        priority_combo.pack(pady=(0, 15))
        priority_combo.set(app_data[10] or "Medium")  # priority
        
        # Buttons
        button_frame = tk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def update_and_close():
            self.update_application_from_dialog(dialog, app_id, job_name_entry.get().strip(), 
                                             company_entry.get().strip(), url_entry.get().strip(),
                                             date_entry.get().strip(), salary_entry.get().strip(),
                                             status_combo.get(), recruiter_entry.get().strip(),
                                             team_entry.get().strip(), hiring_manager_entry.get().strip(),
                                             priority_combo.get())
        
        update_btn = tk.CTkButton(button_frame, text="Update Application", 
                                 command=update_and_close)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.CTkButton(button_frame, text="Cancel", 
                                 command=dialog.destroy, fg_color="gray")
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def update_application_from_dialog(self, dialog, app_id, job_name, company, url, date_text, salary, status, recruiter, team_member, hiring_manager, priority):
        """Update application from dialog data"""
        # Validate required fields
        if not job_name or not company:
            tkinter.messagebox.showerror("Error", "Job title and company are required!")
            return
        
        # Handle date
        if date_text.lower() == "today":
            date_applied = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
                date_applied = date_text
            except ValueError:
                tkinter.messagebox.showerror("Error", "Please use YYYY-MM-DD format for date!")
                return
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                UPDATE applications 
                SET job_name = ?, url = ?, company = ?, date_applied = ?,
                    salary = ?, status = ?, recruiter_dm = ?, 
                    team_member_dm = ?, hiring_manager_dm = ?, priority = ?
                WHERE id = ?
            ''', (job_name, url, company, date_applied, salary, status,
                  recruiter, team_member, hiring_manager, priority, app_id))
            
            self.db.commit()
            self.refresh_applications()
            tkinter.messagebox.showinfo("Success", "Application updated successfully!")
            dialog.destroy()
            
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to update application: {str(e)}")
    
    def select_application(self, app_id, job_name, company):
        """Select an application for status update"""
        self.selected_app_id = app_id
        self.selected_app_label.configure(text=f"Selected: {job_name} at {company}")
        
        # Get current status
        cursor = self.db.cursor()
        cursor.execute('SELECT status FROM applications WHERE id = ?', (app_id,))
        current_status = cursor.fetchone()[0]
        self.status_update_combo.set(current_status)
    
    def update_status(self):
        """Update status of selected application"""
        if not hasattr(self, 'selected_app_id'):
            tkinter.messagebox.showerror("Error", "Please select an application first!")
            return
        
        new_status = self.status_update_combo.get()
        
        try:
            cursor = self.db.cursor()
            cursor.execute('UPDATE applications SET status = ? WHERE id = ?',
                         (new_status, self.selected_app_id))
            self.db.commit()
            self.refresh_applications()
            tkinter.messagebox.showinfo("Success", "Status updated successfully!")
            
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to update status: {str(e)}")
    
    def delete_application(self):
        """Delete selected application"""
        if not hasattr(self, 'selected_app_id'):
            tkinter.messagebox.showerror("Error", "Please select an application first!")
            return
        
        if tkinter.messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this application?"):
            try:
                cursor = self.db.cursor()
                cursor.execute('DELETE FROM applications WHERE id = ?',
                             (self.selected_app_id,))
                self.db.commit()
                self.refresh_applications()
                self.selected_app_label.configure(text="No application selected")
                tkinter.messagebox.showinfo("Success", "Application deleted successfully!")
                
            except Exception as e:
                tkinter.messagebox.showerror("Error", f"Failed to delete application: {str(e)}")
    
    def search_applications(self):
        """Search applications by text"""
        search_term = self.search_entry.get().strip()
        
        # Clear existing applications
        for widget in self.applications_frame.winfo_children():
            widget.destroy()
        
        # Recreate empty_label
        self.empty_label = tk.CTkLabel(self.applications_frame, 
                                     text="No applications yet. Add your first application!",
                                     font=("Arial", 14))
        
        cursor = self.db.cursor()
        sort_by = self.sort_combo.get()
        if sort_by == "Priority":
            order_by = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, date_applied DESC"
        else:  # Date Applied
            order_by = "date_applied DESC"
        
        if search_term:
            cursor.execute(f'''
                SELECT id, job_name, company, date_applied, status, url, priority
                FROM applications 
                WHERE job_name LIKE ? OR company LIKE ? OR status LIKE ?
                ORDER BY {order_by}
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute(f'''
                SELECT id, job_name, company, date_applied, status, url, priority
                FROM applications ORDER BY {order_by}
            ''')
        
        applications = cursor.fetchall()
        
        if not applications:
            self.empty_label.pack(pady=50)
        else:
            for app in applications:
                self.create_application_card(app)
    
    def update_stats(self):
        """Update statistics display"""
        cursor = self.db.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications')
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Applied'")
        applied = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Offer Received'")
        offers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Rejected'")
        rejected = cursor.fetchone()[0]
        
        stats_text = f"Total: {total} | Applied: {applied} | Pending: {pending} | Offers: {offers} | Rejected: {rejected}"
        self.stats_label.configure(text=stats_text)
    
    def export_to_csv(self):
        """Export applications to CSV file"""
        # Ask for file location
        file_path = tkinter.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Applications to CSV"
        )
        if not file_path:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT job_name, company, date_applied, status, priority, url, salary, 
                       recruiter_dm, team_member_dm, hiring_manager_dm, created_at
                FROM applications ORDER BY date_applied DESC
            ''')
            applications = cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Job Name', 'Company', 'Date Applied', 'Status', 'Priority', 
                               'URL', 'Salary', 'Recruiter Contact', 'Team Member Contact', 
                               'Hiring Manager Contact', 'Created At'])
                # Write data
                for app in applications:
                    writer.writerow(app)
            
            tkinter.messagebox.showinfo("Success", f"Exported {len(applications)} applications to {file_path}")
            
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
        self.db.close()

# Run the application
if __name__ == "__main__":
    app = JobTracker()
    app.run()
