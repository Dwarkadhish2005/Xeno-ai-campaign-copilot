from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import tempfile
import os
import re
from typing import List, Dict, Any
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from ..database import get_async_session
from ..models import Customer, Order
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/upload", tags=["upload"])


PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")


async def _save_upload_to_temp(upload: UploadFile) -> str:
    suffix = os.path.splitext(upload.filename or "")[1] or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    content = await upload.read()
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return tmp.name


def _row_error(row_idx: int, field: str, message: str) -> Dict[str, Any]:
    return {"row": int(row_idx) + 1, "field": field, "message": message}


@router.post("/customers")
async def upload_customers(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    tmp_path = await _save_upload_to_temp(file)
    try:
        df = pd.read_csv(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        return JSONResponse(status_code=400, content={"success": False, "data": None, "message": f"Failed to parse CSV: {e}"})

    errors: List[Dict[str, Any]] = []
    total_rows = len(df)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    id_col = None
    if "customer_id" in df.columns:
        id_col = "customer_id"
    elif "id" in df.columns:
        id_col = "id"

    required = ["name", "email", "signup_date"]
    for col in required:
        if col not in df.columns:
            os.unlink(tmp_path)
            return JSONResponse(status_code=400, content={"success": False, "data": None, "message": f"Missing required column: {col}"})

    # Check duplicate emails within file
    if "email" in df.columns:
        dup_mask = df["email"].duplicated(keep=False)
        for idx in df[dup_mask].index:
            errors.append(_row_error(idx, "email", f"Duplicate email in file: {df.at[idx,'email']}"))

    # Validate phone and signup_date formats
    for idx, row in df.iterrows():
        email = row.get("email")
        phone = row.get("phone") if "phone" in df.columns else None
        signup = row.get("signup_date")

        # signup date parse
        try:
            parsed = pd.to_datetime(signup, errors="coerce")
            if pd.isna(parsed):
                errors.append(_row_error(idx, "signup_date", f"Invalid date: {signup}"))
            else:
                df.at[idx, "_signup_parsed"] = parsed.date()
        except Exception:
            errors.append(_row_error(idx, "signup_date", f"Invalid date: {signup}"))

        # phone validation (allow NaN)
        if phone and not (isinstance(phone, float) and pd.isna(phone)):
            if not PHONE_REGEX.match(str(phone).strip()):
                errors.append(_row_error(idx, "phone", f"Invalid E.164 phone: {phone}"))

    # Check existing emails in DB
    emails = [e for e in df["email"].dropna().astype(str).unique()]
    if emails:
        q = await session.execute(select(Customer.email).where(Customer.email.in_(emails)))
        existing = {r[0] for r in q.fetchall()}
        for idx, row in df.iterrows():
            if str(row.get("email")) in existing:
                errors.append(_row_error(idx, "email", f"Email already exists in DB: {row.get('email')}"))

    # Determine valid rows
    invalid_rows = {e["row"] for e in errors}
    records: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        if (idx + 1) in invalid_rows:
            continue
        rec = {}
        if id_col:
            rec["id"] = int(row[id_col])
        rec["name"] = str(row["name"]).strip()
        rec["email"] = str(row["email"]).strip()
        rec["phone"] = None if ("phone" not in df.columns or (isinstance(row.get("phone"), float) and pd.isna(row.get("phone")))) else str(row.get("phone")).strip()
        rec["city"] = None if ("city" not in df.columns or (isinstance(row.get("city"), float) and pd.isna(row.get("city")))) else str(row.get("city")).strip()
        rec["signup_date"] = row.get("_signup_parsed")
        records.append(rec)

    inserted = 0
    # Batch insert
    try:
        for i in range(0, len(records), 1000):
            batch = records[i : i + 1000]
            if not batch:
                continue
            await session.execute(insert(Customer).values(batch))
        inserted = len(records)
    except IntegrityError as e:
        await session.rollback()
        os.unlink(tmp_path)
        return JSONResponse(status_code=500, content={"success": False, "data": None, "message": f"DB integrity error: {e}"})

    os.unlink(tmp_path)
    result = {
        "total_rows": total_rows,
        "valid_rows": len(records),
        "invalid_rows": len(errors),
        "errors": errors,
        "inserted_count": inserted,
    }
    return {"success": True, "data": result, "message": f"Upload processed: {inserted} inserted, {len(errors)} errors"}


@router.post("/orders")
async def upload_orders(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    tmp_path = await _save_upload_to_temp(file)
    try:
        df = pd.read_csv(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        return JSONResponse(status_code=400, content={"success": False, "data": None, "message": f"Failed to parse CSV: {e}"})

    errors: List[Dict[str, Any]] = []
    total_rows = len(df)

    df.columns = [c.strip() for c in df.columns]

    id_col = None
    if "order_id" in df.columns:
        id_col = "order_id"
    elif "id" in df.columns:
        id_col = "id"

    required = ["customer_id", "amount", "order_date"]
    for col in required:
        if col not in df.columns:
            os.unlink(tmp_path)
            return JSONResponse(status_code=400, content={"success": False, "data": None, "message": f"Missing required column: {col}"})

    # parse order_date and amount
    for idx, row in df.iterrows():
        # order_date parse
        parsed = pd.to_datetime(row.get("order_date"), errors="coerce")
        if pd.isna(parsed):
            errors.append(_row_error(idx, "order_date", f"Invalid order_date: {row.get('order_date')}"))
        else:
            df.at[idx, "_order_date_parsed"] = parsed.to_pydatetime()

        # amount validation
        try:
            amt = float(row.get("amount"))
            if amt <= 0:
                errors.append(_row_error(idx, "amount", "Amount must be > 0"))
        except Exception:
            errors.append(_row_error(idx, "amount", f"Invalid amount: {row.get('amount')}"))

    # Validate customer_id exists in DB
    customer_ids = [int(c) for c in df["customer_id"].dropna().unique()]
    if customer_ids:
        q = await session.execute(select(Customer.id).where(Customer.id.in_(customer_ids)))
        existing = {r[0] for r in q.fetchall()}
        for idx, row in df.iterrows():
            cid = int(row.get("customer_id"))
            if cid not in existing:
                errors.append(_row_error(idx, "customer_id", f"Customer ID {cid} not found in database"))

    invalid_rows = {e["row"] for e in errors}
    records: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        if (idx + 1) in invalid_rows:
            continue
        rec = {}
        if id_col:
            rec["id"] = int(row[id_col])
        rec["customer_id"] = int(row["customer_id"])
        rec["amount"] = float(row["amount"])
        rec["order_date"] = row.get("_order_date_parsed")
        rec["category"] = None if ("category" not in df.columns or (isinstance(row.get("category"), float) and pd.isna(row.get("category")))) else str(row.get("category")).strip()
        records.append(rec)

    inserted = 0
    try:
        for i in range(0, len(records), 1000):
            batch = records[i : i + 1000]
            if not batch:
                continue
            await session.execute(insert(Order).values(batch))
        inserted = len(records)
    except IntegrityError as e:
        await session.rollback()
        os.unlink(tmp_path)
        return JSONResponse(status_code=500, content={"success": False, "data": None, "message": f"DB integrity error: {e}"})

    os.unlink(tmp_path)
    result = {
        "total_rows": total_rows,
        "valid_rows": len(records),
        "invalid_rows": len(errors),
        "errors": errors,
        "inserted_count": inserted,
    }
    return {"success": True, "data": result, "message": f"Upload processed: {inserted} inserted, {len(errors)} errors"}
