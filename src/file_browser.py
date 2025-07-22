"""
Custom File Browser Component for Streamlit

This module provides a user-friendly file browser interface
that mimics a native file explorer experience.
"""

import streamlit as st
import os
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple

def create_file_browser(
    start_path: str = ".",
    title: str = "📁 File Browser",
    file_types: List[str] = None,
    max_files: int = 100
) -> Optional[str]:
    """
    Create a custom file browser component
    
    Args:
        start_path: Starting directory path
        title: Title for the browser
        file_types: List of file extensions to show (e.g., ['.csv', '.txt'])
        max_files: Maximum number of files to display
    
    Returns:
        Selected folder path or None
    """
    
    if file_types is None:
        file_types = ['.csv']
    
    st.markdown(f"### {title}")
    
    # Initialize session state for navigation
    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.path.abspath(start_path)
    
    if 'browser_history' not in st.session_state:
        st.session_state.browser_history = [st.session_state.current_path]
    
    if 'history_index' not in st.session_state:
        st.session_state.history_index = 0
    
    # Navigation controls
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("⬆️ Up", help="Go to parent directory"):
            parent = os.path.dirname(st.session_state.current_path)
            if parent != st.session_state.current_path:
                st.session_state.current_path = parent
                st.session_state.browser_history.append(parent)
                st.session_state.history_index += 1
                st.rerun()
    
    with col2:
        if st.button("🏠 Home", help="Go to home directory"):
            home = os.path.expanduser("~")
            st.session_state.current_path = home
            st.session_state.browser_history.append(home)
            st.session_state.history_index += 1
            st.rerun()
    
    with col3:
        if st.button("📂 Root", help="Go to root directory"):
            root = "/" if os.name != 'nt' else "C:\\"
            st.session_state.current_path = root
            st.session_state.browser_history.append(root)
            st.session_state.history_index += 1
            st.rerun()
    
    with col4:
        # Path input for direct navigation
        new_path = st.text_input(
            "Enter path:",
            value=st.session_state.current_path,
            help="Enter a directory path to navigate to"
        )
        if new_path and new_path != st.session_state.current_path and os.path.exists(new_path):
            st.session_state.current_path = new_path
            st.session_state.browser_history.append(new_path)
            st.session_state.history_index += 1
            st.rerun()
    
    # Current path display
    st.markdown(f"**📍 Current Location:** `{st.session_state.current_path}`")
    
    try:
        # Get directory contents
        items = os.listdir(st.session_state.current_path)
        
        # Separate directories and files
        directories = []
        files = []
        
        for item in items:
            item_path = os.path.join(st.session_state.current_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            elif os.path.isfile(item_path):
                # Check if file type matches
                if any(item.lower().endswith(ext.lower()) for ext in file_types):
                    files.append(item)
        
        # Sort items
        directories.sort()
        files.sort()
        
        # Display directories
        if directories:
            st.markdown("**📁 Folders:**")
            
            # Create columns for directory buttons
            cols = st.columns(3)
            for i, directory in enumerate(directories[:9]):  # Show first 9 directories
                col_idx = i % 3
                with cols[col_idx]:
                    if st.button(f"📁 {directory}", key=f"dir_{directory}"):
                        new_path = os.path.join(st.session_state.current_path, directory)
                        st.session_state.current_path = new_path
                        st.session_state.browser_history.append(new_path)
                        st.session_state.history_index += 1
                        st.rerun()
            
            if len(directories) > 9:
                st.markdown(f"*... and {len(directories) - 9} more folders*")
        
        # Display files
        if files:
            st.markdown(f"**📄 Files ({len(files)} found):**")
            
            # File selection
            selected_files = st.multiselect(
                "Select files:",
                files[:max_files],
                help=f"Select one or more {', '.join(file_types)} files"
            )
            
            # Show file details
            if selected_files:
                st.markdown("**✅ Selected Files:**")
                file_details = []
                
                for file in selected_files:
                    file_path = os.path.join(st.session_state.current_path, file)
                    try:
                        size = os.path.getsize(file_path)
                        size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
                        file_details.append(f"• {file} ({size_str})")
                    except:
                        file_details.append(f"• {file}")
                
                for detail in file_details:
                    st.markdown(detail)
                
                # Return the current directory path if files are selected
                if selected_files:
                    return st.session_state.current_path
        
        # Quick access buttons for common locations
        st.markdown("---")
        st.markdown("**🚀 Quick Access:**")
        
        quick_cols = st.columns(4)
        quick_paths = {
            "📂 Data": "data",
            "📂 Test": "data/test_data",
            "📂 Sample": "data/sample_data",
            "📂 Denmark": "data/Denmark"
        }
        
        for i, (name, path) in enumerate(quick_paths.items()):
            with quick_cols[i]:
                if st.button(name, key=f"quick_{path}"):
                    if os.path.exists(path):
                        st.session_state.current_path = os.path.abspath(path)
                        st.session_state.browser_history.append(st.session_state.current_path)
                        st.session_state.history_index += 1
                        st.rerun()
                    else:
                        st.error(f"Path not found: {path}")
        
        # No files found message
        if not directories and not files:
            st.info("📂 This folder is empty")
        
        # File count summary
        if files:
            st.markdown(f"📊 **Summary:** {len(files)} {', '.join(file_types)} files found")
        
    except PermissionError:
        st.error("❌ Permission denied accessing this directory")
        return None
    except Exception as e:
        st.error(f"❌ Error accessing directory: {str(e)}")
        return None
    
    return None

def create_simple_folder_picker(
    title: str = "📁 Select Data Folder",
    default_path: str = "data/test_data"
) -> Optional[str]:
    """
    Create a simple folder picker with common options
    
    Args:
        title: Title for the picker
        default_path: Default path to show
    
    Returns:
        Selected folder path or None
    """
    
    # Initialize popup state
    if 'file_browser_popup_open' not in st.session_state:
        st.session_state.file_browser_popup_open = False
    
    # If popup is open, show the popup interface
    if st.session_state.file_browser_popup_open:
        return _show_popup_file_explorer()
    
    # Main interface (when popup is closed)
    st.markdown(f"### {title}")
    
    # Option 1: Native File Uploader (BEST UX - Native file browser)
    st.markdown("**Option 1: Native File Browser (Recommended)**")
    st.info("💡 **Best Experience**: Opens your system's native file browser for easy file selection")
    
    uploaded_files = st.file_uploader(
        "📁 Browse and select CSV files:",
        type=['csv'],
        accept_multiple_files=True,
        help="Click to open your system's file browser and select CSV files"
    )
    
    if uploaded_files:
        st.success(f"✅ Selected {len(uploaded_files)} files")
        
        # Show selected files in a compact list
        st.markdown("**📄 Selected Files:**")
        for file in uploaded_files:
            st.markdown(f"• {file.name}")
        
        # Store uploaded files in session state
        st.session_state.uploaded_files = uploaded_files
        
        # Return a special identifier for uploaded files
        return "UPLOADED_FILES"
    
    # Option 2: Quick Access (for common data folders)
    st.markdown("**Option 2: Quick Access**")
    st.info("💡 **Quick Start**: Select from common data folders")
    
    # Quick access to common folders
    quick_folders = [
        ("data/test_data", "📁 Test Data"),
        ("data/sample_data", "📁 Sample Data"),
        (os.path.expanduser("~/Desktop"), "🖥️ Desktop"),
        (os.path.expanduser("~/Downloads"), "⬇️ Downloads"),
    ]
    
    # Filter to only show existing folders
    available_quick_folders = [(path, label) for path, label in quick_folders if os.path.exists(path)]
    
    if available_quick_folders:
        selected_quick = st.selectbox(
            "Choose a folder:",
            options=[path for path, label in available_quick_folders],
            format_func=lambda x: next(label for path, label in available_quick_folders if path == x),
            help="Select a folder to browse its contents"
        )
        
        if selected_quick:
            selected_path = selected_quick
            
            try:
                # Get CSV files from the selected folder
                csv_files = get_csv_files_from_folder(selected_path)
                
                if csv_files:
                    # Auto-select all files by default, but allow deselection
                    if len(csv_files) <= 20:
                        # For folders with 20 or fewer files, show all with auto-selection
                        default_selection = csv_files
                        available_files = csv_files
                    else:
                        # For folders with more than 20 files, show first 20 with option to see more
                        default_selection = csv_files[:20]
                        available_files = csv_files[:20]
                        st.warning(f"⚠️ Showing first 20 of {len(csv_files)} files. Use 'Select All' to include all files.")
                    
                    # File selection with auto-selection
                    selected_files = st.multiselect(
                        f"📄 CSV Files ({len(csv_files)} found) - Select files (all selected by default):",
                        available_files,
                        default=default_selection,
                        help=f"All CSV files are selected by default. Deselect files you don't want to analyze."
                    )
                    
                    # Show file count and selection controls
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Select All", key="select_all_quick"):
                            st.session_state.selected_files_quick = available_files
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Deselect All", key="deselect_all_quick"):
                            st.session_state.selected_files_quick = []
                            st.rerun()
                    
                    # Show selected files with count
                    if selected_files:
                        st.success(f"✅ {len(selected_files)} files selected for analysis")
                        
                        # Option to use this folder
                        if st.button("Analyze Selected Files", key="use_current"):
                            st.session_state.selected_files_quick = selected_files
                            return selected_path
                    else:
                        st.warning("⚠️ No files selected. Please select at least one CSV file.")
                else:
                    st.info("📂 No CSV files found in this folder")
                    
            except PermissionError:
                st.warning("⚠️ Permission denied accessing folder contents")
            except Exception as e:
                st.error(f"❌ Error accessing folder: {str(e)}")
    else:
        st.error(f"❌ Folder not found: {selected_path}")
    
    # Option 3: Custom File Explorer (Advanced)
    st.markdown("**Option 3: Custom File Explorer (Advanced)**")
    st.info("💡 **Advanced**: Full folder navigation with custom interface")
    
    # Button to open popup
    if st.button("Open Custom File Explorer", type="secondary"):
        st.session_state.file_browser_popup_open = True
        st.rerun()
    
    # Option 4: Manual path input
    st.markdown("**Option 4: Manual Path (Advanced)**")
    
    # Use a checkbox instead of expander to avoid nesting issues
    show_manual_input = st.checkbox("🔧 Show advanced manual path input", help="Check to enter a custom folder path")
    
    if show_manual_input:
        manual_path = st.text_input(
            "Enter folder path:",
            value=default_path,
            help="Enter the full path to your data folder"
        )
        
        if manual_path:
            if os.path.exists(manual_path):
                st.success(f"✅ Path valid: {os.path.abspath(manual_path)}")
                return manual_path
            else:
                st.error(f"❌ Path not found: {manual_path}")
    
    return None


def _show_popup_file_explorer() -> Optional[str]:
    """
    Show the popup file explorer interface
    """
    # Create a visual separator for the popup
    st.markdown("---")
    st.markdown("### 🗂️ File Explorer (Pop-up Mode)")
    st.markdown("*This is the pop-up file explorer interface*")
    st.markdown("---")
    
    # Close button at the top
    col1, col2, col3 = st.columns([1, 3, 1])
    with col3:
        if st.button("❌ Close Pop-up", key="close_popup"):
            st.session_state.file_browser_popup_open = False
            st.rerun()
    
    # Initialize or get current browse path
    if 'current_browse_path' not in st.session_state:
        st.session_state.current_browse_path = os.path.expanduser("~")
    
    # Navigation controls in a compact layout
    st.markdown("**🎮 Navigation:**")
    nav_cols = st.columns(5)
    
    with nav_cols[0]:
        if st.button("⬆️ Up", help="Go to parent directory"):
            parent = os.path.dirname(st.session_state.current_browse_path)
            if parent != st.session_state.current_browse_path:
                st.session_state.current_browse_path = parent
                if 'explorer_dir_page' in st.session_state:
                    st.session_state.explorer_dir_page = 0
                st.rerun()
    
    with nav_cols[1]:
        if st.button("🏠 Home", help="Go to home directory"):
            st.session_state.current_browse_path = os.path.expanduser("~")
            if 'explorer_dir_page' in st.session_state:
                st.session_state.explorer_dir_page = 0
            st.rerun()
    
    with nav_cols[2]:
        if st.button("📂 Root", help="Go to root directory"):
            root = "/" if os.name != 'nt' else "C:\\"
            st.session_state.current_browse_path = root
            if 'explorer_dir_page' in st.session_state:
                st.session_state.explorer_dir_page = 0
            st.rerun()
    
    with nav_cols[3]:
        if st.button("🔄 Refresh", help="Refresh current directory"):
            st.rerun()
    
    with nav_cols[4]:
        if st.button("✅ Select Folder", type="primary", help="Use current folder"):
            st.session_state.file_browser_popup_open = False
            return st.session_state.current_browse_path
    
    # Current path display with breadcrumb navigation
    st.markdown("**📍 Current Location:**")
    
    # Create breadcrumb navigation
    path_parts = st.session_state.current_browse_path.split(os.sep)
    if os.name == 'nt' and st.session_state.current_browse_path.startswith('\\'):
        # Windows network path
        path_parts = ['\\\\'] + [p for p in path_parts if p]
    elif os.name == 'nt':
        # Windows local path
        path_parts = [path_parts[0] + '\\'] + path_parts[1:]
    
    breadcrumb_cols = st.columns(len(path_parts))
    for i, part in enumerate(path_parts):
        with breadcrumb_cols[i]:
            if i == 0:
                # Root/home
                if st.button(f"🏠 {part}", key=f"breadcrumb_{i}"):
                    st.session_state.current_browse_path = part
                    if 'explorer_dir_page' in st.session_state:
                        st.session_state.explorer_dir_page = 0
                    st.rerun()
            else:
                # Build path up to this point
                current_path = os.sep.join(path_parts[:i+1])
                if st.button(f"📁 {part}", key=f"breadcrumb_{i}"):
                    st.session_state.current_browse_path = current_path
                    if 'explorer_dir_page' in st.session_state:
                        st.session_state.explorer_dir_page = 0
                    st.rerun()
    
    # Path input for direct navigation
    new_path = st.text_input(
        "Enter path to navigate:",
        value=st.session_state.current_browse_path,
        help="Enter a directory path to navigate to"
    )
    if new_path and new_path != st.session_state.current_browse_path and os.path.exists(new_path):
        st.session_state.current_browse_path = new_path
        if 'explorer_dir_page' in st.session_state:
            st.session_state.explorer_dir_page = 0
        st.rerun()
    
    # Show current directory contents
    try:
        items = os.listdir(st.session_state.current_browse_path)
        
        # Separate directories and files
        directories = []
        csv_files = []
        
        for item in items:
            item_path = os.path.join(st.session_state.current_browse_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            elif os.path.isfile(item_path) and item.lower().endswith('.csv'):
                csv_files.append(item)
        
        # Sort items
        directories.sort()
        csv_files.sort()
        
        # Display directories with pagination
        if directories:
            st.markdown("**📁 Folders:**")
            
            # Initialize pagination state for file explorer
            if 'explorer_dir_page' not in st.session_state:
                st.session_state.explorer_dir_page = 0
            
            # Pagination settings
            folders_per_page = 9
            total_pages = (len(directories) + folders_per_page - 1) // folders_per_page
            
            # Calculate current page items
            start_idx = st.session_state.explorer_dir_page * folders_per_page
            end_idx = min(start_idx + folders_per_page, len(directories))
            current_dirs = directories[start_idx:end_idx]
            
            # Create columns for directory buttons
            cols = st.columns(3)
            for i, directory in enumerate(current_dirs):
                col_idx = i % 3
                with cols[col_idx]:
                    if st.button(f"📁 {directory}", key=f"dir_{directory}"):
                        new_path = os.path.join(st.session_state.current_browse_path, directory)
                        st.session_state.current_browse_path = new_path
                        # Reset pagination when entering new directory
                        st.session_state.explorer_dir_page = 0
                        st.rerun()
            
            # Pagination controls for file explorer
            if total_pages > 1:
                st.markdown("**📄 Folder Navigation:**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("⬅️ Previous", disabled=st.session_state.explorer_dir_page == 0, key="prev_explorer"):
                        st.session_state.explorer_dir_page = max(0, st.session_state.explorer_dir_page - 1)
                        st.rerun()
                
                with col2:
                    st.markdown(f"**Page {st.session_state.explorer_dir_page + 1} of {total_pages}**")
                
                with col3:
                    if st.button("➡️ Next", disabled=st.session_state.explorer_dir_page >= total_pages - 1, key="next_explorer"):
                        st.session_state.explorer_dir_page = min(total_pages - 1, st.session_state.explorer_dir_page + 1)
                        st.rerun()
                
                with col4:
                    if st.button("🏠 Reset", key="reset_explorer"):
                        st.session_state.explorer_dir_page = 0
                        st.rerun()
                
                # Show total count
                st.markdown(f"*📊 Showing {start_idx + 1}-{end_idx} of {len(directories)} folders*")
        
        # Display CSV files
        if csv_files:
            # Auto-select all files by default, but allow deselection
            if len(csv_files) <= 20:
                # For folders with 20 or fewer files, show all with auto-selection
                default_selection = csv_files
                available_files = csv_files
            else:
                # For folders with more than 20 files, show first 20 with option to see more
                default_selection = csv_files[:20]
                available_files = csv_files[:20]
                st.warning(f"⚠️ Showing first 20 of {len(csv_files)} files. Use 'Select All' to include all files.")
            
            # File selection with auto-selection
            selected_files = st.multiselect(
                f"📄 CSV Files ({len(csv_files)} found) - Select files (all selected by default):",
                available_files,
                default=default_selection,
                help=f"All CSV files are selected by default. Deselect files you don't want to analyze."
            )
            
            # Show file count and selection controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Select All", key="select_all_explorer"):
                    st.session_state.selected_files_explorer = available_files
                    st.rerun()
            
            with col2:
                if st.button("❌ Deselect All", key="deselect_all_explorer"):
                    st.session_state.selected_files_explorer = []
                    st.rerun()
            
            with col3:
                if len(csv_files) > 20:
                    if st.button("📄 Show All Files", key="show_all_explorer"):
                        st.session_state.show_all_files_explorer = True
                        st.rerun()
            
            # Show selected files with count
            if selected_files:
                st.success(f"✅ {len(selected_files)} files selected for analysis")
                
                # Option to use this folder
                if st.button("Analyze Selected Files", key="use_explorer"):
                    st.session_state.selected_files_explorer = selected_files
                    st.session_state.file_browser_popup_open = False
                    return st.session_state.current_browse_path
            else:
                st.warning("⚠️ No files selected. Please select at least one CSV file.")
        
        # No files found message
        if not directories and not csv_files:
            st.info("📂 This folder is empty")
        
        # File count summary
        if csv_files:
            st.markdown(f"📊 **Summary:** {len(csv_files)} CSV files found in current folder")
    
    except PermissionError:
        st.error("❌ Permission denied accessing this directory")
    except Exception as e:
        st.error(f"❌ Error accessing directory: {str(e)}")
    
    return None

def get_csv_files_from_folder(folder_path: str) -> List[str]:
    """
    Get all CSV files from a folder
    
    Args:
        folder_path: Path to the folder
    
    Returns:
        List of CSV file paths
    """
    
    if not os.path.exists(folder_path):
        return []
    
    try:
        csv_files = []
        for file in os.listdir(folder_path):
            if file.lower().endswith('.csv'):
                csv_files.append(os.path.join(folder_path, file))
        return sorted(csv_files)
    except PermissionError:
        st.error("❌ Permission denied accessing folder")
        return []
    except Exception as e:
        st.error(f"❌ Error accessing folder: {str(e)}")
        return [] 