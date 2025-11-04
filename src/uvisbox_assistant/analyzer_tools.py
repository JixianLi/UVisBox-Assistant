"""LLM-powered uncertainty analysis and report generation."""

import traceback
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from uvisbox_assistant import config
from uvisbox_assistant.model import create_model_with_tools


def generate_uncertainty_report(
    statistics_summary: dict,
    analysis_type: str = "quick"
) -> Dict:
    """
    Generate natural language uncertainty analysis report.

    Uses LLM to interpret statistical summaries and generate reports in three formats:
    - inline: 1 sentence summary of uncertainty level
    - quick: 3-5 sentence overview
    - detailed: Full report with median, band, and outlier analysis

    Args:
        statistics_summary: Structured dict from statistics_tool
        analysis_type: "inline" | "quick" | "detailed" (default: "quick")

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly confirmation
        - report: Generated text report
        - analysis_type: Echo of requested type
    """
    try:
        # Implementation will be in Phase 3
        # Placeholder for Phase 1
        return {
            "status": "error",
            "message": "Analyzer tool not yet implemented (Phase 3)"
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error generating report: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


# Tool registry
ANALYZER_TOOLS = {
    "generate_uncertainty_report": generate_uncertainty_report,
}


# Tool schemas for LLM binding
ANALYZER_TOOL_SCHEMAS = [
    {
        "name": "generate_uncertainty_report",
        "description": (
            "Generate a natural language uncertainty analysis report from statistical summaries. "
            "Use this after compute_functional_boxplot_statistics to create text-based analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "statistics_summary": {
                    "type": "object",
                    "description": "Structured statistical summary from statistics tool"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Report format",
                    "enum": ["inline", "quick", "detailed"],
                    "default": "quick"
                }
            },
            "required": ["statistics_summary"]
        }
    }
]
