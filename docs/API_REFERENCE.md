# API Reference

This document describes the public endpoints exposed by the application.

## Base URL

All endpoints are served from the application's base URL.

---

## GET /health

**Purpose:** Health check endpoint used by load balancers, uptime monitors, and deployment pipelines to verify that the service is running and responsive.

**Request:**

```http
GET /health
```

**Response:**

| Status Code | Description |
|-------------|-------------|
| 200 | Service is healthy |

**Example Response:**

```json
{
  "status": "ok",
  "uptime_seconds": 86400
}
```

---

## POST /api/auth

**Purpose:** Authentication endpoint for user login. Accepts credentials and returns an access token on success.

**Request:**

```http
POST /api/auth
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | yes | User's email address |
| password | string | yes | User's password |

**Responses:**

| Status Code | Description |
|-------------|-------------|
| 200 | Authentication successful; access token returned |
| 400 | Malformed request body |
| 401 | Invalid credentials |
| 429 | Too many authentication attempts |

**Example Request:**

```json
{
  "email": "user@example.com",
  "password": "s3cret"
}
```

**Example Response (200):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## GET /api/locations

**Purpose:** Retrieves a list of available locations. Supports optional filtering and pagination.

**Request:**

```http
GET /api/locations
```

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| region | string | no | Filter locations by region (e.g. `us-east`) |
| page | integer | no | Page number, defaults to 1 |
| per_page | integer | no | Items per page, defaults to 20, max 100 |

**Responses:**

| Status Code | Description |
|-------------|-------------|
| 200 | List of locations returned |
| 400 | Invalid query parameters |
| 401 | Authentication required |
| 404 | No locations found for the given filter |

**Example Request:**

```http
GET /api/locations?region=us-east&page=1&per_page=10
```

**Example Response (200):**

```json
{
  "data": [
    {
      "id": "loc-001",
      "name": "New York",
      "region": "us-east",
      "timezone": "America/New_York"
    },
    {
      "id": "loc-002",
      "name": "Boston",
      "region": "us-east",
      "timezone": "America/New_York"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 42
  }
}
```

---

## Error Format

All error responses use a consistent JSON structure:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "The provided credentials are incorrect."
  }
}
```
