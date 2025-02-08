import json

from yaspin import yaspin

from codeqai.constants import DatasetFormat, LlmHost
from codeqai.llm import LLM


class DatasetExtractor:
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
        print("Exporting dataset...")
        if self.format == DatasetFormat.CONVERSATIONAL.value:
            self.export_conversational()
            print("Dataset exported to conversational_dataset.json")
        elif self.format == DatasetFormat.ALPACA.value:
            self.export_alpaca()
            print("Dataset exported to alpaca_dataset.json")
        elif self.format == DatasetFormat.INSTRUCTION.value:
            self.export_instruction()
            print("Dataset exported to instruction_dataset.json")

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

    def export_instruction(self):
        instructions_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.distillation:
                    result = self.distill_docstring(code_snippet)
                    if type(result) is str:
                        docstring = result
                    else:
                        continue
                else:
                    continue
            else:
                docstring = code_snippet.get("description")

            instruction = {
                "prompt": "You are a "
                + (code_snippet.get("language") or "programming")
                + " expert. Write an implementation for the following description:\n"
                + (docstring or ""),
                "completion": code_snippet.get("code"),
            }
            instructions_list.append(instruction)
            instruction = {
                "prompt": "You are a "
                + (code_snippet.get("language") or "programming")
                + " expert. Explain the following code:\n"
                + (code_snippet.get("code") or ""),
                "completion": docstring,
            }
            instructions_list.append(instruction)

        with open("instruction_dataset.json", "w") as f:
            json.dump(instructions_list, f, indent=4)

    def export_completion(self):
        completions_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.distillation:
                    docstring = self.distill_docstring(code_snippet)
                else:
                    continue
            else:
                docstring = code_snippet.get("description")

            completion = {
                "input": docstring,
                "output": code_snippet.get("code"),
            }
            completions_list.append(completion)

        with open("completion_dataset.json", "w") as f:
            json.dump(completions_list, f, indent=4)

    def distill_docstring(self, code_snippet):
        spinner = yaspin(
            text=f"Distilling {code_snippet.get('method_name')}...",
            color="green",
        )
        spinner.start()
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
        spinner.stop()
        return docstring.content
