import json
import pymupdf4llm
import dataprofiler as dp
from ollama import Client
import os


class DataDictionaryEngine:
    def __init__(self, model="qwen2.5-coder:7b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model

        # --- PATH ANCHORING ---
        self.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../"))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.pdf_dir = os.path.join(self.data_dir, "pdfs")
        self.sample_dir = os.path.join(self.data_dir, "samples")

    def ensure_dirs(self):
        """Initializes the directory structure needed for ingestion."""
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.sample_dir, exist_ok=True)
        print(f"[*] Ingestion zones verified at: {self.data_dir}")

    def get_data_ground_truth(self, file_path):
        """Refined ground truth extraction handling DataProfiler output variations."""
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return [{"reference_text": f.read()[:5000]}]

        try:
            data = dp.Data(file_path)
            profile = dp.Profiler(data)
            report = profile.report(report_options={"output_format": "pretty"})

            data_stats = report.get('data_stats', [])
            if isinstance(data_stats, list):
                names = [c.get('column_name') for c in data_stats]
            else:
                names = data_stats.keys()

            return [{"column": name, "type": "detected"} for name in names]
        except Exception as e:
            print(f"[-] Ground truth extraction failed for {file_path}: {e}")
            return []

    def generate_summary(self, pdf_path, user_query="data dictionary summary"):
        """Architect Pass: Generates a human-readable summary with key mapping validation."""
        print(
            f"[*] Generating provisional summary for: {os.path.basename(pdf_path)}")
        md_text = pymupdf4llm.to_markdown(pdf_path)
        context = md_text[:12000]

        prompt = f"""
        Role: Data Architect.
        Task: Create a human-readable summary of the provided data documentation.
        User Query: {user_query}
        Context: {context}

        Return ONLY a JSON object:
        {{
            "title": "Short Descriptive Title",
            "summary_text": "A detailed human-readable paragraph",
            "entities": ["list", "of", "main", "tables", "or", "subjects"]
        }}
        """

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={"num_ctx": 16000}
        )

        raw = json.loads(response['response'])
        # Robustness: Map common LLM key variations
        return {
            "title": raw.get("title", "Untitled Dataset"),
            "summary_text": raw.get("summary_text") or raw.get("description") or "No summary generated.",
            "entities": raw.get("entities") or raw.get("key_entities") or []
        }

    def generate_data_report(self, sample_path):
        """Scientist Pass: Analyzes data quality and technical readiness."""
        print(f"[*] Analyzing quality for: {os.path.basename(sample_path)}")

        data = dp.Data(sample_path)
        profile = dp.Profiler(data)
        report = profile.report(report_options={"output_format": "pretty"})

        stats_summary = {
            "row_count": report.get('global_stats', {}).get('row_count', 0),
            "column_count": report.get('global_stats', {}).get('column_count', 0),
            "missing_cells": report.get('global_stats', {}).get('missing_cells', 0),
            "columns": []
        }

        data_stats = report.get('data_stats', [])
        iterable_stats = data_stats if isinstance(
            data_stats, list) else data_stats.values()

        for col in iterable_stats:
            stats_summary["columns"].append({
                "name": col.get('column_name'),
                "type": col.get('data_type'),
                "null_count": col.get('null_count', 0),
                "unique_count": col.get('statistics', {}).get('unique_count', 0)
            })

        prompt = f"""
        Role: Lead Data Scientist.
        Task: Technical Data Quality Report.
        Input Stats: {json.dumps(stats_summary)}
        Return ONLY JSON:
        {{"quality_score": "...", "technical_observations": "...", "data_quality_warnings": [], "modeling_readiness": "..."}}
        """

        response = self.client.generate(
            model=self.model, prompt=prompt, format="json")
        raw = json.loads(response['response'])

        # Robustness: Ensure modeling_readiness is never empty
        return {
            "quality_score": raw.get("quality_score", "Unknown"),
            "technical_observations": raw.get("technical_observations", "No observations."),
            "data_quality_warnings": raw.get("data_quality_warnings", []),
            "modeling_readiness": raw.get("modeling_readiness", "Readiness not determined.")
        }

    def extract_definitions(self, pdf_path, ground_truth=None):
        """Engineer Pass: Reconciles PDF with Schema. Fixes KeyError: 'field_name' via remapping."""
        print(
            f"[*] Performing deep extraction from: {os.path.basename(pdf_path)}")
        md_text = pymupdf4llm.to_markdown(pdf_path)

        prompt = f"""
        Role: Senior Data Engineer.
        Task: Create a unified Data Dictionary.
        Documentation: {md_text[:12000]}
        Ground Truth: {json.dumps(ground_truth) if ground_truth else "None"}
        
        Return ONLY a valid JSON list of objects: 
        [{{"field_name": "...", "data_type": "...", "description": "..."}}]
        """

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={"num_ctx": 16000}
        )
        try:
            raw_list = json.loads(response['response'])
            validated_list = []

            for item in raw_list:
                # Handle case where item is a dictionary (as expected)
                if isinstance(item, dict):
                    name = item.get("field_name") or item.get(
                        "name") or item.get("column")
                    data_type = item.get("data_type", "string")
                    description = item.get(
                        "description", "No description provided.")
                # Handle case where item is just a string (hallucinated format)
                elif isinstance(item, str):
                    name = item
                    data_type = "string"
                    description = "Field identified in documentation."
                else:
                    continue

                if name:
                    validated_list.append({
                        "field_name": name,
                        "data_type": data_type,
                        "description": description
                    })
            return validated_list
        except (json.JSONDecodeError, TypeError):
            print("[-] LLM returned invalid extraction format.")
            return []
