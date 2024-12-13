import sys
import logging
import socketio

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

sio = socketio.Server(cors_allowed_origins='*', logger=logger, engineio_logger=logger, async_mode="gevent_uwsgi")


@sio.on("backend")
def handle_message(sid, data):
    # Set CORS headers
    # headers = {
    #     'Access-Control-Allow-Origin': '*',  # Replace '*' with specific domains if needed
    #     'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    #     'Access-Control-Allow-Headers': 'Authorization, Content-Type'
        
    # }
    
    # Emit with headers
    sio.emit(data["event"], data["message"], skip_sid=sid)


app = socketio.Middleware(sio)
