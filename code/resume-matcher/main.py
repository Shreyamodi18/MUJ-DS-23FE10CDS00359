import argparse
import json
import sys

from llm_client import LLMClient


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        sys.exit(1)


def print_report(result):
    print("\n" + "=" * 50)
    print("RESUME vs JOB MATCH REPORT")
    print("=" * 50)
    print(f"\nSummary: {result['candidate_summary']}")
    print(f"Match score: {result['match_score']}/100")
    print("\nMatched skills:  " + ", ".join(result["matched_skills"]))
    print("Missing skills:  " + ", ".join(result["missing_skills"]))
    print("\nStrengths:")
    for s in result["strengths"]:
        print(f"  - {s}")
    print("\nSuggestions:")
    for i, s in enumerate(result["suggestions"], 1):
        print(f"  {i}. {s}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Resume-to-Job Matcher (LLM powered)")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument("--job", required=True, help="Path to job description text file")
    parser.add_argument("--output", help="Optional path to save the JSON result")
    args = parser.parse_args()

    resume = read_file(args.resume)
    job = read_file(args.job)

    client = LLMClient()
    print("Analyzing with LLM...")
    result = client.analyze(resume, job)

    print_report(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Saved JSON to {args.output}")


if __name__ == "__main__":
    main()