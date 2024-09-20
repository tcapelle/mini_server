import os
from mini_server import MiniServer
import uvicorn
import openai
from fastapi import Request

# Set up OpenAI API key
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


if __name__ == "__main__":
    app = MiniServer(
        rate_limit_requests_per_minute=1, # 1 request per minute per user
        log_level="DEBUG", # debug level logging
        stats_print_interval=5, # print stats every 5 seconds
    )

    # Add a custom route for chat
    @app.post("/v1/chat/completions")
    async def chat(request: Request):
        data = await request.json()
        print(f"Received data: {data}") # in case you want to see the data
        response = await client.chat.completions.create(**data)
        return response


    uvicorn.run(app, host="0.0.0.0", port=8080)