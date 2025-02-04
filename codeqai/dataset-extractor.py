import json

from codeqai.constants import DatasetFormat


class DatesetExtractor:
    def __init__(
        self, format: DatasetFormat, distillation: bool, code_snippets: list[dict]
    ):
        self.format = format
        self.distillation = distillation
        self.code_snippets = code_snippets

    def export(self):
        if self.format == DatasetFormat.CONVERSATIONAL:
            return self.export_conversational()
        elif self.format == DatasetFormat.ALPACA:
            return self.export_alpaca()

    def export_conversational(self):
        messages_list = []
        for code_snippet in self.code_snippets:
            messages = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a "
                        + (code_snippet.get("language") or "programming")
                        + " expert.",
                    },
                    {"role": "user", "content": code_snippet.get("description")},
                    {"role": "assistant", "content": code_snippet.get("code")},
                ]
            }
            messages_list.append(messages)

        with open("conversational_dataset.json", "w") as f:
            for messages in messages_list:
                json.dump(messages, f)
                f.write("\n")

    def export_alpaca(self):
        alpaca_list = []
        for code_snippet in self.code_snippets:
            alpaca_entry = {
                "instruction": code_snippet.get("description"),
                "input": "",
                "output": code_snippet.get("code"),
            }
            alpaca_list.append(alpaca_entry)

        with open("alpaca_dataset.json", "w") as f:
            json.dump(alpaca_list, f, indent=4)
