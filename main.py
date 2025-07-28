import flet as ft
from flet import *
import json
import os
from datetime import datetime
from file_manager import FileManager
from ai_analyzer import AIAnalyzer

class AiCheat2ShooterApp:
    def __init__(self):
        self.current_page = "dashboard"
        self.theme_mode = "light"
        self.config = self.load_config()
        
        # Initialize modules
        self.file_manager = FileManager()
        self.ai_analyzer = AIAnalyzer()
        
        # Analysis results
        self.current_analysis_results = None
        
    def load_config(self):
        """Load application configuration"""
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return {
            "theme": "light",
            "window_size": {"width": 1200, "height": 800},
            "ai_model": "default",
            "export_path": "./exports"
        }
    
    def save_config(self):
        """Save application configuration"""
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def main(self, page: ft.Page):
        page.title = "AiCheat2Shooter - AI Desktop Application"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.window_maximizable = True
        page.padding = 0
        page.spacing = 0
        
        # Navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.AI_OUTLINED,
                    selected_icon=ft.icons.AI,
                    label="AI Analysis",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OUTLINED,
                    selected_icon=ft.icons.FOLDER,
                    label="Files",
                ),
            ],
            on_change=self.navigation_change
        )
        
        # Main content area
        self.content_area = ft.Container(
            content=self.get_dashboard_content(),
            expand=True,
            padding=20
        )
        
        # Status bar
        status_bar = ft.Container(
            content=ft.Row([
                ft.Text("Ready", size=12),
                ft.VerticalDivider(width=1),
                ft.Text(f"Model: {self.config.get('ai_model', 'default')}", size=12),
                ft.VerticalDivider(width=1),
                ft.Text(f"Theme: {self.theme_mode}", size=12),
                ft.VerticalDivider(width=1),
                ft.Text(f"Files: {len(self.file_manager.get_files())}", size=12),
            ]),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=10,
            height=40
        )
        
        # Main layout
        page.add(
            ft.Row([
                nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column([
                    self.content_area,
                    status_bar
                ], expand=True)
            ], expand=True)
        )
        
        page.update()
    
    def navigation_change(self, e):
        """Handle navigation changes"""
        index = e.control.selected_index
        pages = ["dashboard", "ai_analysis", "settings", "files"]
        self.current_page = pages[index]
        
        # Update content based on selected page
        if self.current_page == "dashboard":
            self.content_area.content = self.get_dashboard_content()
        elif self.current_page == "ai_analysis":
            self.content_area.content = self.get_ai_analysis_content()
        elif self.current_page == "settings":
            self.content_area.content = self.get_settings_content()
        elif self.current_page == "files":
            self.content_area.content = self.get_files_content()
        
        self.content_area.update()
    
    def get_dashboard_content(self):
        """Dashboard page content"""
        stats = self.file_manager.get_storage_stats()
        ai_stats = self.ai_analyzer.get_model_statistics()
        
        return ft.Column([
            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                self.create_stat_card("AI Models", f"{len(self.ai_analyzer.get_available_models())} Available", ft.icons.AI),
                self.create_stat_card("Files Processed", str(stats["total_files"]), ft.icons.FILE_COPY),
                self.create_stat_card("Analysis Time", f"{ai_stats.get('average_analysis_time', 0):.1f}s avg", ft.icons.TIMER),
                self.create_stat_card("Storage Used", f"{stats['total_size_mb']:.1f} MB", ft.icons.STORAGE),
            ], spacing=20),
            ft.Divider(),
            ft.Text("Recent Activity", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.get_recent_activity_list(),
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                padding=10
            )
        ])
    
    def get_recent_activity_list(self):
        """Get recent activity list"""
        activities = []
        
        # Add recent analysis results
        recent_analyses = self.ai_analyzer.get_analysis_history(limit=3)
        for analysis in recent_analyses:
            activities.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.AI),
                    title=ft.Text(f"AI Analysis - {analysis.get('risk_level', 'unknown').title()} Risk"),
                    subtitle=ft.Text(f"Confidence: {analysis.get('confidence_score', 0):.2f}"),
                    trailing=ft.Text(f"{analysis.get('analysis_time', 0):.1f}s")
                )
            )
        
        # Add recent file activities
        recent_files = self.file_manager.get_files()[-2:]
        for file in recent_files:
            activities.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FILE_DOWNLOAD),
                    title=ft.Text(f"File Added: {file['original_name']}"),
                    subtitle=ft.Text(f"Size: {file['size']} bytes"),
                    trailing=ft.Text(file['upload_date'][:10])
                )
            )
        
        if not activities:
            activities.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INFO),
                    title=ft.Text("No recent activity"),
                    subtitle=ft.Text("Start by uploading files and running analysis")
                )
            )
        
        return ft.ListView(activities, height=200)
    
    def get_ai_analysis_content(self):
        """AI Analysis page content"""
        return ft.Column([
            ft.Text("AI Analysis", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Upload Files",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=self.upload_files
                ),
                ft.ElevatedButton(
                    "Start Analysis",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=self.start_analysis
                ),
                ft.ElevatedButton(
                    "Export Results",
                    icon=ft.icons.DOWNLOAD,
                    on_click=self.export_results
                ),
            ], spacing=10),
            ft.Divider(),
            ft.Text("Analysis Results", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.get_analysis_results_content(),
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                padding=20
            )
        ])
    
    def get_analysis_results_content(self):
        """Get analysis results content"""
        if not self.current_analysis_results:
            return ft.Text("No analysis results yet. Upload files and start analysis.")
        
        if isinstance(self.current_analysis_results, list):
            # Batch analysis results
            return ft.Column([
                ft.Text(f"Batch Analysis Results ({len(self.current_analysis_results)} files)", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ListView([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.AI),
                        title=ft.Text(f"File: {result.get('file_path', 'Unknown')}"),
                        subtitle=ft.Text(f"Risk: {result.get('risk_level', 'Unknown')} | Confidence: {result.get('confidence_score', 0):.2f}"),
                        trailing=ft.Text(f"{result.get('analysis_time', 0):.1f}s")
                    ) for result in self.current_analysis_results
                ], height=300)
            ])
        else:
            # Single analysis result
            result = self.current_analysis_results
            return ft.Column([
                ft.Text(f"Analysis Result", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"File: {result.get('file_path', 'Unknown')}"),
                ft.Text(f"Risk Level: {result.get('risk_level', 'Unknown')}"),
                ft.Text(f"Confidence: {result.get('confidence_score', 0):.2f}"),
                ft.Text(f"Analysis Time: {result.get('analysis_time', 0):.1f}s"),
                ft.Divider(),
                ft.Text("Detected Patterns:", size=14, weight=ft.FontWeight.BOLD),
                ft.ListView([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.WARNING),
                        title=ft.Text(pattern.get('pattern', 'Unknown')),
                        subtitle=ft.Text(f"Confidence: {pattern.get('confidence', 0):.2f}")
                    ) for pattern in result.get('detected_patterns', [])
                ], height=150)
            ])
    
    def get_settings_content(self):
        """Settings page content"""
        return ft.Column([
            ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("Theme", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Radio(value="light", label="Light", group="theme"),
                        ft.Radio(value="dark", label="Dark", group="theme"),
                    ]),
                    ft.Divider(),
                    ft.Text("AI Model", size=16, weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        label="Select AI Model",
                        options=[
                            ft.dropdown.Option(model, model.title()) 
                            for model in self.ai_analyzer.get_available_models()
                        ],
                        value=self.config.get("ai_model", "default"),
                        on_change=self.on_model_change
                    ),
                    ft.Divider(),
                    ft.Text("Export Settings", size=16, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="Export Path",
                        value=self.config.get("export_path", "./exports"),
                        width=300
                    ),
                ]),
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                padding=20
            )
        ])
    
    def get_files_content(self):
        """Files page content"""
        files = self.file_manager.get_files()
        
        return ft.Column([
            ft.Text("File Management", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Add Files",
                    icon=ft.icons.ADD,
                    on_click=self.add_files
                ),
                ft.ElevatedButton(
                    "Create Folder",
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    on_click=self.create_folder
                ),
            ], spacing=10),
            ft.Divider(),
            ft.Text(f"Files ({len(files)})", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.get_files_list(files),
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=8,
                padding=10
            )
        ])
    
    def get_files_list(self, files):
        """Get files list content"""
        if not files:
            return ft.Text("No files uploaded yet.")
        
        return ft.ListView([
            ft.ListTile(
                leading=ft.Icon(ft.icons.FILE_COPY),
                title=ft.Text(file['original_name']),
                subtitle=ft.Text(f"Size: {file['size']} bytes | Category: {file['category']}"),
                trailing=ft.Text(file['upload_date'][:10]),
                on_click=lambda e, file_id=file['id']: self.analyze_file(file_id)
            ) for file in files
        ], height=400)
    
    def create_stat_card(self, title, value, icon):
        """Create a statistics card"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=32, color=ft.colors.PRIMARY),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=150,
            height=100,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            padding=20,
            alignment=ft.alignment.center
        )
    
    def upload_files(self, e):
        """Handle file upload"""
        # TODO: Implement file picker dialog
        print("Upload files clicked")
    
    def start_analysis(self, e):
        """Handle analysis start"""
        files = self.file_manager.get_files()
        if not files:
            print("No files to analyze")
            return
        
        # Analyze all files
        file_paths = [file['path'] for file in files]
        self.current_analysis_results = self.ai_analyzer.analyze_batch(file_paths)
        
        # Update UI
        if self.current_page == "ai_analysis":
            self.content_area.content = self.get_ai_analysis_content()
            self.content_area.update()
    
    def export_results(self, e):
        """Handle results export"""
        if not self.current_analysis_results:
            print("No results to export")
            return
        
        try:
            export_path = self.file_manager.export_results(
                self.current_analysis_results, 
                "analysis_results", 
                "json"
            )
            print(f"Results exported to: {export_path}")
        except Exception as e:
            print(f"Export failed: {e}")
    
    def add_files(self, e):
        """Handle adding files"""
        # TODO: Implement file picker dialog
        print("Add files clicked")
    
    def create_folder(self, e):
        """Handle folder creation"""
        # TODO: Implement folder creation dialog
        print("Create folder clicked")
    
    def analyze_file(self, file_id):
        """Analyze specific file"""
        file_record = self.file_manager.get_file_by_id(file_id)
        if file_record:
            self.current_analysis_results = self.ai_analyzer.analyze_file(file_record['path'])
            
            # Switch to analysis page
            self.current_page = "ai_analysis"
            self.content_area.content = self.get_ai_analysis_content()
            self.content_area.update()
    
    def on_model_change(self, e):
        """Handle AI model change"""
        model_name = e.control.value
        if self.ai_analyzer.set_model(model_name):
            self.config["ai_model"] = model_name
            self.save_config()
            print(f"AI model changed to: {model_name}")

def main():
    app = AiCheat2ShooterApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()
