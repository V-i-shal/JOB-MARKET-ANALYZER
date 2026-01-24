"""
GUI Application Launcher
Main entry point for the graphical user interface
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import JobMarketAnalyzer
from src.gui.main_window import MainWindow
from src.gui.results_window import ResultsWindow
from src.gui.styles import WINDOW


class JobMarketAnalyzerGUI(ctk.CTk):
    """
    Main GUI Application for Job Market Analyzer
    """
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Job Market Analyzer - AI-Powered Career Analysis")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.minsize(WINDOW['min_width'], WINDOW['min_height'])
        
        # Initialize analyzer
        print("Initializing analyzer...")
        self.analyzer = JobMarketAnalyzer()
        print("Analyzer ready!")
        
        # Current view
        self.current_view = None
        
        # Processing flag
        self.is_processing = False
        
        # Show main window
        self._show_main_window()
    
    def _show_main_window(self):
        """Show the main upload window"""
        # Clear current view
        if self.current_view:
            self.current_view.destroy()
        
        # Create main window
        self.current_view = MainWindow(self, on_analyze_callback=self._start_analysis)
        self.current_view.pack(fill="both", expand=True)
        
        print("Main window displayed")
    
    def _start_analysis(self, file_path: str, domain: str):
        """
        Start resume analysis in background thread.
        
        Args:
            file_path: Path to resume file
            domain: Job domain selected
        """
        if self.is_processing:
            messagebox.showwarning("Processing", "Analysis already in progress!")
            return
        
        self.is_processing = True
        print(f"\nStarting analysis:")
        print(f"  File: {file_path}")
        print(f"  Domain: {domain}")
        
        # Progress callback
        def progress_callback(message, percentage):
            # Update UI from main thread
            self.after(0, lambda m=message, p=percentage: self._update_progress(m, p))
        
        # Analysis thread
        def analysis_thread():
            try:
                print("Analysis thread started...")
                result = self.analyzer.process_resume(
                    file_path=file_path,
                    job_domain=domain,
                    num_jobs=20,  # Fetch 20 jobs for GUI (faster)
                    progress_callback=progress_callback
                )
                
                print(f"Analysis complete! Result: {result is not None}")
                
                if result:
                    # Generate charts
                    print("Generating charts...")
                    charts = self.analyzer.generate_charts(output_dir="charts")
                    print(f"Charts generated: {len(charts)}")
                    
                    # Show results on main thread
                    self.after(0, lambda r=result: self._show_results(r))
                else:
                    self.after(0, lambda: self._show_error("Analysis failed. Please check the logs."))
                    
            except Exception as e:
                print(f"Error in analysis thread: {e}")
                import traceback
                traceback.print_exc()
                self.after(0, lambda: self._show_error(f"Error during analysis:\n{str(e)}"))
            finally:
                self.is_processing = False
        
        # Start thread
        thread = threading.Thread(target=analysis_thread, daemon=True)
        thread.start()
        print("Background thread started")
    
    def _update_progress(self, message: str, percentage: int):
        """Update progress bar (called from main thread)"""
        try:
            if isinstance(self.current_view, MainWindow):
                self.current_view.update_progress(message, percentage)
                print(f"[{percentage:3d}%] {message}")
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def _show_results(self, result):
        """Show results window"""
        print("Displaying results window...")
        
        # Clear current view
        if self.current_view:
            self.current_view.destroy()
        
        # Create results window
        self.current_view = ResultsWindow(
            self,
            analysis_result=result,
            on_new_analysis_callback=self._show_main_window
        )
        self.current_view.pack(fill="both", expand=True)
        
        print("Results window displayed")
    
    def _show_error(self, message: str):
        """Show error message and reset"""
        messagebox.showerror("Error", message)
        print(f"Error shown: {message}")
        
        # Reset main window
        if isinstance(self.current_view, MainWindow):
            self.current_view.reset()
        
        self.is_processing = False
    
    def on_closing(self):
        """Handle window close event"""
        if self.is_processing:
            if not messagebox.askyesno("Analysis in Progress", "Analysis is still running. Are you sure you want to quit?"):
                return
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            print("Cleaning up...")
            self.analyzer.cleanup()
            self.destroy()


def main():
    """Main entry point for GUI application"""
    print("=" * 70)
    print("Job Market Analyzer - GUI Mode")
    print("=" * 70)
    
    # Configure CustomTkinter
    ctk.set_appearance_mode("light")  # "light" or "dark"
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = JobMarketAnalyzerGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("\nGUI started. Waiting for user input...")
    app.mainloop()
    
    print("Application closed.")


if __name__ == "__main__":
    main()