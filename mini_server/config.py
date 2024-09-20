from dataclasses import dataclass
import simple_parsing

@dataclass
class Config:
    rate_limit_requests_per_minute: int = 10
    max_concurrent_requests: int = 5
    rate_limit_error_message: str = "Rate limit exceeded. Please try again later."
    server_host: str = "0.0.0.0"
    server_port: int = 8080
    log_level: str = "INFO"
    stats_window_size: int = 3600  # 1 hour window for statistics
    stats_print_interval: int = 20  # Interval in seconds for printing stats
    verbose: bool = False

config = simple_parsing.parse(Config)