"""
PDF and HTML Report Generation Service with MongoDB Integration
Generates professional sustainability reports and stores metadata in MongoDB
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    PDF and HTML report generator with MongoDB integration
    """
    
    def __init__(self, mongodb_uri: str = None, db_name: str = "sustainability_reports"):
        """
        Initialize PDF generator with MongoDB connection
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Database name
        """
        self.output_dir = Path(settings.REPORT_OUTPUT_PATH)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # MongoDB setup
        self.mongodb_uri = mongodb_uri or settings.database_url
        self.db_name = db_name
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.db_name]
        self.reports_collection = self.db['reports']
        
        # Create indexes
        self._create_indexes()
        
        logger.info("PDF Generator with MongoDB initialized")
    
    def _create_indexes(self):
        """Create MongoDB indexes for efficient queries"""
        try:
            self.reports_collection.create_index("report_id", unique=True)
            self.reports_collection.create_index("project_name")
            self.reports_collection.create_index("generated_at")
            self.reports_collection.create_index([("project_name", 1), ("generated_at", -1)])
            logger.info("MongoDB indexes created")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def generate_pdf_report(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate PDF sustainability report and save metadata to MongoDB
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Dictionary with file paths and MongoDB document ID
        """
        try:
            logger.info(f"Generating PDF report: {report_data['report_id']}")
            
            # Create filename
            filename = f"{report_data['report_id']}.pdf"
            filepath = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            styles = getSampleStyleSheet()
            
            # Add custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e3a8a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title Page
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("Sustainability Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            project_title = ParagraphStyle(
                'ProjectTitle',
                parent=styles['Normal'],
                fontSize=18,
                alignment=TA_CENTER
            )
            story.append(Paragraph(report_data['project_name'], project_title))
            story.append(Spacer(1, 0.5*inch))
            
            # Date
            date_str = report_data['generated_at'].strftime("%B %d, %Y")
            story.append(Paragraph(f"Generated on: {date_str}", styles['Normal']))
            story.append(PageBreak())
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            lca_result = report_data['lca_result']
            summary_data = [
                ['Metric', 'Value', 'Unit'],
                ['Total CO₂ Emissions', f"{lca_result['total_co2_emissions']:,.2f}", 'kg CO₂'],
                ['CO₂ per Unit', f"{lca_result['co2_per_unit']:.4f}", 'kg CO₂/kg'],
                ['Energy Consumption', f"{lca_result['energy_consumption']:,.2f}", 'MJ'],
                ['Water Usage', f"{lca_result['water_usage']:,.2f}", 'liters'],
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # LCA Input Parameters
            story.append(Paragraph("Input Parameters", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            lca_input = report_data['lca_input']
            input_data = [
                ['Parameter', 'Value'],
                ['Material', lca_input['material'].title()],
                ['Production Type', lca_input['production_type'].title()],
                ['Quantity', f"{lca_input['quantity']:,.0f} kg"],
                ['Energy Source', lca_input['energy_source'].replace('_', ' ').title()],
                ['Transport Distance', f"{lca_input['transport_distance']:,.0f} km"],
                ['Transport Mode', lca_input['transport_mode'].title()],
                ['Recycled Content', f"{lca_input['recycled_content']}%"],
                ['EOL Recycling Rate', f"{lca_input['end_of_life_recycling_rate']}%"],
            ]
            
            input_table = Table(input_data, colWidths=[3*inch, 3*inch])
            input_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(input_table)
            story.append(PageBreak())
            
            # Emissions Breakdown
            story.append(Paragraph("Emissions Breakdown by Lifecycle Stage", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            breakdown = lca_result['breakdown']
            total = lca_result['total_co2_emissions']
            
            breakdown_data = [
                ['Lifecycle Stage', 'Emissions (kg CO₂)', 'Percentage'],
                ['Raw Material Extraction', 
                 f"{breakdown['raw_material_extraction']:,.2f}",
                 f"{(breakdown['raw_material_extraction']/total*100):.1f}%"],
                ['Production', 
                 f"{breakdown['production']:,.2f}",
                 f"{(breakdown['production']/total*100):.1f}%"],
                ['Transport', 
                 f"{breakdown['transport']:,.2f}",
                 f"{(breakdown['transport']/total*100):.1f}%"],
                ['End of Life', 
                 f"{breakdown['end_of_life']:,.2f}",
                 f"{(breakdown['end_of_life']/total*100):.1f}%"],
                ['TOTAL', f"{total:,.2f}", '100%']
            ]
            
            breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e7ff')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(breakdown_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Carbon Savings
            if lca_result.get('carbon_savings'):
                story.append(Paragraph("Carbon Savings", heading_style))
                savings_text = (
                    f"By using {lca_input['recycled_content']}% recycled content, "
                    f"you have saved approximately <b>{lca_result['carbon_savings']:,.2f} kg CO₂</b> "
                    f"compared to using 100% virgin materials."
                )
                story.append(Paragraph(savings_text, styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Recommendations
            if report_data.get('recommendations'):
                story.append(PageBreak())
                story.append(Paragraph("Sustainability Recommendations", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                recommendations = report_data['recommendations']['recommendations']
                
                for i, rec in enumerate(recommendations[:5], 1):  # Top 5
                    rec_title = f"{i}. {rec['title']}"
                    story.append(Paragraph(rec_title, styles['Heading3']))
                    story.append(Paragraph(rec['description'], styles['Normal']))
                    story.append(Paragraph(f"<b>Impact:</b> {rec['impact']}", styles['Normal']))
                    story.append(Paragraph(f"<b>Difficulty:</b> {rec['implementation_difficulty']}", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
            
            # Industry Comparison
            if report_data.get('comparisons'):
                story.append(PageBreak())
                story.append(Paragraph("Industry Comparison", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                comp = report_data['comparisons']
                comp_text = (
                    f"Your CO₂ emissions per kg: <b>{comp['your_co2_per_kg']:.2f}</b><br/>"
                    f"Industry average: <b>{comp['industry_average_co2_per_kg']:.2f}</b><br/>"
                    f"Performance: <b>{comp['performance']}</b><br/>"
                    f"Difference: <b>{abs(comp['difference_percent']):.1f}%</b>"
                )
                story.append(Paragraph(comp_text, styles['Normal']))
            
            # Footer
            story.append(PageBreak())
            story.append(Spacer(1, 6*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Generated by CirculoMetrix AI", footer_style))
            story.append(Paragraph("Sustainable Manufacturing Analytics Platform", footer_style))
            
            # Build PDF
            doc.build(story)
            
            # Save metadata to MongoDB
            mongo_doc_id = self._save_report_metadata(
                report_data=report_data,
                pdf_path=str(filepath),
                html_path=None
            )
            
            logger.info(f"PDF report generated: {filepath}")
            return {
                "pdf_path": str(filepath),
                "mongo_id": str(mongo_doc_id),
                "report_id": report_data['report_id']
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate HTML sustainability report and save metadata to MongoDB
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Dictionary with file path and MongoDB document ID
        """
        try:
            logger.info(f"Generating HTML report: {report_data['report_id']}")
            
            filename = f"{report_data['report_id']}.html"
            filepath = self.output_dir / filename
            
            lca_result = report_data['lca_result']
            lca_input = report_data['lca_input']
            breakdown = lca_result['breakdown']
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustainability Report - {report_data['project_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3a8a; text-align: center; border-bottom: 3px solid #1e3a8a; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 30px; }}
        .metric {{ background: #e0e7ff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1e3a8a; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #1e3a8a; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border: 1px solid #ddd; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .recommendation {{ background: #f0f9ff; padding: 15px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sustainability Report</h1>
        <h2 style="text-align: center; color: #666;">{report_data['project_name']}</h2>
        <p style="text-align: center;">Generated on: {report_data['generated_at'].strftime("%B %d, %Y")}</p>
        
        <h2>Executive Summary</h2>
        <div class="metric">
            <div>Total CO₂ Emissions</div>
            <div class="metric-value">{lca_result['total_co2_emissions']:,.2f} kg CO₂</div>
        </div>
        <div class="metric">
            <div>Energy Consumption</div>
            <div class="metric-value">{lca_result['energy_consumption']:,.2f} MJ</div>
        </div>
        <div class="metric">
            <div>Water Usage</div>
            <div class="metric-value">{lca_result['water_usage']:,.2f} liters</div>
        </div>
        
        <h2>Input Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Material</td><td>{lca_input['material'].title()}</td></tr>
            <tr><td>Production Type</td><td>{lca_input['production_type'].title()}</td></tr>
            <tr><td>Quantity</td><td>{lca_input['quantity']:,.0f} kg</td></tr>
            <tr><td>Energy Source</td><td>{lca_input['energy_source'].replace('_', ' ').title()}</td></tr>
            <tr><td>Recycled Content</td><td>{lca_input['recycled_content']}%</td></tr>
        </table>
        
        <h2>Emissions Breakdown</h2>
        <table>
            <tr><th>Lifecycle Stage</th><th>Emissions (kg CO₂)</th><th>Percentage</th></tr>
            <tr><td>Raw Material Extraction</td><td>{breakdown['raw_material_extraction']:,.2f}</td>
                <td>{(breakdown['raw_material_extraction']/lca_result['total_co2_emissions']*100):.1f}%</td></tr>
            <tr><td>Production</td><td>{breakdown['production']:,.2f}</td>
                <td>{(breakdown['production']/lca_result['total_co2_emissions']*100):.1f}%</td></tr>
            <tr><td>Transport</td><td>{breakdown['transport']:,.2f}</td>
                <td>{(breakdown['transport']/lca_result['total_co2_emissions']*100):.1f}%</td></tr>
            <tr><td>End of Life</td><td>{breakdown['end_of_life']:,.2f}</td>
                <td>{(breakdown['end_of_life']/lca_result['total_co2_emissions']*100):.1f}%</td></tr>
        </table>
        
        <div class="footer">
            <p>Generated by CirculoMetrix AI</p>
            <p>Sustainable Manufacturing Analytics Platform</p>
        </div>
    </div>
</body>
</html>
            """
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save metadata to MongoDB
            mongo_doc_id = self._save_report_metadata(
                report_data=report_data,
                pdf_path=None,
                html_path=str(filepath)
            )
            
            logger.info(f"HTML report generated: {filepath}")
            return {
                "html_path": str(filepath),
                "mongo_id": str(mongo_doc_id),
                "report_id": report_data['report_id']
            }
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            raise
    
    def _save_report_metadata(
        self, 
        report_data: Dict[str, Any], 
        pdf_path: Optional[str] = None,
        html_path: Optional[str] = None
    ) -> ObjectId:
        """
        Save report metadata to MongoDB
        
        Args:
            report_data: Report data dictionary
            pdf_path: Path to PDF file (if generated)
            html_path: Path to HTML file (if generated)
            
        Returns:
            MongoDB document ObjectId
        """
        try:
            document = {
                "report_id": report_data['report_id'],
                "project_name": report_data['project_name'],
                "generated_at": report_data['generated_at'],
                "pdf_path": pdf_path,
                "html_path": html_path,
                "lca_summary": {
                    "total_co2_emissions": report_data['lca_result']['total_co2_emissions'],
                    "co2_per_unit": report_data['lca_result']['co2_per_unit'],
                    "energy_consumption": report_data['lca_result']['energy_consumption'],
                    "water_usage": report_data['lca_result']['water_usage']
                },
                "input_parameters": report_data['lca_input'],
                "has_recommendations": bool(report_data.get('recommendations')),
                "has_comparisons": bool(report_data.get('comparisons')),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.reports_collection.insert_one(document)
            logger.info(f"Report metadata saved to MongoDB: {result.inserted_id}")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Error saving report metadata: {str(e)}")
            raise
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve report metadata by report_id
        
        Args:
            report_id: Report ID
            
        Returns:
            Report document or None
        """
        try:
            report = self.reports_collection.find_one({"report_id": report_id})
            if report:
                report['_id'] = str(report['_id'])
            return report
        except Exception as e:
            logger.error(f"Error retrieving report: {str(e)}")
            return None
    
    def get_reports_by_project(self, project_name: str, limit: int = 10) -> list:
        """
        Get all reports for a specific project
        
        Args:
            project_name: Project name
            limit: Maximum number of reports to return
            
        Returns:
            List of report documents
        """
        try:
            reports = list(
                self.reports_collection
                .find({"project_name": project_name})
                .sort("generated_at", -1)
                .limit(limit)
            )
            for report in reports:
                report['_id'] = str(report['_id'])
            return reports
        except Exception as e:
            logger.error(f"Error retrieving reports: {str(e)}")
            return []
    
    def get_recent_reports(self, limit: int = 20) -> list:
        """
        Get most recent reports
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of report documents
        """
        try:
            reports = list(
                self.reports_collection
                .find()
                .sort("generated_at", -1)
                .limit(limit)
            )
            for report in reports:
                report['_id'] = str(report['_id'])
            return reports
        except Exception as e:
            logger.error(f"Error retrieving recent reports: {str(e)}")
            return []
    
    def update_report_metadata(self, report_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update report metadata
        
        Args:
            report_id: Report ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            updates['updated_at'] = datetime.utcnow()
            result = self.reports_collection.update_one(
                {"report_id": report_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating report: {str(e)}")
            return False
    
    def delete_report(self, report_id: str, delete_files: bool = False) -> bool:
        """
        Delete report metadata and optionally files
        
        Args:
            report_id: Report ID
            delete_files: Whether to delete the physical files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get report to find file paths
            report = self.get_report_by_id(report_id)
            if not report:
                return False
            
            # Delete files if requested
            if delete_files:
                if report.get('pdf_path'):
                    Path(report['pdf_path']).unlink(missing_ok=True)
                if report.get('html_path'):
                    Path(report['html_path']).unlink(missing_ok=True)
            
            # Delete from MongoDB
            result = self.reports_collection.delete_one({"report_id": report_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting report: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logger.info("MongoDB connection closed")


# Global PDF generator instance
pdf_generator = PDFGenerator()