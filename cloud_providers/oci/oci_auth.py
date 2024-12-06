from datetime import datetime, timedelta
import oci
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import yaml

class CustomerConfig:
    def __init__(self):
        # Load OCI configuration
        self.config = oci.config.from_file()
        self.identity = oci.identity.IdentityClient(self.config)
        
    def create_customer_compartment(self, customer_name):
        """Create a new compartment for the customer"""
        create_compartment_details = oci.identity.models.CreateCompartmentDetails(
            compartment_id=self.config['tenancy'],
            name=f"customer_{customer_name}",
            description=f"Compartment for {customer_name}"
        )
        return self.identity.create_compartment(create_compartment_details)

    def create_customer_group(self, customer_name):
        """Create a new group for the customer"""
        create_group_details = oci.identity.models.CreateGroupDetails(
            compartment_id=self.config['tenancy'],
            name=f"group_{customer_name}",
            description=f"Group for {customer_name}"
        )
        return self.identity.create_group(create_group_details)

    def create_customer_policy(self, compartment_id, group_id, customer_name):
        """Create policies for customer access"""
        policy_statements = [
            f"Allow group group_{customer_name} to manage all-resources in compartment customer_{customer_name}"
        ]
        create_policy_details = oci.identity.models.CreatePolicyDetails(
            compartment_id=compartment_id,
            name=f"policy_{customer_name}",
            description=f"Policy for {customer_name}",
            statements=policy_statements
        )
        return self.identity.create_policy(create_policy_details)

# FastAPI app for customer onboarding
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT tokens
SECRET_KEY = "TODO VAULT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Customer(BaseModel):
    username: str
    email: str
    company_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/onboard", response_model=Token)
async def onboard_customer(customer: Customer):
    try:
        # Initialize OCI configuration
        oci_config = CustomerConfig()
        
        # Create customer resources in OCI
        compartment = oci_config.create_customer_compartment(customer.company_name)
        group = oci_config.create_customer_group(customer.company_name)
        policy = oci_config.create_customer_policy(
            compartment.data.id,
            group.data.id,
            customer.company_name
        )
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": customer.username, "compartment": compartment.data.id}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to onboard customer: {str(e)}"
        )

async def get_current_customer(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.get("/customer/me")
async def read_customer(current_customer: str = Depends(get_current_customer)):
    return {"username": current_customer}
