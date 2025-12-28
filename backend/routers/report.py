"""
Report Generation API Router
Endpoints for generating PDF and HTML sustainability reports
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any
from datetime import datetime
import logging
import os
from pathlib import Path
import uuid

from models.schemas import ReportRequestSchema, ReportResponseSchema, LCAInputSchema
from services.pdf_generator import pdf_generator
from services.lca_engine import lca_engine
from services.circularity_engine import circularity_engine
from services.recommendation_engine import recommendation_engine
from core.config import settings
from core.utils import success_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_report(
    request: ReportRequestSchema,
    background_tasks: BackgroundTasks
):
    """
    Generate comprehensive sustainability report
    
    **Parameters:**
    - project_name: Name of the project
    - lca_input: LCA input parameters
    - include_recommendations: Include recommendations section
    - include_comparisons: Include industry comparisons
    - format: Report format (pdf or html)
    
    **Returns:**
    - Report ID and download URL
    """
    try:
        logger.info(f"Generating report for project: {request.project_name}")
        
        # Generate unique report ID
        report_id = f"rep_{uuid.uuid4().hex[:12]}"
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(request.lca_input)
        
        # Prepare report data
        report_data = {
            "report_id": report_id,
            "project_name": request.project_name,
            "generated_at": datetime.utcnow(),
            "lca_input": request.lca_input.dict(),
            "lca_result": lca_result.dict(),
            "recommendations": None,
            "comparisons": None
        }
        
        # Add recommendations if requested
        if request.include_recommendations:
            recommendations = recommendation_engine.generate_recommendations(
                request.lca_input,
                lca_result,
                None
            )
            report_data["recommendations"] = recommendations.dict()
        
        # Add industry comparisons if requested
        if request.include_comparisons:
            # Get benchmark data
            benchmarks = {
                "aluminium": {"primary": 11.5, "secondary": 0.6},
                "copper": {"primary": 3.2, "secondary": 1.2},
                "steel": {"primary": 2.8, "secondary": 0.5}
            }
            
            material = request.lca_input.material.value
            prod_type = request.lca_input.production_type.value
            
            industry_avg = benchmarks.get(material, {}).get(prod_type, 5.0)
            your_performance = lca_result.co2_per_unit
            
            report_data["comparisons"] = {
                "industry_average_co2_per_kg": industry_avg,
                "your_co2_per_kg": your_performance,
                "performance": "Better than average" if your_performance < industry_avg else "Worse than average",
                "difference_percent": round(((your_performance - industry_avg) / industry_avg) * 100, 2)
            }
        
        # Generate report file
        if request.format == "pdf":
            file_path = pdf_generator.generate_pdf_report(report_data)
        else:
            file_path = pdf_generator.generate_html_report(report_data)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create response
        response = ReportResponseSchema(
            report_id=report_id,
            report_url=f"/api/v1/report/download/{report_id}",
            generated_at=datetime.utcnow(),
            file_size=file_size
        )
        
        # Schedule cleanup after 24 hours
        background_tasks.add_task(cleanup_old_reports)
        
        return success_response(
            data=response.dict(),
            message="Report generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating report"
        )


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    Download generated report
    
    **Parameters:**
    - report_id: Unique report identifier
    
    **Returns:**
    - Report file for download
    """
    try:
        logger.info(f"Downloading report: {report_id}")
        
        # Find report file
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        
        # Check for PDF first
        pdf_file = report_dir / f"{report_id}.pdf"
        html_file = report_dir / f"{report_id}.html"
        
        if pdf_file.exists():
            return FileResponse(
                path=str(pdf_file),
                filename=f"sustainability_report_{report_id}.pdf",
                media_type="application/pdf"
            )
        elif html_file.exists():
            return FileResponse(
                path=str(html_file),
                filename=f"sustainability_report_{report_id}.html",
                media_type="text/html"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found or has expired"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading report"
        )


@router.get("/preview/{report_id}", response_model=Dict[str, Any])
async def preview_report(report_id: str):
    """
    Get report preview/metadata
    
    **Parameters:**
    - report_id: Unique report identifier
    
    **Returns:**
    - Report metadata and summary
    """
    try:
        logger.info(f"Previewing report: {report_id}")
        
        # Check if report exists
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        pdf_file = report_dir / f"{report_id}.pdf"
        html_file = report_dir / f"{report_id}.html"
        
        if not (pdf_file.exists() or html_file.exists()):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        
        # Get file info
        file_path = pdf_file if pdf_file.exists() else html_file
        file_size = os.path.getsize(file_path)
        file_format = "pdf" if pdf_file.exists() else "html"
        
        preview = {
            "report_id": report_id,
            "format": file_format,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            "download_url": f"/api/v1/report/download/{report_id}"
        }
        
        return success_response(
            data=preview,
            message="Report preview retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving report preview"
        )


