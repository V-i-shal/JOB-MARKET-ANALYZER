"""
Results Window - Display Analysis Results
Shows skill analysis, job matches, learning path, and charts
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
from typing import Optional
from pathlib import Path
from .styles import COLORS, FONTS, SPACING, SIZES


class ResultsWindow(ctk.CTkFrame):
    """
    Results display window showing analysis results in tabs.
    """
    
    def __init__(self, parent, analysis_result, on_new_analysis_callback):
        """
        Initialize the results window.
        
        Args:
            parent: Parent widget
            analysis_result: AnalysisResult object with all data
            on_new_analysis_callback: Callback to start new analysis
        """
        super().__init__(parent, fg_color=COLORS['bg_secondary'])
        
        self.analysis_result = analysis_result
        self.on_new_analysis_callback = on_new_analysis_callback
        
        # Create UI
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header section
        self._create_header()
        
        # Stats cards
        self._create_stats_cards()
        
        # Tabview for different sections
        self._create_tabview()
        
        # Action buttons
        self._create_action_buttons()
    
    def _create_header(self):
        """Create header with title"""
        header = ctk.CTkFrame(self, fg_color=COLORS['primary'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(
            header,
            text="📊 Analysis Results",
            font=FONTS['title'],
            text_color=COLORS['text_white']
        )
        title.pack(pady=SPACING['lg'])
        
        # Resume name
        resume_name = ctk.CTkLabel(
            header,
            text=f"Resume: {self.analysis_result.resume.filename}",
            font=FONTS['body'],
            text_color=COLORS['text_white']
        )
        resume_name.pack(pady=(0, SPACING['lg']))
    
    def _create_stats_cards(self):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Configure grid
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        
        # Stat 1: Match Percentage
        self._create_stat_card(
            stats_frame, 
            "Overall Match", 
            f"{self.analysis_result.match_percentage}%",
            COLORS['primary'],
            0
        )
        
        # Stat 2: Jobs Analyzed
        self._create_stat_card(
            stats_frame,
            "Jobs Analyzed",
            str(self.analysis_result.total_jobs_analyzed),
            COLORS['success'],
            1
        )
        
        # Stat 3: Matching Skills
        self._create_stat_card(
            stats_frame,
            "Skills You Have",
            str(self.analysis_result.matching_skill_count),
            COLORS['success'],
            2
        )
        
        # Stat 4: Missing Skills
        self._create_stat_card(
            stats_frame,
            "Skills to Learn",
            str(self.analysis_result.missing_skill_count),
            COLORS['danger'],
            3
        )
    
    def _create_stat_card(self, parent, title, value, color, column):
        """Create a single stat card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_primary'], corner_radius=SIZES['border_radius'])
        card.grid(row=0, column=column, padx=SPACING['sm'], sticky="ew")
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=FONTS['title'],
            text_color=color
        )
        value_label.pack(pady=(SPACING['lg'], SPACING['xs']))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(0, SPACING['lg']))
    
    def _create_tabview(self):
        """Create tabbed view for different sections"""
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS['bg_primary'],
            segmented_button_fg_color=COLORS['bg_secondary'],
            segmented_button_selected_color=COLORS['primary'],
            segmented_button_selected_hover_color=COLORS['primary_hover']
        )
        self.tabview.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Create tabs
        self.tabview.add("Summary")
        self.tabview.add("Job Matches")
        self.tabview.add("Learning Path")
        self.tabview.add("Charts")
        
        # Populate tabs
        self._create_summary_tab()
        self._create_jobs_tab()
        self._create_learning_path_tab()
        self._create_charts_tab()
    
    def _create_summary_tab(self):
        """Create summary tab"""
        tab = self.tabview.tab("Summary")
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        # Resume info section
        info_title = ctk.CTkLabel(
            scroll,
            text="Resume Information",
            font=FONTS['heading'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        info_title.pack(fill="x", pady=(0, SPACING['sm']))
        
        info_text = f"""
Filename: {self.analysis_result.resume.filename}
Skills Extracted: {self.analysis_result.resume.skill_count}
Name: {self.analysis_result.resume.user_name or 'Not detected'}
Email: {self.analysis_result.resume.email or 'Not detected'}
        """.strip()
        
        info_label = ctk.CTkLabel(
            scroll,
            text=info_text,
            font=FONTS['body'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            justify="left"
        )
        info_label.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Matching Skills section
        if self.analysis_result.matching_skills:
            match_title = ctk.CTkLabel(
                scroll,
                text=f"✓ Skills You Have ({len(self.analysis_result.matching_skills)})",
                font=FONTS['heading'],
                text_color=COLORS['success'],
                anchor="w"
            )
            match_title.pack(fill="x", pady=(SPACING['md'], SPACING['sm']))
            
            # Skills container
            skills_frame = ctk.CTkFrame(scroll, fg_color=COLORS['bg_secondary'], corner_radius=SIZES['border_radius'])
            skills_frame.pack(fill="x", pady=(0, SPACING['lg']))
            
            # Create skill pills
            self._create_skill_pills(skills_frame, self.analysis_result.matching_skills, is_matching=True)
        
        # Missing Skills section
        if self.analysis_result.missing_skills:
            missing_title = ctk.CTkLabel(
                scroll,
                text=f"✗ Skills to Learn ({len(self.analysis_result.missing_skills)})",
                font=FONTS['heading'],
                text_color=COLORS['danger'],
                anchor="w"
            )
            missing_title.pack(fill="x", pady=(SPACING['md'], SPACING['sm']))
            
            # Skills container
            skills_frame = ctk.CTkFrame(scroll, fg_color=COLORS['bg_secondary'], corner_radius=SIZES['border_radius'])
            skills_frame.pack(fill="x", pady=(0, SPACING['lg']))
            
            # Create skill pills (top 10)
            self._create_skill_pills(skills_frame, self.analysis_result.top_missing_skills, is_matching=False)
    
    def _create_skill_pills(self, parent, skills, is_matching):
        """Create skill pill badges"""
        # Use a frame with wrapping
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])
        
        row = 0
        col = 0
        max_cols = 4
        
        for skill in skills:
            bg_color = COLORS['skill_match_bg'] if is_matching else COLORS['skill_missing_bg']
            text_color = COLORS['skill_match'] if is_matching else COLORS['skill_missing']
            
            pill = ctk.CTkLabel(
                container,
                text=f"{skill.name} ({skill.frequency})",
                font=FONTS['body'],
                fg_color=bg_color,
                text_color=text_color,
                corner_radius=20
            )
            pill.grid(row=row, column=col, padx=SPACING['xs'], pady=SPACING['xs'], sticky="w")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _create_jobs_tab(self):
        """Create job matches tab"""
        tab = self.tabview.tab("Job Matches")
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        # Show jobs
        for i, job in enumerate(self.analysis_result.analyzed_jobs[:20], 1):  # Show top 20
            self._create_job_card(scroll, job, i)
    
    def _create_job_card(self, parent, job, index):
        """Create a job card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_primary'], corner_radius=SIZES['border_radius'])
        card.pack(fill="x", pady=SPACING['sm'])
        
        # Header with job title and company
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['xs']))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{index}. {job.title}",
            font=FONTS['heading'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Match percentage
        match_pct = job.calculate_match_percentage(self.analysis_result.resume.skills)
        match_color = COLORS['success'] if match_pct >= 50 else COLORS['warning'] if match_pct >= 30 else COLORS['danger']
        
        match_label = ctk.CTkLabel(
            header_frame,
            text=f"{match_pct}% Match",
            font=FONTS['body_bold'],
            text_color=match_color
        )
        match_label.pack(side="right")
        
        # Company and location
        info_label = ctk.CTkLabel(
            card,
            text=f"{job.company} • {job.location or 'Remote/Hybrid'}",
            font=FONTS['small'],
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        info_label.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        # Skills required
        skills_text = f"Required Skills: {job.get_required_skills_as_string()}"
        skills_label = ctk.CTkLabel(
            card,
            text=skills_text,
            font=FONTS['small'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            wraplength=800
        )
        skills_label.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        # Button frame
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Search on LinkedIn button
        def search_linkedin():
            import webbrowser
            # Create LinkedIn job search URL
            job_query = job.title.replace(" ", "%20")
            linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={job_query}&location=Worldwide"
            webbrowser.open(linkedin_url)
        
        linkedin_btn = ctk.CTkButton(
            button_frame,
            text="🔗 Search on LinkedIn",
            command=search_linkedin,
            font=FONTS['small_bold'],
            height=30,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        )
        linkedin_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        # Search on Indeed button
        def search_indeed():
            import webbrowser
            job_query = job.title.replace(" ", "+")
            indeed_url = f"https://www.indeed.com/jobs?q={job_query}"
            webbrowser.open(indeed_url)
        
        indeed_btn = ctk.CTkButton(
            button_frame,
            text="🔗 Search on Indeed",
            command=search_indeed,
            font=FONTS['small_bold'],
            height=30,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        )
        indeed_btn.pack(side="left")
        
    def _create_learning_path_tab(self):
        """Create learning path tab with clickable links"""
        tab = self.tabview.tab("Learning Path")
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(tab, fg_color=COLORS['bg_primary'])
        scroll.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        # Parse and display learning path with clickable links
        self._create_formatted_learning_path(scroll)

    def _create_formatted_learning_path(self, parent):
        """Create formatted learning path with clickable links"""
        import re
        
        # Title
        title = ctk.CTkLabel(
            parent,
            text="YOUR PERSONALIZED 4-WEEK LEARNING PATH",
            font=FONTS['title'],
            text_color=COLORS['primary']
        )
        title.pack(pady=SPACING['lg'])
        
        # Split learning path into lines
        lines = self.analysis_result.learning_path.split('\n')
        
        # URL pattern
        url_pattern = r'https?://[^\s]+'
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('='):
                continue  # Skip empty lines and separators
            
            # Check if line contains URL
            urls = re.findall(url_pattern, line)
            
            if urls:
                # Line with URL - create clickable link
                url = urls[0]
                # Remove URL from text
                text_without_url = line.replace(url, '').strip()
                
                # Container for text and button
                link_frame = ctk.CTkFrame(parent, fg_color="transparent")
                link_frame.pack(fill="x", pady=SPACING['xs'], padx=SPACING['md'])
                
                # Text part
                if text_without_url:
                    text_label = ctk.CTkLabel(
                        link_frame,
                        text=text_without_url,
                        font=FONTS['body'],
                        text_color=COLORS['text_primary'],
                        anchor="w"
                    )
                    text_label.pack(side="left", fill="x", expand=True)
                
                # Link button
                def make_open_url(link):
                    return lambda: webbrowser.open(link)
                
                link_btn = ctk.CTkButton(
                    link_frame,
                    text="🔗 Open Course",
                    command=make_open_url(url),
                    font=FONTS['small_bold'],
                    height=25,
                    width=120,
                    fg_color=COLORS['primary'],
                    hover_color=COLORS['primary_hover']
                )
                link_btn.pack(side="right")
                
            elif line.startswith('📅 WEEK'):
                # Week header
                week_label = ctk.CTkLabel(
                    parent,
                    text=line,
                    font=FONTS['subtitle'],
                    text_color=COLORS['primary']
                )
                week_label.pack(fill="x", pady=(SPACING['lg'], SPACING['sm']), padx=SPACING['md'])
                
            elif line.startswith('🎯') or line.startswith('📖') or line.startswith('🏆') or line.startswith('💡'):
                # Section headers
                section_label = ctk.CTkLabel(
                    parent,
                    text=line,
                    font=FONTS['heading'],
                    text_color=COLORS['text_primary'],
                    anchor="w"
                )
                section_label.pack(fill="x", pady=(SPACING['md'], SPACING['xs']), padx=SPACING['md'])
                
            elif line.startswith('•') or line.startswith('-') or line.startswith('→') or line.startswith('↳') or line.startswith('⭐'):
                # Bullet points
                bullet_label = ctk.CTkLabel(
                    parent,
                    text=line,
                    font=FONTS['body'],
                    text_color=COLORS['text_secondary'],
                    anchor="w",
                    justify="left"
                )
                bullet_label.pack(fill="x", pady=SPACING['xs'], padx=(SPACING['xl'], SPACING['md']))
                
            elif line.strip().startswith(('1.', '2.', '3.', '4.')):
                # Numbered lists
                num_label = ctk.CTkLabel(
                    parent,
                    text=line,
                    font=FONTS['body'],
                    text_color=COLORS['text_secondary'],
                    anchor="w",
                    justify="left"
                )
                num_label.pack(fill="x", pady=SPACING['xs'], padx=(SPACING['xl'], SPACING['md']))
                
            elif line.startswith('─'):
                # Separator
                separator = ctk.CTkFrame(parent, height=2, fg_color=COLORS['border_light'])
                separator.pack(fill="x", pady=SPACING['sm'], padx=SPACING['lg'])
                
            else:
                # Regular text
                if line:
                    text_label = ctk.CTkLabel(
                        parent,
                        text=line,
                        font=FONTS['body'],
                        text_color=COLORS['text_secondary'],
                        anchor="w",
                        wraplength=900,
                        justify="left"
                    )
                    text_label.pack(fill="x", pady=SPACING['xs'], padx=SPACING['md'])
    
    def _create_charts_tab(self):
        """Create charts tab"""
        tab = self.tabview.tab("Charts")
        
        # Info label
        info = ctk.CTkLabel(
            tab,
            text="📊 Interactive charts have been saved to the 'charts/' folder\n\nOpen the HTML files in your browser to view interactive visualizations",
            font=FONTS['body'],
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        info.pack(expand=True)
        
        # Open charts button
        open_btn = ctk.CTkButton(
            tab,
            text="📂 Open Charts Folder",
            command=self._open_charts_folder,
            font=FONTS['button'],
            height=SIZES['button_height'],
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        )
        open_btn.pack(pady=SPACING['lg'])
    
    def _create_action_buttons(self):
        """Create action buttons at bottom"""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Export button
        export_btn = ctk.CTkButton(
            button_frame,
            text="💾 Export Results",
            command=self._export_results,
            font=FONTS['button'],
            height=SIZES['button_height'],
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        )
        export_btn.pack(side="left", expand=True, fill="x", padx=(0, SPACING['sm']))
        
        # New analysis button
        new_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Analyze Another Resume",
            command=self._new_analysis,
            font=FONTS['button'],
            height=SIZES['button_height'],
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        )
        new_btn.pack(side="right", expand=True, fill="x", padx=(SPACING['sm'], 0))
    
    def _open_charts_folder(self):
        """Open charts folder in file explorer"""
        charts_dir = Path("charts")
        if charts_dir.exists():
            import os
            import platform
            
            if platform.system() == "Windows":
                os.startfile(charts_dir)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open {charts_dir}")
            else:  # Linux
                os.system(f"xdg-open {charts_dir}")
        else:
            messagebox.showwarning("Not Found", "Charts folder not found!")
    
    def _export_results(self):
        """Export results to text file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"analysis_{self.analysis_result.resume.filename.split('.')[0]}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write("JOB MARKET ANALYZER - ANALYSIS REPORT\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(self.analysis_result.get_detailed_summary())
                    f.write("\n\n" + "=" * 70 + "\n")
                    f.write("LEARNING PATH\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(self.analysis_result.learning_path)
                
                messagebox.showinfo("Success", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def _new_analysis(self):
        """Start new analysis"""
        self.on_new_analysis_callback()