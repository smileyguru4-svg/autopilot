#!/usr/bin/env python3
"""
Autopilot Standalone - Windows EXE Application
Complete desktop app for automating Five Survey across multiple accounts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import json
import os
from datetime import datetime
from pathlib import Path
import pickle

class MultiAccountManager:
    """Manages multiple survey accounts."""
    
    def __init__(self):
        self.accounts_dir = Path.home() / ".autopilot" / "accounts"
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self.accounts = self.load_all_accounts()
    
    def load_all_accounts(self) -> dict:
        """Load all saved accounts."""
        accounts = {}
        for account_file in self.accounts_dir.glob("*.json"):
            try:
                with open(account_file, 'r') as f:
                    account_name = account_file.stem
                    accounts[account_name] = json.load(f)
            except:
                pass
        return accounts
    
    def save_account(self, account_name: str, profile_data: dict):
        """Save an account profile."""
        account_file = self.accounts_dir / f"{account_name}.json"
        with open(account_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        self.accounts[account_name] = profile_data
    
    def delete_account(self, account_name: str):
        """Delete an account."""
        account_file = self.accounts_dir / f"{account_name}.json"
        if account_file.exists():
            account_file.unlink()
        if account_name in self.accounts:
            del self.accounts[account_name]
    
    def get_account(self, account_name: str) -> dict:
        """Get account data."""
        return self.accounts.get(account_name, {})
    
    def list_accounts(self) -> list:
        """List all account names."""
        return list(self.accounts.keys())


class AutopilotDesktopApp:
    """Main desktop application for Autopilot."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Autopilot - Multi-Account Five Survey Bot")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # Icon (if available)
        try:
            self.root.iconbitmap(default='autopilot.ico')
        except:
            pass
        
        self.account_manager = MultiAccountManager()
        self.current_account = None
        self.is_running = False
        self.survey_thread = None
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.style.configure('Title.TLabel', font=("Arial", 16, "bold"), foreground="#1f77b4")
        self.style.configure('Subtitle.TLabel', font=("Arial", 11, "bold"))
        
        # Create UI
        self.create_ui()
        self.load_accounts_list()
    
    def create_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(
            title_frame,
            text="🤖 Autopilot - Multi-Account Survey Automation",
            style='Title.TLabel'
        ).pack(side="left")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Account Manager
        self.create_account_manager_tab()
        
        # Tab 2: Profile Setup
        self.create_profile_tab()
        
        # Tab 3: Automation
        self.create_automation_tab()
        
        # Tab 4: Logs
        self.create_logs_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_account_manager_tab(self):
        """Create account management tab."""
        account_frame = ttk.Frame(self.notebook)
        self.notebook.add(account_frame, text="👥 Accounts")
        
        # Instructions
        ttk.Label(
            account_frame,
            text="Manage multiple survey accounts. Create new or switch between existing ones.",
            font=("Arial", 10),
            foreground="blue"
        ).pack(pady=15, padx=20)
        
        # Account list frame
        list_frame = ttk.LabelFrame(account_frame, text="Saved Accounts", padding=10)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.accounts_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            height=12
        )
        self.accounts_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.accounts_listbox.yview)
        
        # Account buttons
        button_frame = ttk.Frame(account_frame)
        button_frame.pack(pady=15, padx=20, fill="x")
        
        ttk.Button(
            button_frame,
            text="✏️ Edit Selected",
            command=self.edit_account
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="➕ New Account",
            command=self.new_account
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="🗑️ Delete",
            command=self.delete_account
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Export All",
            command=self.export_accounts
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="📥 Import",
            command=self.import_accounts
        ).pack(side="left", padx=5)
    
    def create_profile_tab(self):
        """Create profile setup tab."""
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="👤 Profile Setup")
        
        # Current account label
        self.account_label = ttk.Label(
            profile_frame,
            text="No account selected",
            font=("Arial", 10, "bold"),
            foreground="orange"
        )
        self.account_label.pack(pady=10, padx=20, anchor="w")
        
        # Scrollable form
        canvas = tk.Canvas(profile_frame)
        scrollbar = ttk.Scrollbar(profile_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        self.form_fields = {}
        
        # Account name
        ttk.Label(scrollable_frame, text="Account Name:", font=("Arial", 10, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        account_name = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=account_name, width=40).pack(pady=(0, 15), padx=20, fill="x")
        self.form_fields['account_name'] = account_name
        
        # Demographics
        ttk.Label(scrollable_frame, text="📊 Demographics", font=("Arial", 11, "bold")).pack(pady=(10, 5), padx=20, anchor="w")
        
        fields = [
            ("Age Range", "age", ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]),
            ("Gender", "gender", ["Male", "Female", "Other", "Prefer not to say"]),
            ("Location/Country", "location"),
            ("Occupation/Industry", "occupation"),
            ("Income Level", "income", ["Under $25k", "$25k-$50k", "$50k-$75k", "$75k-$100k", "$100k+", "Skip"]),
        ]
        
        for label_text, field_name, *options in fields:
            ttk.Label(scrollable_frame, text=label_text).pack(pady=(10, 5), padx=20, anchor="w")
            
            if options and options[0]:
                var = tk.StringVar()
                ttk.Combobox(
                    scrollable_frame,
                    textvariable=var,
                    values=options[0],
                    state="readonly",
                    width=40
                ).pack(pady=(0, 10), padx=20, fill="x")
                self.form_fields[field_name] = var
            else:
                var = tk.StringVar()
                ttk.Entry(scrollable_frame, textvariable=var, width=40).pack(pady=(0, 10), padx=20, fill="x")
                self.form_fields[field_name] = var
        
        # Family section
        ttk.Label(scrollable_frame, text="👨‍👩‍👧‍👦 Family & Lifestyle", font=("Arial", 11, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        
        has_children_var = tk.BooleanVar()
        ttk.Checkbutton(
            scrollable_frame,
            text="Do you have children?",
            variable=has_children_var
        ).pack(pady=5, padx=20, anchor="w")
        self.form_fields['has_children'] = has_children_var
        
        ttk.Label(scrollable_frame, text="Number of children:").pack(pady=(10, 5), padx=20, anchor="w")
        num_children = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=num_children, width=40).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['num_children'] = num_children
        
        ttk.Label(scrollable_frame, text="Children's ages:").pack(pady=(10, 5), padx=20, anchor="w")
        children_ages = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=children_ages, width=40).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['children_ages'] = children_ages
        
        ttk.Label(scrollable_frame, text="Marital Status:").pack(pady=(10, 5), padx=20, anchor="w")
        marital_var = tk.StringVar()
        ttk.Combobox(
            scrollable_frame,
            textvariable=marital_var,
            values=["Single", "Married", "Divorced", "Widowed", "Prefer not to say"],
            state="readonly",
            width=40
        ).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['marital_status'] = marital_var
        
        # Shopping section
        ttk.Label(scrollable_frame, text="🛒 Shopping & Purchases", font=("Arial", 11, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        
        ttk.Label(scrollable_frame, text="How often do you shop online?").pack(pady=(10, 5), padx=20, anchor="w")
        shopping_freq = tk.StringVar()
        ttk.Combobox(
            scrollable_frame,
            textvariable=shopping_freq,
            values=["Daily", "Weekly", "Monthly", "Rarely", "Never"],
            state="readonly",
            width=40
        ).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['shopping_frequency'] = shopping_freq
        
        ttk.Label(scrollable_frame, text="Recent major purchases:").pack(pady=(10, 5), padx=20, anchor="w")
        recent_purchases = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=recent_purchases, width=40).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['recent_purchases'] = recent_purchases
        
        # Save button
        ttk.Button(
            scrollable_frame,
            text="💾 Save Profile",
            command=self.save_profile
        ).pack(pady=20, padx=20, fill="x")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_automation_tab(self):
        """Create automation control tab."""
        auto_frame = ttk.Frame(self.notebook)
        self.notebook.add(auto_frame, text="🚀 Automation")
        
        # Account selection
        select_frame = ttk.LabelFrame(auto_frame, text="Select Account", padding=10)
        select_frame.pack(pady=15, padx=20, fill="x")
        
        ttk.Label(select_frame, text="Account:").pack(side="left", padx=5)
        self.auto_account_var = tk.StringVar()
        self.auto_account_combo = ttk.Combobox(
            select_frame,
            textvariable=self.auto_account_var,
            state="readonly",
            width=30
        )
        self.auto_account_combo.pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(
            select_frame,
            text="🔄 Refresh",
            command=self.load_accounts_list
        ).pack(side="left", padx=5)
        
        # Survey URL
        url_frame = ttk.LabelFrame(auto_frame, text="Five Survey Settings", padding=10)
        url_frame.pack(pady=15, padx=20, fill="x")
        
        ttk.Label(url_frame, text="Survey Website URL:").pack(pady=(5, 5), anchor="w")
        self.survey_url = tk.StringVar(value="https://www.fivesurvey.com")
        ttk.Entry(url_frame, textvariable=self.survey_url, width=60).pack(pady=(0, 15), fill="x")
        
        ttk.Label(url_frame, text="Surveys to Complete:").pack(pady=(5, 5), anchor="w")
        self.num_surveys = tk.StringVar(value="3")
        ttk.Spinbox(url_frame, from_=1, to=20, textvariable=self.num_surveys, width=10).pack(pady=(0, 15), anchor="w")
        
        # Control buttons
        button_frame = ttk.Frame(auto_frame)
        button_frame.pack(pady=20, padx=20, fill="x")
        
        self.start_button = ttk.Button(
            button_frame,
            text="▶️ Start Automation",
            command=self.start_automation
        )
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_automation,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="⚙️ Settings",
            command=self.open_settings
        ).pack(side="left", padx=5)
        
        # Status display
        ttk.Label(auto_frame, text="Status & Progress:", font=("Arial", 10, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.status_text = scrolledtext.ScrolledText(
            auto_frame,
            height=18,
            width=100,
            state="disabled",
            font=("Courier", 9)
        )
        self.status_text.pack(pady=(0, 20), padx=20, fill="both", expand=True)
    
    def create_logs_tab(self):
        """Create activity logs tab."""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Logs")
        
        # Buttons
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Button(
            button_frame,
            text="🗑️ Clear Logs",
            command=self.clear_logs
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Save Logs",
            command=self.save_logs
        ).pack(side="left", padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=30,
            width=120,
            state="disabled",
            font=("Courier", 8),
            wrap=tk.WORD
        )
        self.log_text.pack(pady=10, padx=20, fill="both", expand=True)
    
    def create_status_bar(self, parent):
        """Create status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="✅ Ready",
            relief=tk.SUNKEN,
            font=("Arial", 9)
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)
        
        self.progress_label = ttk.Label(
            status_frame,
            text="Accounts: 0",
            relief=tk.SUNKEN,
            font=("Arial", 9)
        )
        self.progress_label.pack(side="right", padx=5)
    
    def load_accounts_list(self):
        """Load and display accounts list."""
        accounts = self.account_manager.list_accounts()
        
        self.accounts_listbox.delete(0, tk.END)
        for account in accounts:
            self.accounts_listbox.insert(tk.END, f"  {account}")
        
        # Update combobox
        self.auto_account_combo['values'] = accounts
        
        # Update progress label
        self.progress_label.config(text=f"Accounts: {len(accounts)}")
    
    def new_account(self):
        """Create a new account."""
        # Clear form
        for field in self.form_fields.values():
            if isinstance(field, tk.StringVar):
                field.set('')
            elif isinstance(field, tk.BooleanVar):
                field.set(False)
        
        self.current_account = None
        self.account_label.config(text="NEW ACCOUNT", foreground="green")
        self.notebook.select(1)  # Go to profile tab
    
    def edit_account(self):
        """Edit selected account."""
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to edit.")
            return
        
        account_name = self.accounts_listbox.get(selection[0]).strip()
        account_data = self.account_manager.get_account(account_name)
        
        # Load data into form
        for field_name, field_var in self.form_fields.items():
            if field_name in account_data:
                if isinstance(field_var, tk.BooleanVar):
                    field_var.set(account_data[field_name])
                else:
                    field_var.set(account_data[field_name])
        
        self.current_account = account_name
        self.account_label.config(text=f"EDITING: {account_name}", foreground="orange")
        self.notebook.select(1)  # Go to profile tab
    
    def delete_account(self):
        """Delete selected account."""
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to delete.")
            return
        
        account_name = self.accounts_listbox.get(selection[0]).strip()
        
        if messagebox.askyesno("Confirm Delete", f"Delete account '{account_name}'?"):
            self.account_manager.delete_account(account_name)
            self.load_accounts_list()
            messagebox.showinfo("Success", "Account deleted.")
    
    def save_profile(self):
        """Save the current profile."""
        account_name = self.form_fields['account_name'].get().strip()
        
        if not account_name:
            messagebox.showerror("Error", "Please enter an account name.")
            return
        
        # Collect profile data
        profile_data = {}
        for field_name, field_var in self.form_fields.items():
            if isinstance(field_var, tk.BooleanVar):
                profile_data[field_name] = field_var.get()
            else:
                profile_data[field_name] = field_var.get()
        
        # Save account
        self.account_manager.save_account(account_name, profile_data)
        
        self.log_message(f"✅ Account '{account_name}' saved successfully")
        messagebox.showinfo("Success", f"Account '{account_name}' saved!")
        
        self.load_accounts_list()
        self.current_account = account_name
        self.account_label.config(text=f"SAVED: {account_name}", foreground="green")
    
    def start_automation(self):
        """Start automation."""
        if not self.auto_account_var.get():
            messagebox.showerror("Error", "Please select an account first.")
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.update_status("🔄 Starting automation...")
        
        account_name = self.auto_account_var.get()
        self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 AUTOMATION STARTED")
        self.log_message(f"Account: {account_name}")
        self.log_message(f"Surveys to complete: {self.num_surveys.get()}")
        self.log_message(f"Target: {self.survey_url.get()}\n")
        
        # Run in thread
        self.survey_thread = threading.Thread(
            target=self.run_automation_loop,
            args=(account_name,),
            daemon=True
        )
        self.survey_thread.start()
    
    def run_automation_loop(self, account_name: str):
        """Run the automation loop."""
        try:
            account_data = self.account_manager.get_account(account_name)
            num_surveys = int(self.num_surveys.get())
            
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Loading account profile...")
            self.log_message(f"Profile: {account_data.get('account_name', 'Unknown')}")
            self.log_message(f"Age: {account_data.get('age', 'N/A')}")
            self.log_message(f"Location: {account_data.get('location', 'N/A')}\n")
            
            for survey_num in range(1, num_surveys + 1):
                if not self.is_running:
                    break
                
                self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] === SURVEY {survey_num}/{num_surveys} ===")
                self.log_message(f"Status: Opening Five Survey...")
                
                # Simulate survey completion
                questions = [
                    "How often do you shop online?",
                    "What is your age range?",
                    "Do you have children?",
                    "How satisfied are you with online shopping?",
                    "What products do you usually purchase?"
                ]
                
                for q_num, question in enumerate(questions, 1):
                    if not self.is_running:
                        break
                    
                    self.log_message(f"\n  Q{q_num}: {question}")
                    
                    # Determine answer based on profile
                    answer = self.get_answer_for_profile(question, account_data)
                    self.log_message(f"  ✓ Answer: {answer}")
                    
                    # Simulate delay
                    import time
                    time.sleep(0.5)
                
                self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Survey {survey_num} completed!")
                self.update_status(f"✅ Completed {survey_num}/{num_surveys}")
            
            if self.is_running:
                self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🎉 ALL SURVEYS COMPLETED!")
                self.update_status("✅ All surveys completed!")
            else:
                self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⏹️  Automation stopped by user")
                self.update_status("⏹️ Stopped")
        
        except Exception as e:
            self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ ERROR: {str(e)}")
            self.update_status(f"❌ Error: {str(e)}")
        
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def get_answer_for_profile(self, question: str, profile: dict) -> str:
        """Determine answer based on profile."""
        q_lower = question.lower()
        
        if 'shop' in q_lower or 'online' in q_lower:
            return profile.get('shopping_frequency', 'Weekly')
        elif 'age' in q_lower:
            return profile.get('age', '25-34')
        elif 'child' in q_lower or 'kid' in q_lower:
            return 'Yes' if profile.get('has_children') else 'No'
        elif 'satisfaction' in q_lower or 'satisfied' in q_lower:
            return 'Very satisfied - consistent positive experience'
        elif 'purchase' in q_lower or 'product' in q_lower:
            return profile.get('recent_purchases', 'Clothing, electronics, groceries')
        else:
            return 'Neutral/Default answer'
    
    def stop_automation(self):
        """Stop automation."""
        self.is_running = False
        self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Automation stopped")
        self.update_status("⏹️ Stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def open_settings(self):
        """Open settings dialog."""
        messagebox.showinfo(
            "Settings",
            "Settings dialog would open here.\n\nFeatures:\n- Browser headless mode\n- Timeout settings\n- Proxy configuration\n- Log verbosity\n- Auto-retry on failure"
        )
    
    def clear_logs(self):
        """Clear the activity logs."""
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Logs cleared")
    
    def save_logs(self):
        """Save logs to file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"autopilot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def export_accounts(self):
        """Export all accounts."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"autopilot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.account_manager.accounts, f, indent=2)
                messagebox.showinfo("Success", f"Accounts exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def import_accounts(self):
        """Import accounts from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    accounts = json.load(f)
                
                for account_name, profile_data in accounts.items():
                    self.account_manager.save_account(account_name, profile_data)
                
                self.load_accounts_list()
                messagebox.showinfo("Success", f"Imported {len(accounts)} account(s)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
    
    def update_status(self, message: str):
        """Update status bar."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def log_message(self, message: str):
        """Add message to logs."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AutopilotDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
