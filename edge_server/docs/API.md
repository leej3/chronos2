# HVAC Edge Server API Documentation

## Overview
This document describes the REST API endpoints provided by the HVAC Edge Server for controlling and monitoring an HVAC system running on a Raspberry Pi.

## Base URL
All endpoints are prefixed with `/api`

## Authentication
Currently, the API does not require authentication as it's designed for internal network use only.

## Endpoints

### Get System State
```http
GET /api/state
```
Returns the complete state of the HVAC system including sensor readings and actuator states.

**Response**
```json
{
  "chiller_status": 0,
  "boiler_status": 0,
  "temperature_1": 22.5,
  "temperature_2": 23.5,
  "humidity": 45.0,
  "system_mode": 0,
  "serial_status": "STATUS:RUNNING;TEMP:22.5"
}
```

### Get Current Mode
```http
GET /api/mode
```
Returns the current operating mode of the system.

**Response**
```json
{
  "mode": "COOLING"
}
```

### Set System Mode
```http
POST /api/mode
```

**Request Body**
```json
{
  "mode": "COOLING"
}
```
Valid modes: `"COOLING"`, `"HEATING"`, `"OFF"`

**Response**
```json
{
  "status": "success",
  "mode": "COOLING"
}
```

### Get Temperature Readings
```http
GET /api/temperature
```
Returns current temperature readings from all sensors.

**Response**
```json
{
  "temperature_1": 22.5,
  "temperature_2": 23.5
}
```

### Set Target Temperature
```http
POST /api/temperature
```

**Request Body**
```json
{
  "temperature": 22.5
}
```
Temperature must be between 16.0°C and 30.0°C.

**Response**
```json
{
  "status": "success",
  "temperature": 22.5
}
```

### Get System Logs
```http
GET /api/logs
```
Returns recent system logs.

**Response**
```json
{
  "logs": [
    "2024-12-17 14:24:51.297 | INFO | System initialized",
    "2024-12-17 14:24:57.115 | INFO | Mode changed to COOLING"
  ]
}
```

## Error Responses
All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid mode. Must be one of: ['COOLING', 'HEATING', 'OFF']"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to connect to hardware"
}
```