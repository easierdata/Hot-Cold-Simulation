# default_config.py

default_configurations = {
    "database": {
        "DB_NAME": "railway",
        "DB_USER": "postgres",
        "DB_PASS": "",
        "DB_HOST": "",
        "DB_PORT": "6563",
    },
    "MonteCarlo-Properties": {
        "step_size": 0.1,
        "num_requests": 100,
        "cache_type": "LRUCache",
        "cache_param_increment": 50,
        "prepopulate_cache": True,
        "num_runs": 32,
        "return_type": "requests",
    },
}
