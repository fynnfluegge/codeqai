import json

from codeqai.constants import DatasetFormat, LlmHost
from codeqai.llm import LLM


class DatesetExtractor:
    def __init__(
        self,
        format: DatasetFormat,
        distillation: bool,
        code_snippets: list[dict],
        config,
    ):
        self.format = format
        self.distillation = distillation
        self.code_snippets = code_snippets
        self.llm = LLM(
            llm_host=LlmHost[config["llm-host"].upper().replace("-", "_")],
            chat_model=config["chat-model"],
            deployment=(
                config["model-deployment"] if "model-deployment" in config else None
            ),
        )

    def export(self):
        if self.format == DatasetFormat.CONVERSATIONAL.value:
            return self.export_conversational()
        elif self.format == DatasetFormat.ALPACA.value:
            return self.export_alpaca()

    def export_conversational(self):
        messages_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.distillation:
                    docstring = self.distill_docstring(code_snippet)
                else:
                    continue
            else:
                docstring = code_snippet.get("description")
            message = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a "
                        + (code_snippet.get("language") or "programming")
                        + " expert. Write an implementation for the following description.",
                    },
                    {"role": "user", "content": docstring},
                    {"role": "assistant", "content": code_snippet.get("code")},
                ]
            }

            messages_list.append(message)
            message = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a "
                        + (code_snippet.get("language") or "programming")
                        + " expert. Explain the following code.",
                    },
                    {"role": "user", "content": code_snippet.get("code")},
                    {
                        "role": "assistant",
                        "content": docstring,
                    },
                ]
            }

            messages_list.append(message)

        with open("conversational_dataset.json", "w") as f:
            for messages in messages_list:
                json.dump(messages, f)
                f.write("\n")

    def export_alpaca(self):
        alpaca_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.distillation:
                    docstring = self.distill_docstring(code_snippet)
                else:
                    continue
            else:
                docstring = code_snippet.get("description")

            alpaca_entry = {
                "instruction": "You are a "
                + (code_snippet.get("language") or "programming")
                + " expert. Write an implementation for the following description.",
                "input": docstring,
                "output": code_snippet.get("code"),
            }
            alpaca_list.append(alpaca_entry)
            alpaca_entry = {
                "instruction": "You are a "
                + (code_snippet.get("language") or "programming")
                + " expert. Explain the following code.",
                "input": code_snippet.get("code"),
                "output": docstring,
            }
            alpaca_list.append(alpaca_entry)

        with open("alpaca_dataset.json", "w") as f:
            json.dump(alpaca_list, f, indent=4)

    def distill_docstring(self, code_snippet):
        prompt = (
            "You are a "
            + (code_snippet.get("language") or "programming")
            + " expert. Write a short and decent description for the following code. Return only the description."
        )
        docstring = self.llm.chat_model.invoke(
            [
                ("system", prompt),
                ("human", code_snippet.get("code") or ""),
            ]
        )
        return docstring.content
