# Production configuration

PRODUCTION_CONFIG = {
    "debug": False,
    "workers": 4,
    "log_level": "INFO",
    "cors": ["https://yourdomain.com"],
    "max_connections": 100,
}

# Development configuration

DEVELOPMENT_CONFIG = {
    "debug": True,
    "workers": 1,
    "log_level": "DEBUG",
    "cors": ["*"],
    "max_connections": 10,
}

# Testing configuration

TESTING_CONFIG = {
    "debug": True,
    "database_url": "sqlite:///:memory:",
    "redis_url": "redis://localhost:6379/1",
}
