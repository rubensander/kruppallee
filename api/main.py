"""FastAPI application for exposing departure data."""
from fastapi import FastAPI, HTTPException, Query
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
async def get_departures(
    line: Optional[str] = Query(None, description="Filter by specific line number (e.g., '107', '103')"),
    limit: int = Query(100, description="Maximum number of results to return (default: 100)"),
    from_date: Optional[str] = Query(None, description="Filter departures from this date (YYYY-MM-DD format, e.g., '2026-07-01')"),
    to_date: Optional[str] = Query(None, description="Filter departures up to this date (YYYY-MM-DD format, e.g., '2026-07-04')")
):
    """
    Get departure data from the database.
    
    Returns a list of departures with the following optional filters:
    
    - **line**: Filter by specific line (e.g., '107', '103', 'ne8')
    - **limit**: Maximum number of results (default: 100, max: 1000)
    - **from_date**: Start date in YYYY-MM-DD format (inclusive)
    - **to_date**: End date in YYYY-MM-DD format (inclusive)
    
    Examples:
    - `/departures` - Get 100 latest departures
    - `/departures?limit=50` - Get 50 latest departures
    - `/departures?line=107` - Get departures for line 107
    - `/departures?from_date=2026-07-01&to_date=2026-07-04` - Get departures in date range
    - `/departures?line=107&from_date=2026-07-01&to_date=2026-07-04&limit=500` - Combined filters
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build WHERE clause conditions
        conditions = []
        params = []
        
        if line:
            conditions.append("line = %s")
            params.append(line)
        
        if from_date:
            conditions.append("DATE(datetime) >= %s")
            params.append(from_date)
        
        if to_date:
            conditions.append("DATE(datetime) <= %s")
            params.append(to_date)
        
        # Build query
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
        else:
            where_clause = ""
        
        params.append(limit)
        query = f"SELECT * FROM departures{where_clause} ORDER BY datetime DESC LIMIT %s"
        cursor.execute(query, params)
        
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
