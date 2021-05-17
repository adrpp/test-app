
CLIENT_URL = 'https://exponea-engineering-assignment.appspot.com/api/work'
NUMBER_OF_TASKS = 3
REQUEST_ID_HEADER = 'request-id'
SIZE_POOL_AIOHTTP = 100

LOGGER_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file_handler_info': {
            'level': 'INFO',
            'filename': 'info.log',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'file_handler_debug': {
            'level': 'DEBUG',
            'filename': 'debug.log',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'test.service': {
            'handlers': ['file_handler_debug'],
            'level': 'DEBUG',
        },
        'uvicorn.error': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_handler_debug'],
            'propagate': False
        },
        'uvicorn.access': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_handler_debug'],
            'propagate': False
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': ['console', 'file_handler_info'],
            'propagate': False
        }
    }
}
