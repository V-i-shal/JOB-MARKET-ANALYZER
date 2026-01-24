"""
Main Entry Point
Choose between CLI and GUI mode
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point with mode selection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Job Market Analyzer")
    parser.add_argument(
        "--mode",
        choices=["gui", "cli"],
        default="gui",
        help="Run in GUI or CLI mode (default: gui)"
    )
    parser.add_argument(
        "resume",
        nargs="?",
        help="Resume file path (CLI mode only)"
    )
    parser.add_argument(
        "--domain",
        default="Software Developer",
        help="Job domain (CLI mode only)"
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=50,
        help="Number of jobs to analyze (CLI mode only)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        # Launch GUI
        from src.gui_app import main as gui_main
        gui_main()
    else:
        # Launch CLI
        if not args.resume:
            print("Error: Resume file required in CLI mode")
            print("Usage: python main.py --mode cli <resume_file> [--domain DOMAIN] [--jobs NUM]")
            sys.exit(1)
        
        from src.main import main as cli_main
        sys.argv = ["main.py", args.resume, args.domain, str(args.jobs)]
        cli_main()


if __name__ == "__main__":
    main()