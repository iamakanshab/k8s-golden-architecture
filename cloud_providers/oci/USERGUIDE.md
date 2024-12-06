# OCI Customer Authentication System

A secure authentication and onboarding system for managing customer access to Oracle Cloud Infrastructure (OCI) clusters. This system provides automated customer isolation, resource management, and secure authentication flows.

## Features

- **Automated Customer Onboarding**
  - Creates isolated compartments for each customer
  - Configures customer-specific IAM groups
  - Sets up appropriate access policies
  - Generates secure authentication tokens

- **Secure Authentication**
  - JWT-based authentication
  - OAuth2 password flow implementation
  - Automatic token expiration and refresh
  - Secure password hashing with bcrypt

- **RESTful API Endpoints**
  - Customer onboarding
  - Authentication validation
  - Customer profile management

## Prerequisites

- Python 3.8+
- OCI CLI configured with appropriate credentials
- Access to an OCI tenancy with administrative privileges

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/oci-auth-system.git
cd oci-auth-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install fastapi uvicorn oci python-jose[cryptography] passlib[bcrypt] pydantic python-multipart
```

4. Configure OCI credentials:
- Ensure your OCI config file is properly set up at `~/.oci/config`
- Verify you have the necessary permissions in your OCI tenancy

## Configuration

1. Update the `SECRET_KEY` in the main application file:
```python
SECRET_KEY = "your-secure-secret-key-here"
```

2. (Optional) Adjust token expiration time:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Onboard a new customer:
```bash
curl -X POST "http://localhost:8000/onboard" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "customer1",
           "email": "customer1@example.com",
           "company_name": "Company1"
         }'
```

3. Use the returned access token for subsequent requests:
```bash
curl -X GET "http://localhost:8000/customer/me" \
     -H "Authorization: Bearer <your_access_token>"
```

## API Documentation

### POST /onboard
Onboards a new customer and creates necessary OCI resources.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "company_name": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

### GET /customer/me
Returns information about the authenticated customer.

**Headers:**
- Authorization: Bearer <token>

**Response:**
```json
{
    "username": "string"
}
```

## Security Considerations

- Always use HTTPS in production
- Regularly rotate access tokens
- Monitor and audit access patterns
- Implement rate limiting for API endpoints
- Use strong password policies
- Regular security updates and patches

## Error Handling

The system includes comprehensive error handling for:
- Invalid authentication credentials
- Failed resource creation
- OCI API errors
- Invalid request formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository 
