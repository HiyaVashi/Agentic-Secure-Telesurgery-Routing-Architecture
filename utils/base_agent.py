from pathlib import Path
import json
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class BaseAgent:

    def __init__(self, model, prompt_path):

        self.model = model

        prompt_text = Path(prompt_path).read_text(
            encoding="utf-8"
        )

        self.prompt = ChatPromptTemplate.from_template(
            prompt_text
        )

        self.parser = JsonOutputParser()

        # Runtime metrics for the last invocation
        self.metrics = {}

        # Prompt -> LLM ONLY
        self.chain = (
            self.prompt
            | self.model
        )

    def invoke(self, data: dict):

        # Raw LLM response
        
        start_time = time.perf_counter()
        
        response = self.chain.invoke(data)

        end_time = time.perf_counter()

        # Chat models return AIMessage
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)

        # -----------------------------
        # Runtime Metrics
        # -----------------------------

        elapsed_time = end_time - start_time

        # Approximate token counts
        prompt_tokens = len(str(data).split())

        completion_tokens = len(text.split())

        total_tokens = prompt_tokens + completion_tokens

        tokens_per_second = (
            completion_tokens / elapsed_time
            if elapsed_time > 0
            else 0
        )

        self.metrics = {

            "elapsed_time": round(elapsed_time, 4),

            "prompt_tokens": prompt_tokens,

            "completion_tokens": completion_tokens,

            "total_tokens": total_tokens,

            "tokens_per_second": round(tokens_per_second, 2)

        }

        # DEBUG (remove later if desired)
        print("\n" + "=" * 60)
        print("RAW LLM OUTPUT")
        print("=" * 60)
        print(text)
        print("=" * 60 + "\n")

        # Try normal parsing first
        try:
            return self.parser.parse(text)

        except Exception:

            # Recover JSON if extra text exists
            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1:
                raise RuntimeError(
                    "Model did not return a JSON object."
                )

            json_text = text[start:end + 1]

            try:
                return json.loads(json_text)

            except Exception as exc:
                raise RuntimeError(
                    f"Unable to parse model output as JSON.\n\n{text}"
                ) from exc