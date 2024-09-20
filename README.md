# mini_server

A minimal FastAPI server with built-in rate limiting and logging capabilities.

## Features

- FastAPI-based server with customizable rate limiting
- Concurrent request handling with configurable limits
- Automatic request statistics logging
- Easy integration with OpenAI-like APIs

## Installation

We currently don't have a release on pypi, so you have to install from github.

```bash
pip install @github.com/tcapelle/mini_server.git
```

## Quickstart

```python
from mini_server import MiniServer
import uvicorn

app = MiniServer(
        rate_limit_requests_per_minute=1, # 1 request per minute per user
        log_level="DEBUG", # debug level logging
        stats_print_interval=5, # print stats every 5 seconds
        )

@app.post("/v1/chat/completions")
async def chat(request: Request):
    # Your chat implementation here
    pass

if __name__ == "__main__":
uvicorn.run(app, host="0.0.0.0", port=8080)
```

To run the example:

1. Start the server:
   ```bash
   python example.py
   ```

2. In a separate terminal, run the client:
   ```bash
   python call_server.py
   ```

You can customize the prompt by passing it as an argument:

```bash
python call_server.py --prompt "Tell me a joke"
```

## Stats

Once the server is running, you can see the stats printed on the console.

```
[13:38:16] INFO     PERIODIC STATS:                                                    stats.py:48
           INFO     Current RPS: 0.00                                                  stats.py:49
           INFO     RPM: 0                                                             stats.py:50
           INFO     Unique users (last hour): 0                                        stats.py:51
           INFO     Unique users (last 24 hours): 0                                    stats.py:52
```


So it's just a subclass of FastAPI with some built-in stuff like rate limiting and logging.

## License

MIT