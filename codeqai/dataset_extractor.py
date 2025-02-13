import json

from yaspin import yaspin

from codeqai.constants import DatasetFormat, LlmHost
from codeqai.llm import LLM


class DatasetExtractor:
    def __init__(
        self,
        format: DatasetFormat,
        doc_distillation: bool,
        code_distillation: bool,
        code_snippets: list[dict],
        config,
        max_tokens,
    ):
        self.format = format
        self.doc_distillation = doc_distillation
        self.code_distillation = code_distillation
        self.code_snippets = code_snippets
        self.llm = LLM(
            llm_host=LlmHost[config["llm-host"].upper().replace("-", "_")],
            chat_model=config["chat-model"],
            max_tokens=max_tokens,
            deployment=(
                config["model-deployment"] if "model-deployment" in config else None
            ),
        )

    def export(self):
        """
        Exports the dataset based on the specified format.

        This method checks the format of the dataset and calls the appropriate export method.
        It also prints messages indicating the progress and completion of the export process.

        Supported formats:
        - CONVERSATIONAL: Exports to conversational_dataset.json
        - ALPACA: Exports to alpaca_dataset.json
        - INSTRUCTION: Exports to instruction_dataset.json
        """
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
        """
        Exports the code snippets in a conversational format.

        This method processes each code snippet in the dataset and creates conversational messages
        for both implementation and explanation tasks. The messages are then saved to a JSON file.
        """
        messages_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.doc_distillation:
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
        """
        Exports the code snippets in an Alpaca format.

        This method processes each code snippet in the dataset and creates Alpaca entries
        for both implementation and explanation tasks. The entries are then saved to a JSON file.
        """
        alpaca_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.doc_distillation:
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
        """
        Exports the code snippets in an instruction format.

        This method processes each code snippet in the dataset and creates instruction entries
        for both implementation and explanation tasks. The entries are then saved to a JSON file.
        """
        instructions_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.doc_distillation:
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
        """
        Exports the code snippets in a completion format.

        This method processes each code snippet in the dataset and creates completion entries.
        The entries are then saved to a JSON file.
        """
        completions_list = []
        for code_snippet in self.code_snippets:
            if code_snippet.get("description") is None:
                if self.doc_distillation:
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
        """
        Distills a concise description from the given code snippet.

        Args:
            code_snippet (dict): A dictionary containing details about the code snippet, such as method name, programming language, and the actual code.

        Returns:
            str: A concise description of the code snippet.
        """
        spinner = yaspin(
            text=f"Distilling {code_snippet.get('method_name')}...",
            color="green",
        )
        spinner.start()
        prompt = (
            "You are a "
            + (code_snippet.get("language") or "programming")
            + " expert. Write a short and concise description for the following code. Return only the description."
        )
        docstring = self.llm.chat_model.invoke(
            [
                ("system", prompt),
                ("human", code_snippet.get("code") or ""),
            ]
        )
        spinner.stop()
        return docstring.content

    def distill_code(self, code_snippet):
        """
        Distills a given code snippet into smaller chunks and provides explanations for each chunk.

        Args:
            code_snippet (dict): A dictionary containing details about the code snippet, such as method name, programming language, and the actual code.

        Returns:
            dict: A dictionary containing the distilled code chunks and their explanations.
        """
        spinner = yaspin(
            text=f"Distilling {code_snippet.get('method_name')}...",
            color="green",
        )
        spinner.start()
        prompt = (
            "You are a "
            + (code_snippet.get("language") or "programming")
            + " expert. Split the following code into reasonable chunks and explain each chunk. "
            + "Return a JSON object with a list of objects containing the code chunk with key 'code' and the explanation with key 'explanation'."
        )
        code = self.llm.chat_model.invoke(
            [
                ("system", prompt),
                ("human", code_snippet.get("code") or ""),
            ]
        )
        spinner.stop()

        try:
            # Ensure the content is a string before parsing
            if isinstance(code.content, str):
                # Parse the output to a JSON object
                code_json = json.loads(code.content)
            else:
                raise ValueError("Content is not a valid JSON string")
        except (json.JSONDecodeError, ValueError) as e:
            # Handle JSON parsing error
            print(f"Error parsing response JSON: {e}")
            return {}

        return code_json
