from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.concurrency import run_in_threadpool

from .. import auth, model, schemas
from ..disease_info import DISEASE_INFO
from ..config import settings

router = APIRouter(
    tags=["Prediction"]
)

@router.post("/predict", response_model=schemas.PredictionResponse)
async def upload_and_predict(
    file: UploadFile = File(...),
):
    """
    Receives an image, runs prediction, and returns detailed information about the
    detected plant disease if confidence is high, or a generic message otherwise.
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    image_bytes = await file.read()
    prediction_result = await run_in_threadpool(model.predict_image, image_bytes)

    if "error" in prediction_result:
        raise HTTPException(status_code=500, detail=prediction_result["error"])

    label = prediction_result["prediction_label"]
    confidence = prediction_result["confidence"]

    if label == "Background_without_leaves":
        return schemas.PredictionResponse(
            status="no_leaf",
            confidence=f"{confidence:.2%}",
            message="The detected object may not be a leaf."
        )
    
    if confidence < settings.CONFIDENCE_THRESHOLD:
        return schemas.PredictionResponse(
            status="low_confidence",
            confidence=f"{confidence:.2%}",
            message="Could not confidently identify the plant or disease. Please try again with a clearer image of the affected leaf."
        )
    

    info = DISEASE_INFO.get(label)
    if not info:
        raise HTTPException(status_code=500, detail=f"Internal error: No information available for the detected label '{label}'.")
    
    response_data = {
        "status": "success",
        "confidence": f"{confidence:.2%}",
        **info
    }

    return schemas.PredictionResponse(**response_data)

