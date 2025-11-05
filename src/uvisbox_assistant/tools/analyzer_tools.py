"""LLM-powered uncertainty analysis and report generation."""

import json
import traceback
from typing import Dict, Optional, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from uvisbox_assistant import config
from uvisbox_assistant.llm.model import create_model_with_tools


# Report generation prompts for different formats

INLINE_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a single concise sentence describing the overall uncertainty level in this ensemble data.

Statistical Summary:
{statistics_json}

Guidelines:
- ONE sentence only
- Mention overall uncertainty level (low/moderate/high)
- No recommendations or prescriptions
- Be precise and quantitative when possible

Example outputs:
- "This ensemble shows low uncertainty with tightly clustered curves and no outliers."
- "The data exhibits moderate uncertainty with 15% band width variation and 3 outliers."
- "High uncertainty is evident with wide percentile bands (40% range) and 12% outlier rate."

Generate your inline summary:"""


QUICK_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a brief 3-5 sentence overview of uncertainty characteristics in this ensemble data.

Statistical Summary:
{statistics_json}

Guidelines:
- 3-5 sentences maximum
- Cover: overall MSD (mean squared difference to median), median behavior, band characteristics
- Include specific numbers from the summary
- No recommendations or prescriptions
- Descriptive only

Structure:
1. Overall MSD assessment (1 sentence)
2. Median curve characteristics (1 sentence)
3. Band/variation characteristics (1-2 sentences)
4. Outliers if present (1 sentence)

Generate your quick summary:"""


DETAILED_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a comprehensive uncertainty analysis report from these statistical summaries.

Statistical Summary:
{statistics_json}

Guidelines:
- Comprehensive but concise
- Three sections: Median Behavior, Band Characteristics, Outlier Analysis
- Include specific numbers and metrics from the summary
- Describe trends, patterns, and uncertainty levels
- NO recommendations or prescriptions (descriptive only)
- Use clear, professional language

Structure your report with these sections:

## Median Behavior
[Describe trend, fluctuation, smoothness, value range]

## Band Characteristics
[Describe band widths, widest regions, overall MSD (mean squared difference to median)]

## Outlier Analysis
[Describe outlier count, similarity to median, clustering]

## Overall Assessment
[Synthesize findings into overall uncertainty characterization]

Generate your detailed report:"""


def _get_prompt_for_analysis_type(analysis_type: str) -> str:
    """
    Get the appropriate prompt template for the analysis type.

    Args:
        analysis_type: "inline" | "quick" | "detailed"

    Returns:
        Prompt template string

    Raises:
        ValueError: If analysis_type is invalid
    """
    prompts = {
        "inline": INLINE_REPORT_PROMPT,
        "quick": QUICK_REPORT_PROMPT,
        "detailed": DETAILED_REPORT_PROMPT
    }

    if analysis_type not in prompts:
        raise ValueError(
            f"Invalid analysis_type: {analysis_type}. "
            f"Must be one of {list(prompts.keys())}"
        )

    return prompts[analysis_type]


def validate_processed_statistics(summary: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate processed statistics structure.

    Args:
        summary: Dictionary to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    # Check top-level keys
    required_top_keys = ["data_shape", "median", "bands", "outliers", "method"]
    for key in required_top_keys:
        if key not in summary:
            return False, f"Missing required top-level key: {key}"

    # Check data_shape structure
    if "n_curves" not in summary["data_shape"] or "n_points" not in summary["data_shape"]:
        return False, "data_shape missing n_curves or n_points"

    # Check median structure
    median_keys = ["trend", "overall_slope", "fluctuation_level", "smoothness_score", "value_range"]
    for key in median_keys:
        if key not in summary["median"]:
            return False, f"median missing required key: {key}"

    # Check bands structure
    if "band_widths" not in summary["bands"]:
        return False, "bands missing band_widths"

    # Check outliers structure
    if "count" not in summary["outliers"]:
        return False, "outliers missing count"

    return True, None


def generate_uncertainty_report(
    processed_statistics: dict
) -> Dict:
    """
    Generate natural language uncertainty analysis reports for all three formats.

    Uses LLM to interpret statistical summaries and generate reports in three formats:
    - inline: 1 sentence summary of uncertainty level
    - quick: 3-5 sentence overview
    - detailed: Full report with median, band, and outlier analysis

    Args:
        processed_statistics: Structured dict from compute_functional_boxplot_statistics

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly confirmation
        - reports: Dictionary with all three report types {"inline": "...", "quick": "...", "detailed": "..."}
    """
    try:
        # Validate input structure
        is_valid, error_msg = validate_processed_statistics(processed_statistics)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid processed_statistics: {error_msg}"
            }

        # Convert statistics summary to JSON string for prompts
        statistics_json = json.dumps(processed_statistics, indent=2)

        # Create Gemini model (no tools needed for text generation)
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.3  # Slight creativity for natural language
        )

        # Generate all three report types
        reports = {}
        word_counts = {}

        for analysis_type in ["inline", "quick", "detailed"]:
            # Get appropriate prompt template
            prompt_template = _get_prompt_for_analysis_type(analysis_type)
            prompt = prompt_template.format(statistics_json=statistics_json)

            # Generate report
            response = model.invoke([HumanMessage(content=prompt)])
            report_text = response.content.strip()

            # Validate output length
            word_count = len(report_text.split())

            if analysis_type == "inline" and word_count > 40:
                return {
                    "status": "error",
                    "message": f"Inline report too long ({word_count} words). Expected ~15-30 words."
                }
            elif analysis_type == "quick" and word_count > 150:
                return {
                    "status": "error",
                    "message": f"Quick report too long ({word_count} words). Expected 50-100 words."
                }

            reports[analysis_type] = report_text
            word_counts[analysis_type] = word_count

        # Format summary message
        summary = f"inline: {word_counts['inline']} words, quick: {word_counts['quick']} words, detailed: {word_counts['detailed']} words"

        return {
            "status": "success",
            "message": f"Generated all uncertainty reports ({summary})",
            "reports": reports
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error generating reports: {str(e)}",
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
            "Generate all three types of natural language uncertainty analysis reports "
            "(inline, quick, detailed) from statistical summaries in a single call. "
            "IMPORTANT: You must call compute_functional_boxplot_statistics FIRST to compute statistics. "
            "This tool will automatically use the statistics from that computation and generate all three report formats. "
            "Do NOT call this tool multiple times - it generates all formats at once. "
            "After this call succeeds, all three reports are available in state for instant retrieval."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
