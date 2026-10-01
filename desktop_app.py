#!/usr/bin/env python3
"""
Autopilot Desktop App - Five Survey Automation
A standalone desktop application for autonomous survey completion.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime
from core.agent import SurveyAgent
from core.persona import PersonaBuilder
from core.five_survey import FiveSurveyBot

class AutopilotDesktopApp:
    """Main desktop application for Autopilot."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Autopilot - Five Survey Bot")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.persona = None
        self.bot = None
        self.is_running = False
        self.survey_thread = None
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🤖 Autopilot - Five Survey Automation",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Profile Setup
        self.setup_profile_tab()
        
        # Tab 2: Survey Automation
        self.setup_automation_tab()
        
        # Tab 3: Activity Log
        self.setup_log_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def setup_profile_tab(self):
        """Create the profile setup tab."""
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="👤 Profile Setup")
        
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
        fields = [
            ("Age Range", "age", ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]),
            ("Gender", "gender", ["Male", "Female", "Other", "Prefer not to say"]),
            ("Location/Country", "location"),
            ("Occupation/Industry", "occupation"),
            ("Income Level (Optional)", "income", ["Under $25k", "$25k-$50k", "$50k-$75k", "$75k-$100k", "$100k+", "Skip"]),
        ]
        
        self.form_fields = {}
        
        for label_text, field_name, *options in fields:
            label = ttk.Label(scrollable_frame, text=label_text, font=("Arial", 10, "bold"))
            label.pack(pady=(10, 5), padx=20, anchor="w")
            
            if options and options[0]:
                var = tk.StringVar()
                combo = ttk.Combobox(
                    scrollable_frame,
                    textvariable=var,
                    values=options[0],
                    state="readonly",
                    width=40
                )
                combo.pack(pady=(0, 10), padx=20, fill="x")
                self.form_fields[field_name] = var
            else:
                var = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=40)
                entry.pack(pady=(0, 10), padx=20, fill="x")
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
        
        ttk.Label(scrollable_frame, text="Number of children (if applicable):").pack(pady=(10, 5), padx=20, anchor="w")
        num_children = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=num_children, width=40).pack(pady=(0, 10), padx=20, fill="x")
        self.form_fields['num_children'] = num_children
        
        ttk.Label(scrollable_frame, text="Children's ages (if applicable):").pack(pady=(10, 5), padx=20, anchor="w")
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
        ttk.Label(scrollable_frame, text="🛍️ Shopping & Purchases", font=("Arial", 11, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        
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
        
        ttk.Label(scrollable_frame, text="Recent major purchases (e.g., car, home, electronics):").pack(pady=(10, 5), padx=20, anchor="w")
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
    
    def setup_automation_tab(self):
        """Create the survey automation tab."""
        auto_frame = ttk.Frame(self.notebook)
        self.notebook.add(auto_frame, text="🚀 Automation")
        
        # Instructions
        instructions = ttk.Label(
            auto_frame,
            text="Make sure your profile is saved first, then start the automation.",
            font=("Arial", 10),
            foreground="blue"
        )
        instructions.pack(pady=20, padx=20)
        
        # Survey URL input
        ttk.Label(auto_frame, text="Five Survey URL:", font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.survey_url = tk.StringVar(value="https://www.fivesurvey.com")
        ttk.Entry(auto_frame, textvariable=self.survey_url, width=60).pack(pady=(0, 20), padx=20, fill="x")
        
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
        
        # Status info
        ttk.Label(auto_frame, text="Status:", font=("Arial", 10, "bold")).pack(pady=(20, 5), padx=20, anchor="w")
        self.status_text = scrolledtext.ScrolledText(
            auto_frame,
            height=15,
            width=80,
            state="disabled",
            font=("Courier", 9)
        )
        self.status_text.pack(pady=(0, 20), padx=20, fill="both", expand=True)
    
    def setup_log_tab(self):
        """Create the activity log tab."""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📊 Activity Log")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=25,
            width=100,
            state="disabled",
            font=("Courier", 9)
        )
        self.log_text.pack(pady=20, padx=20, fill="both", expand=True)
    
    def create_status_bar(self, parent):
        """Create a status bar at the bottom."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="⏳ Ready",
            relief=tk.SUNKEN
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)
    
    def save_profile(self):
        """Save the user profile."""
        # Collect form data
        profile_data = {}
        for field_name, var in self.form_fields.items():
            if isinstance(var, tk.BooleanVar):
                profile_data[field_name] = var.get()
            else:
                profile_data[field_name] = var.get()
        
        # Validate required fields
        if not profile_data.get('age') or not profile_data.get('gender') or not profile_data.get('location'):
            messagebox.showerror("Validation Error", "Please fill in all required fields (Age, Gender, Location)")
            return
        
        # Create persona
        self.persona = PersonaBuilder()
        self.persona.set_profile(profile_data)
        
        # Save to file
        try:
            with open('saved_profile.json', 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            messagebox.showinfo("Success", "✅ Profile saved successfully!")
            self.update_status("Profile saved")
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Profile saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")
    
    def start_automation(self):
        """Start the survey automation."""
        if not self.persona:
            messagebox.showerror("Error", "❌ Please save your profile first!")
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.update_status("🚀 Starting automation...")
        
        # Run in separate thread to avoid freezing UI
        self.survey_thread = threading.Thread(target=self.run_survey_automation, daemon=True)
        self.survey_thread.start()
    
    def run_survey_automation(self):
        """Run the survey automation in a separate thread."""
        try:
            self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 Autopilot starting...")
            self.update_status("🔄 Loading Five Survey...")
            
            # Initialize bot
            self.bot = FiveSurveyBot(self.persona, self.log_message)
            
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Navigating to Five Survey...")
            self.update_status("🌐 Connecting to website...")
            
            # Start automation
            self.bot.start(self.survey_url.get())
            
            self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Automation completed!")
            self.update_status("✅ Complete")
            
            messagebox.showinfo("Complete", "✅ Survey automation completed!")
            
        except Exception as e:
            self.log_message(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ ERROR: {str(e)}")
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Automation failed: {e}")
        
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def stop_automation(self):
        """Stop the survey automation."""
        self.is_running = False
        if self.bot:
            self.bot.stop()
        
        self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️  Automation stopped by user")
        self.update_status("⏹️ Stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        messagebox.showinfo("Stopped", "Automation has been stopped.")
    
    def update_status(self, message: str):
        """Update the status bar."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def log_message(self, message: str):
        """Add a message to the activity log."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state="disabled")
        self.root.update_idletasks()


def main():
    """Main entry point for the desktop app."""
    root = tk.Tk()
    app = AutopilotDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
