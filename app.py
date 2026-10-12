from fastapi import Body, FastAPI, HTTPException, Request, Response
from typing import Optional

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

deliveries = {}
next_id = 1
valid_statuses = ("created", "in_transit", "delivered")


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    request: Request, exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/deliveries", status_code=201)
def create_delivery(data: dict = Body(...)):
    global next_id

    recipient = data.get("recipient")
    address = data.get("address")

    if not isinstance(recipient, str) or not recipient.strip():
        raise HTTPException(400, "Recipient must be a non-empty string")

    if not isinstance(address, str) or not address.strip():
        raise HTTPException(400, "Address must be a non-empty string")

    delivery = {
        "id": next_id,
        "recipient": recipient,
        "address": address,
        "status": "created",
    }

    deliveries[next_id] = delivery
    next_id += 1

    return delivery


@app.get("/deliveries")
def list_deliveries(status: Optional[str] = None):
    if status is not None and status not in valid_statuses:
        raise HTTPException(400, "Unknown status")

    return [
        delivery
        for delivery in deliveries.values()
        if status is None or delivery["status"] == status
    ]


@app.get("/deliveries/{delivery_id}")
def get_delivery(delivery_id: int):
    if delivery_id not in deliveries:
        raise HTTPException(404, "Delivery not found")

    return deliveries[delivery_id]
@app.patch("/deliveries/{delivery_id}/status")
def update_status(delivery_id: int, data: dict = Body(...)):
    new_status = data.get("status")

    if new_status not in valid_statuses:
        raise HTTPException(400, "Unknown status")

    if delivery_id not in deliveries:
        raise HTTPException(404, "Delivery not found")

    delivery = deliveries[delivery_id]
    current_index = valid_statuses.index(delivery["status"])
    new_index = valid_statuses.index(new_status)

    if new_index != current_index + 1:
        raise HTTPException(409, "Invalid status transition")

    delivery["status"] = new_status
    return delivery


@app.delete("/deliveries/{delivery_id}", status_code=204)
def delete_delivery(delivery_id: int):
    if delivery_id not in deliveries:
        raise HTTPException(404, "Delivery not found")

    if deliveries[delivery_id]["status"] != "created":
        raise HTTPException(409, "Only a created delivery can be deleted")

    del deliveries[delivery_id]
    return Response(status_code=204)