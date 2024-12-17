# HVAC Edge Server

Edge server implementation for the HVAC system running on Raspberry Pi.

## Setup Instructions

1. Install uv and python >= 3.11

2. Create and activate virtual environment:
```bash
uv sync
source .venv/bin/activate
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Modify settings as needed

5. Run the server:
```bash
python src/main.py
```

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## API Endpoints

- GET `/api/state` - Get current system state
- POST `/api/mode` - Switch system mode
- POST `/api/settings` - Update system settings

## Hardware Configuration

Hardware pins are configured in `src/core/config.py`. Modify the SENSORS and ACTUATORS lists according to your setup.