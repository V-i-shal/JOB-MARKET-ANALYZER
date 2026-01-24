"""
Chart Generator Utility
Creates interactive charts using Plotly for data visualization
"""

from typing import List, Dict, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from loguru import logger


class ChartGenerator:
    """
    Generates interactive charts for job market analysis visualization.
    Uses Plotly for modern, interactive charts.
    """
    
    # Color scheme
    COLOR_MATCH = '#27ae60'      # Green for matching skills
    COLOR_MISSING = '#e74c3c'    # Red for missing skills
    COLOR_INFO = '#3498db'        # Blue for information
    COLOR_SECONDARY = '#95a5a6'   # Gray for secondary info
    
    # Chart dimensions
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    
    @staticmethod
    def create_skill_match_bar_chart(
        matching_count: int,
        missing_count: int,
        title: str = "Skill Match Analysis"
    ) -> go.Figure:
        """
        Create a bar chart showing skill match vs missing skills.
        
        Args:
            matching_count: Number of matching skills
            missing_count: Number of missing skills
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        try:
            # Calculate percentages
            total = matching_count + missing_count
            if total == 0:
                logger.warning("No skills to display in chart")
                return ChartGenerator._create_empty_chart("No data available")
            
            match_pct = (matching_count / total) * 100
            missing_pct = (missing_count / total) * 100
            
            # Create data
            categories = ['Skills You Have', 'Skills to Learn']
            values = [match_pct, missing_pct]
            counts = [matching_count, missing_count]
            colors = [ChartGenerator.COLOR_MATCH, ChartGenerator.COLOR_MISSING]
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    text=[f'{v:.1f}%<br>({c} skills)' for v, c in zip(values, counts)],
                    textposition='auto',
                    marker_color=colors,
                    hovertemplate='<b>%{x}</b><br>' +
                                 '%{y:.1f}%<br>' +
                                 '<extra></extra>'
                )
            ])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Category",
                yaxis_title="Percentage (%)",
                yaxis=dict(range=[0, 100]),
                height=ChartGenerator.DEFAULT_HEIGHT,
                width=ChartGenerator.DEFAULT_WIDTH,
                showlegend=False,
                template='plotly_white',
                hovermode='x'
            )
            
            logger.info("Skill match bar chart created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating skill match chart: {e}")
            return ChartGenerator._create_empty_chart("Error creating chart")
    
    @staticmethod
    def create_top_missing_skills_chart(
        skills_data: List[Dict[str, any]],
        top_n: int = 10,
        title: str = "Top Missing Skills"
    ) -> go.Figure:
        """
        Create a horizontal bar chart showing top missing skills.
        
        Args:
            skills_data: List of dicts with 'name' and 'frequency' keys
            top_n: Number of top skills to display
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        try:
            if not skills_data:
                logger.warning("No missing skills data to display")
                return ChartGenerator._create_empty_chart("No missing skills found")
            
            # Sort by frequency and take top N
            sorted_skills = sorted(
                skills_data, 
                key=lambda x: x.get('frequency', 0), 
                reverse=True
            )[:top_n]
            
            # Extract data
            skill_names = [s['name'] for s in sorted_skills]
            frequencies = [s['frequency'] for s in sorted_skills]
            
            # Create horizontal bar chart
            fig = go.Figure(data=[
                go.Bar(
                    y=skill_names[::-1],  # Reverse for top-to-bottom display
                    x=frequencies[::-1],
                    orientation='h',
                    text=frequencies[::-1],
                    textposition='auto',
                    marker_color=ChartGenerator.COLOR_MISSING,
                    hovertemplate='<b>%{y}</b><br>' +
                                 'Required in %{x} jobs<br>' +
                                 '<extra></extra>'
                )
            ])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Number of Jobs Requiring This Skill",
                yaxis_title="Skill",
                height=max(400, len(skill_names) * 40),  # Dynamic height
                width=ChartGenerator.DEFAULT_WIDTH,
                showlegend=False,
                template='plotly_white',
                margin=dict(l=150)  # More space for skill names
            )
            
            logger.info(f"Top missing skills chart created with {len(skill_names)} skills")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating top missing skills chart: {e}")
            return ChartGenerator._create_empty_chart("Error creating chart")
    
    @staticmethod
    def create_job_match_distribution(
        job_matches: List[float],
        title: str = "Job Match Distribution"
    ) -> go.Figure:
        """
        Create a histogram showing distribution of job match percentages.
        
        Args:
            job_matches: List of match percentages (0-100)
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        try:
            if not job_matches:
                return ChartGenerator._create_empty_chart("No job matches to display")
            
            # Create histogram
            fig = go.Figure(data=[
                go.Histogram(
                    x=job_matches,
                    nbinsx=20,
                    marker_color=ChartGenerator.COLOR_INFO,
                    hovertemplate='Match Range: %{x}%<br>' +
                                 'Number of Jobs: %{y}<br>' +
                                 '<extra></extra>'
                )
            ])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                xaxis_title="Match Percentage (%)",
                yaxis_title="Number of Jobs",
                height=ChartGenerator.DEFAULT_HEIGHT,
                width=ChartGenerator.DEFAULT_WIDTH,
                showlegend=False,
                template='plotly_white'
            )
            
            logger.info("Job match distribution chart created")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating job match distribution: {e}")
            return ChartGenerator._create_empty_chart("Error creating chart")
    
    @staticmethod
    def create_skill_category_pie_chart(
        categories: Dict[str, int],
        title: str = "Skills by Category"
    ) -> go.Figure:
        """
        Create a pie chart showing skill distribution by category.
        
        Args:
            categories: Dictionary mapping category names to counts
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        try:
            if not categories:
                return ChartGenerator._create_empty_chart("No categories to display")
            
            # Extract data
            labels = list(categories.keys())
            values = list(categories.values())
            
            # Create pie chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,  # Donut chart
                    hovertemplate='<b>%{label}</b><br>' +
                                 '%{value} skills<br>' +
                                 '%{percent}<br>' +
                                 '<extra></extra>'
                )
            ])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': '#2c3e50'}
                },
                height=ChartGenerator.DEFAULT_HEIGHT,
                width=ChartGenerator.DEFAULT_WIDTH,
                template='plotly_white'
            )
            
            logger.info("Skill category pie chart created")
            return fig
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return ChartGenerator._create_empty_chart("Error creating chart")
    
    @staticmethod
    def save_chart_as_html(
        fig: go.Figure,
        output_path: str,
        include_plotlyjs: bool = True
    ) -> bool:
        """
        Save Plotly chart as HTML file.
        
        Args:
            fig: Plotly Figure object
            output_path: Path to save HTML file
            include_plotlyjs: Whether to include Plotly JS library
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fig.write_html(
                output_path,
                include_plotlyjs=include_plotlyjs,
                config={'displayModeBar': True, 'responsive': True}
            )
            logger.info(f"Chart saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return False
    
    @staticmethod
    def save_chart_as_image(
        fig: go.Figure,
        output_path: str,
        format: str = 'png',
        width: int = None,
        height: int = None
    ) -> bool:
        """
        Save Plotly chart as static image (requires kaleido).
        
        Args:
            fig: Plotly Figure object
            output_path: Path to save image file
            format: Image format ('png', 'jpg', 'svg', 'pdf')
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            True if successful, False otherwise
        """
        try:
            fig.write_image(
                output_path,
                format=format,
                width=width or ChartGenerator.DEFAULT_WIDTH,
                height=height or ChartGenerator.DEFAULT_HEIGHT
            )
            logger.info(f"Chart image saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving chart image: {e}")
            logger.warning("Make sure 'kaleido' package is installed")
            return False
    
    @staticmethod
    def _create_empty_chart(message: str) -> go.Figure:
        """
        Create an empty chart with a message.
        
        Args:
            message: Message to display
            
        Returns:
            Empty Plotly Figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color=ChartGenerator.COLOR_SECONDARY)
        )
        fig.update_layout(
            height=ChartGenerator.DEFAULT_HEIGHT,
            width=ChartGenerator.DEFAULT_WIDTH,
            template='plotly_white',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Configure logger
    logger.add("logs/chart_generator.log", rotation="10 MB")
    
    print("=" * 60)
    print("CHART GENERATOR TEST")
    print("=" * 60)
    
    # Test 1: Skill match bar chart
    print("\n1. Creating skill match bar chart...")
    fig1 = ChartGenerator.create_skill_match_bar_chart(
        matching_count=15,
        missing_count=10
    )
    ChartGenerator.save_chart_as_html(fig1, "test_skill_match.html")
    print("✓ Saved to test_skill_match.html")
    
    # Test 2: Top missing skills chart
    print("\n2. Creating top missing skills chart...")
    missing_skills = [
        {'name': 'Docker', 'frequency': 35},
        {'name': 'Kubernetes', 'frequency': 28},
        {'name': 'AWS', 'frequency': 42},
        {'name': 'React', 'frequency': 25},
        {'name': 'TypeScript', 'frequency': 20},
        {'name': 'MongoDB', 'frequency': 18},
        {'name': 'Redis', 'frequency': 15},
        {'name': 'GraphQL', 'frequency': 12}
    ]
    fig2 = ChartGenerator.create_top_missing_skills_chart(missing_skills)
    ChartGenerator.save_chart_as_html(fig2, "test_missing_skills.html")
    print("✓ Saved to test_missing_skills.html")
    
    # Test 3: Job match distribution
    print("\n3. Creating job match distribution...")
    job_matches = [45, 50, 55, 60, 65, 70, 75, 80, 85, 40, 50, 60, 70, 55, 65, 75]
    fig3 = ChartGenerator.create_job_match_distribution(job_matches)
    ChartGenerator.save_chart_as_html(fig3, "test_match_distribution.html")
    print("✓ Saved to test_match_distribution.html")
    
    # Test 4: Category pie chart
    print("\n4. Creating skill category pie chart...")
    categories = {
        'Programming Languages': 8,
        'Frameworks': 5,
        'Databases': 3,
        'Cloud Platforms': 4,
        'Tools': 6
    }
    fig4 = ChartGenerator.create_skill_category_pie_chart(categories)
    ChartGenerator.save_chart_as_html(fig4, "test_categories.html")
    print("✓ Saved to test_categories.html")
    
    print("\n" + "=" * 60)
    print("All charts created successfully!")
    print("Open the HTML files in a browser to view them.")
    print("=" * 60)