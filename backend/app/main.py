from fastapi import FastAPI

# Step 1: Create our FastAPI application
app = FastAPI(
    title="ReceiptIQ API",
    description="AI-powered receipt extraction and expense tracking",
    version="0.1.0"
)


# Step 2: Create a health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ReceiptIQ"
    }

