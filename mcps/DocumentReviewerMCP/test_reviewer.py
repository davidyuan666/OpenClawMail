#!/usr/bin/env python3
"""
Test script for Document Reviewer MCP
"""

import asyncio
import json
from reviewer_server import convert_pdf_to_markdown, convert_docx_to_markdown, generate_latex_review_report


def test_latex_generation():
    """Test LaTeX review report generation"""
    print("Testing LaTeX generation...")

    analysis_points = [
        {
            "category": "Rationality & Logic",
            "content": "The paper presents a well-structured argument with clear logical flow."
        },
        {
            "category": "Issues & Problems",
            "content": "The experimental section lacks sufficient detail about hyperparameters."
        },
        {
            "category": "Questions & Concerns",
            "content": "How does the proposed method compare to recent state-of-the-art approaches?"
        },
        {
            "category": "Code & Reproducibility",
            "content": "No code repository is mentioned. Reproducibility may be challenging."
        },
        {
            "category": "Errors & Typos",
            "content": "Minor typo on page 3: 'teh' should be 'the'."
        }
    ]

    latex_content = generate_latex_review_report(analysis_points, "Sample Research Paper")

    # Save to file
    output_path = "test_output/review_report.tex"
    import os
    os.makedirs("test_output", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✅ LaTeX report generated: {output_path}")
    print(f"Preview:\n{latex_content[:500]}...")


if __name__ == "__main__":
    test_latex_generation()
