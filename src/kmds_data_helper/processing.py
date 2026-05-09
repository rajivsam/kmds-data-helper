import json

class ResultsAggregator:
    def __init__(self):
        self.collection = []

    def add_result(self, persona_name, source_file, result_json):
        """Stores a persona's JSON output for later synthesis."""
        self.collection.append({
            "persona": persona_name,
            "source": source_file,
            "data": result_json
        })

    def get_strategic_context(self):
        """Formats the collection into a summary string for the Tech Lead."""
        summary = "AGGREGATED PROJECT INSIGHTS:\n"
        for item in self.collection:
            summary += f"- [{item['persona']}] from {item['source']}: {json.dumps(item['data'])}\n"
        return summary