@router.delete("/delete/{report_id}", response_model=Dict[str, Any])
async def delete_report(report_id: str):
    """
    Delete a generated report
    
    **Parameters:**
    - report_id: Unique report identifier
    
    **Returns:**
    - Deletion confirmation
    """
    try:
        logger.info(f"Deleting report: {report_id}")
        
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        pdf_file = report_dir / f"{report_id}.pdf"
        html_file = report_dir / f"{report_id}.html"
        
        deleted = False
        
        if pdf_file.exists():
            os.remove(pdf_file)
            deleted = True
        
        if html_file.exists():
            os.remove(html_file)
            deleted = True
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        
        return success_response(
            data={"report_id": report_id, "deleted": True},
            message="Report deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting report"
        )


@router.get("/list", response_model=Dict[str, Any])
async def list_reports(limit: int = 10):
    """
    List available reports
    
    **Parameters:**
    - limit: Maximum number of reports to return
    
    **Returns:**
    - List of available reports
    """
    try:
        logger.info("Listing available reports")
        
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        
        if not report_dir.exists():
            return success_response(
                data={"reports": [], "count": 0},
                message="No reports found"
            )
        
        # Get all report files
        pdf_files = list(report_dir.glob("rep_*.pdf"))
        html_files = list(report_dir.glob("rep_*.html"))
        
        all_files = pdf_files + html_files
        all_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        
        # Limit results
        all_files = all_files[:limit]
        
        reports = []
        for file_path in all_files:
            report_id = file_path.stem
            file_size = os.path.getsize(file_path)
            
            reports.append({
                "report_id": report_id,
                "format": file_path.suffix[1:],  # Remove dot
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "download_url": f"/api/v1/report/download/{report_id}"
            })
        
        return success_response(
            data={"reports": reports, "count": len(reports)},
            message=f"Found {len(reports)} reports"
        )
        
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing reports"
        )


@router.post("/email", response_model=Dict[str, Any])
async def email_report(
    report_id: str,
    email: str,
    background_tasks: BackgroundTasks
):
    """
    Email a report to specified address
    
    **Parameters:**
    - report_id: Report identifier
    - email: Recipient email address
    
    **Returns:**
    - Email status
    """
    try:
        logger.info(f"Emailing report {report_id} to {email}")
        
        # Validate email
        from core.security import validate_email
        if not validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address"
            )
        
        # Check if report exists
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        pdf_file = report_dir / f"{report_id}.pdf"
        html_file = report_dir / f"{report_id}.html"
        
        if not (pdf_file.exists() or html_file.exists()):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        
        # Schedule email in background
        background_tasks.add_task(send_report_email, report_id, email)
        
        return success_response(
            data={
                "report_id": report_id,
                "email": email,
                "status": "scheduled"
            },
            message="Report email scheduled for delivery"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error emailing report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error scheduling report email"
        )


@router.get("/templates", response_model=Dict[str, Any])
async def get_report_templates():
    """
    Get available report templates
    
    **Returns:**
    - List of report templates
    """
    try:
        templates = {
            "standard": {
                "name": "Standard Sustainability Report",
                "description": "Comprehensive report with LCA results and recommendations",
                "sections": [
                    "Executive Summary",
                    "LCA Results",
                    "Emissions Breakdown",
                    "Recommendations",
                    "Industry Comparison"
                ],
                "default": True
            },
            "executive": {
                "name": "Executive Summary",
                "description": "High-level overview for executives",
                "sections": [
                    "Key Metrics",
                    "Top Recommendations",
                    "Cost-Benefit Analysis"
                ],
                "default": False
            },
            "technical": {
                "name": "Technical Report",
                "description": "Detailed technical analysis",
                "sections": [
                    "Methodology",
                    "Detailed LCA Calculations",
                    "Emissions by Lifecycle Stage",
                    "Data Sources",
                    "Assumptions"
                ],
                "default": False
            },
            "comparison": {
                "name": "Comparison Report",
                "description": "Compare multiple scenarios",
                "sections": [
                    "Scenario Comparison",
                    "What-If Analysis",
                    "Optimization Opportunities"
                ],
                "default": False
            }
        }
        
        return success_response(
            data=templates,
            message="Report templates retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving report templates"
        )


# Background tasks

def cleanup_old_reports():
    """Clean up reports older than 24 hours"""
    try:
        report_dir = Path(settings.REPORT_OUTPUT_PATH)
        
        if not report_dir.exists():
            return
        
        import time
        current_time = time.time()
        max_age = 24 * 60 * 60  # 24 hours in seconds
        
        for file_path in report_dir.glob("rep_*.*"):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > max_age:
                os.remove(file_path)
                logger.info(f"Cleaned up old report: {file_path.name}")
        
    except Exception as e:
        logger.error(f"Error cleaning up old reports: {str(e)}")


def send_report_email(report_id: str, email: str):
    """Send report via email (placeholder for actual implementation)"""
    try:
        # This is a placeholder - actual email sending would use SMTP
        logger.info(f"Sending report {report_id} to {email}")
        
        # In production, implement actual email sending:
        # - Use smtp library or email service (SendGrid, AWS SES, etc.)
        # - Attach report file
        # - Send formatted email
        
        logger.info(f"Report {report_id} sent to {email}")
        
    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")