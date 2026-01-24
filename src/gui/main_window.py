"""
Main Window - Upload Screen
Initial interface for uploading resume and selecting job domain
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional
from .styles import COLORS, FONTS, SPACING, WINDOW, SIZES


class MainWindow(ctk.CTkFrame):
    """
    Main upload window for the Job Market Analyzer.
    Allows users to upload resume and select job domain.
    """

    def __init__(self, parent, on_analyze_callback: Callable):
        """
        Initialize the main window.

        Args:
            parent: Parent widget
            on_analyze_callback: Callback function when analysis starts
        """
        super().__init__(parent, fg_color=COLORS['bg_secondary'])

        self.on_analyze_callback = on_analyze_callback
        self.selected_file: Optional[str] = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create UI
        self._create_widgets()

    def _create_widgets(self):
        """Create all UI widgets"""
    # Main container
        container = ctk.CTkScrollableFrame(
        self,
        fg_color=COLORS['bg_primary'],
        corner_radius=SIZES['border_radius']
    )
        container.pack(fill="both", expand=True,
                   padx=SPACING['xxl'], pady=SPACING['xxl'])

    # Title
        title_label = ctk.CTkLabel(
        container,
        text="📊 Job Market Analyzer",
        font=FONTS['title'],
        text_color=COLORS['primary']
        )
        title_label.pack(pady=(SPACING['xl'], SPACING['md']))

    # Subtitle
        subtitle_label = ctk.CTkLabel(
        container,
        text="AI-Powered Career Analysis Tool",
        font=FONTS['body'],
        text_color=COLORS['text_secondary']
    )
        subtitle_label.pack(pady=(0, SPACING['xl']))

    # Instructions card
        self._create_instructions_card(container)

    # Job domain selection
        self._create_domain_selector(container)

    # File upload section
        self._create_file_upload_section(container)

    # Analyze button
        self._create_analyze_button(container)

    # Progress section (hidden initially)
        self._create_progress_section(container)


    def _create_instructions_card(self, parent):
        """Create instructions card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=SIZES['border_radius'])
        card.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        # Title
        card_title = ctk.CTkLabel(
            card,
            text="How to Use:",
            font=FONTS['heading'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        card_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        
        instructions = [
            "1. Select your job domain from the dropdown",
            "2. Upload your resume (PDF or Image)",
            "3. Click 'Analyze Resume' to start",
            "4. View your personalized skill gap analysis and learning path"
        ]
        
        for instruction in instructions:
            label = ctk.CTkLabel(
                card,
                text=instruction,
                font=FONTS['body'],
                text_color=COLORS['text_primary'],
                anchor="w"
            )
            label.pack(anchor="w", padx=SPACING['lg'], pady=SPACING['xs'])
        
        # Add bottom padding
        spacer = ctk.CTkLabel(card, text="", height=SPACING['sm'])
        spacer.pack()


    def _create_domain_selector(self, parent):
        """Create job domain dropdown"""
        label = ctk.CTkLabel(
            parent,
            text="Select Job Domain:",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
         )
        label.pack(anchor="w", padx=SPACING['lg'],
               pady=(SPACING['lg'], SPACING['sm']))

        domains = [
        "Software Developer",
        "Data Scientist",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Machine Learning Engineer",
        "Web Developer"
    ]

        self.domain_var = ctk.StringVar(value="Software Developer")
        self.domain_dropdown = ctk.CTkComboBox(
            parent,
            values=domains,
            variable=self.domain_var,
            font=FONTS['body'],
            dropdown_font=FONTS['body'],
            height=SIZES['input_height'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover']
    )
        self.domain_dropdown.pack(fill="x", padx=SPACING['lg'],
                              pady=(0, SPACING['md']))


    def _create_file_upload_section(self, parent):
        """Create file upload section"""
        label = ctk.CTkLabel(
        parent,
        text="Upload Resume:",
        font=FONTS['heading'],
        text_color=COLORS['text_primary']
    )
        label.pack(anchor="w", padx=SPACING['lg'],
               pady=(SPACING['lg'], SPACING['sm']))

        self.upload_button = ctk.CTkButton(
        parent,
        text="📄 Choose File",
        command=self._handle_file_upload,
        font=FONTS['button'],
        height=SIZES['button_height'],
        fg_color=COLORS['primary'],
        hover_color=COLORS['primary_hover']
    )
        self.upload_button.pack(fill="x", padx=SPACING['lg'],
                            pady=(0, SPACING['sm']))

        self.file_label = ctk.CTkLabel(
        parent,
        text="No file selected",
        font=FONTS['small'],
        text_color=COLORS['text_secondary']
    )
        self.file_label.pack(anchor="w", padx=SPACING['lg'],
                         pady=(0, SPACING['md']))


    def _create_analyze_button(self, parent):
        """Create analyze button"""
        self.analyze_button = ctk.CTkButton(
        parent,
        text="🚀 Analyze Resume",
        command=self._handle_analyze,
        font=FONTS['button'],
        height=SIZES['button_height'] + 10,
        fg_color=COLORS['success'],
        hover_color=COLORS['success_hover'],
        state="disabled"
    )
        self.analyze_button.pack(fill="x", padx=SPACING['lg'],
                             pady=SPACING['xl'])


    def _create_progress_section(self, parent):
        """Create progress section (hidden initially)"""
        self.progress_frame = ctk.CTkFrame(
        parent,
        fg_color=COLORS['bg_secondary'],
        corner_radius=SIZES['border_radius']
    )

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            progress_color=COLORS['primary']
        )
        self.progress_bar.pack(fill="x", padx=SPACING['lg'],
                           pady=SPACING['md'])
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to analyze...",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack(anchor="w", padx=SPACING['lg'],
                                pady=(0, SPACING['md']))
        
    def _handle_file_upload(self):
        """Handle file upload button click"""
        filetypes = [
            ("All Supported", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("PDF files", "*.pdf"),
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("All files", "*.*")
    ]

        filename = filedialog.askopenfilename(
        title="Select Resume File",
        filetypes=filetypes
    )

        if filename:
            self.selected_file = filename
            file_path = Path(filename)
            self.file_label.configure(text=f"Selected: {file_path.name}")
            self.analyze_button.configure(state="normal")



    def _handle_analyze(self):
        """Handle analyze button click"""
        print("DEBUG: Analyze button clicked!")
        print(f"DEBUG: Selected file: {self.selected_file}")
        print(f"DEBUG: Domain: {self.domain_var.get()}")
        
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a resume file first")
            print("DEBUG: No file selected")
            return
        
        domain = self.domain_var.get()
        print(f"DEBUG: Starting analysis with domain: {domain}")
        
        # Show progress section
        self.progress_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        print("DEBUG: Progress frame shown")
        
        # Disable buttons during processing
        self.upload_button.configure(state="disabled")
        self.analyze_button.configure(state="disabled")
        print("DEBUG: Buttons disabled")
        
        # Call callback with file and domain
        print(f"DEBUG: Calling callback with file={self.selected_file}, domain={domain}")
        try:
            self.on_analyze_callback(self.selected_file, domain)
            print("DEBUG: Callback called successfully")
        except Exception as e:
            print(f"DEBUG ERROR: Callback failed: {e}")
            import traceback
            traceback.print_exc()

    def reset(self):
        """Reset the upload form"""
        self.selected_file = None
        self.file_label.configure(text="No file selected")
        self.upload_button.configure(state="normal")
        self.analyze_button.configure(state="disabled")
        self.progress_frame.pack_forget()
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to analyze...")