from dataclasses import dataclass
import simple_parsing
from openai import OpenAI

local_url = "http://127.0.0.1:8080/v1"

@dataclass
class Args:
    prompt: str = "Tell me a short joke"
    model: str = "gpt-4o-mini"


if __name__ == "__main__":
    args = simple_parsing.parse(Args)

    client = OpenAI(
        base_url=local_url,
        api_key="dummy_key",
    )

    response = client.chat.completions.create(
        model=args.model,
        messages=[
            {"role": "user", "content": args.prompt}
        ]
    )

    print(response)