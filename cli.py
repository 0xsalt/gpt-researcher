"""
Provides a command line interface for the GPTResearcher class.

Usage:

```shell
python cli.py "<query>" --report_type <report_type> --tone <tone> --query_domains <foo.com,bar.com>
```

"""
import asyncio
import argparse
from argparse import RawTextHelpFormatter
from uuid import uuid4
import os

from dotenv import load_dotenv

from gpt_researcher import GPTResearcher
from gpt_researcher.utils.enum import ReportType, Tone
from backend.report_type import DetailedReport
from backend.utils import write_text_to_md, write_md_to_pdf, write_md_to_word

# =============================================================================
# CLI
# =============================================================================

cli = argparse.ArgumentParser(
    description="Generate a research report.",
    # Enables the use of newlines in the help message
    formatter_class=RawTextHelpFormatter)

# =====================================
# Arg: Query
# =====================================

cli.add_argument(
    # Position 0 argument
    "query",
    type=str,
    help="The query to conduct research on.")

# =====================================
# Arg: Report Type
# =====================================

choices = [report_type.value for report_type in ReportType]

report_type_descriptions = {
    ReportType.ResearchReport.value: "Summary - Short and fast (~2 min)",
    ReportType.DetailedReport.value: "Detailed - In depth and longer (~5 min)",
    ReportType.ResourceReport.value: "",
    ReportType.OutlineReport.value: "",
    ReportType.CustomReport.value: "",
    ReportType.SubtopicReport.value: "",
    ReportType.DeepResearch.value: "Deep Research"
}

cli.add_argument(
    "--report_type",
    type=str,
    help="The type of report to generate. Options:\n" + "\n".join(
        f"  {choice}: {report_type_descriptions[choice]}" for choice in choices
    ),
    # Deserialize ReportType as a List of strings:
    choices=choices,
    required=True)

# =====================================
# Arg: Tone
# =====================================

cli.add_argument(
    "--tone",
    type=str,
    help="The tone of the report (optional).",
    choices=["objective", "formal", "analytical", "persuasive", "informative",
            "explanatory", "descriptive", "critical", "comparative", "speculative",
            "reflective", "narrative", "humorous", "optimistic", "pessimistic"],
    default="objective"
)

# =====================================
# Arg: Encoding
# =====================================

cli.add_argument(
    "--encoding",
    type=str,
    help="The encoding to use for the output file (default: utf-8).",
    default="utf-8"
)

# =====================================
# Arg: Query Domains
# =====================================

cli.add_argument(
    "--query_domains",
    type=str,
    help="A comma-separated list of domains to search for the query.",
    default=""
)

# =====================================
# Arg: Report Name
# =====================================

cli.add_argument(
    "--report-name",
    type=str,
    help="Custom name for the output report files (without extension).\n"
         "Example: --report-name \"my-research\" produces my-research.md, my-research.pdf, etc.",
    default=None
)

# =============================================================================
# Main
# =============================================================================

async def main(args):
    """
    Conduct research on the given query, generate the report, and write
    it as a markdown file to the output directory.
    """
    query_domains = args.query_domains.split(",") if args.query_domains else []

    if args.report_type == 'detailed_report':
        detailed_report = DetailedReport(
            query=args.query,
            query_domains=query_domains,
            report_type="research_report",
            report_source="web_search",
        )

        report = await detailed_report.run()
    else:
        # Convert the simple keyword to the full Tone enum value
        tone_map = {
            "objective": Tone.Objective,
            "formal": Tone.Formal,
            "analytical": Tone.Analytical,
            "persuasive": Tone.Persuasive,
            "informative": Tone.Informative,
            "explanatory": Tone.Explanatory,
            "descriptive": Tone.Descriptive,
            "critical": Tone.Critical,
            "comparative": Tone.Comparative,
            "speculative": Tone.Speculative,
            "reflective": Tone.Reflective,
            "narrative": Tone.Narrative,
            "humorous": Tone.Humorous,
            "optimistic": Tone.Optimistic,
            "pessimistic": Tone.Pessimistic
        }

        researcher = GPTResearcher(
            query=args.query,
            query_domains=query_domains,
            report_type=args.report_type,
            tone=tone_map[args.tone],
            encoding=args.encoding
        )

        await researcher.conduct_research()

        report = await researcher.write_report()

    # Determine report filename
    os.makedirs("outputs", exist_ok=True)
    if args.report_name:
        report_filename = args.report_name
    else:
        report_filename = str(uuid4())

    # Generate all output formats
    md_path = await write_text_to_md(report, report_filename)
    pdf_path = await write_md_to_pdf(report, report_filename)
    docx_path = await write_md_to_word(report, report_filename)

    # Print generated files
    print(f"\nReport generation complete:")
    print(f"  Markdown: outputs/{report_filename}.md")
    if pdf_path:
        print(f"  PDF:      outputs/{report_filename}.pdf")
    if docx_path:
        print(f"  DOCX:     outputs/{report_filename}.docx")

if __name__ == "__main__":
    load_dotenv()
    args = cli.parse_args()
    asyncio.run(main(args))
