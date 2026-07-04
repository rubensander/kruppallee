"""FastAPI application for exposing departure data."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import mysql.connector
import os
from dotenv import load_dotenv
from typing import List, Optional, Union
from datetime import datetime

load_dotenv()

app = FastAPI(title="Departure API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
}


class Departure(BaseModel):
    """Pydantic model for departure data."""
    datetime: Union[str, datetime]
    line: Union[str, int]
    platform: Union[str, int]
    realdatetime: Optional[Union[str, datetime]] = None
    delay: Optional[int] = None
    realtime: Optional[bool] = None
    direction: Optional[str] = None

    @field_validator("datetime", "realdatetime", mode="before")
    @classmethod
    def convert_datetime(cls, v):
        """Convert datetime objects to ISO format strings."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @field_validator("line", "platform", mode="before")
    @classmethod
    def convert_to_string(cls, v):
        """Convert line and platform to strings."""
        return str(v) if v is not None else v


def get_db_connection():
    """Create a new database connection."""
    return mysql.connector.connect(**DB_CONFIG)


@app.get("/departures", response_model=List[Departure])
async def get_departures(line: Optional[str] = None, limit: int = 100):
    """
    Get departure data from the database.
    
    Query parameters:
    - line: Filter by specific line (optional)
    - limit: Maximum number of results (default: 100)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if line:
            query = "SELECT * FROM departures WHERE line = %s ORDER BY datetime DESC LIMIT %s"
            cursor.execute(query, (line, limit))
        else:
            query = "SELECT * FROM departures ORDER BY datetime DESC LIMIT %s"
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if not results:
            raise HTTPException(status_code=404, detail="No departures found")
        
        return results
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
