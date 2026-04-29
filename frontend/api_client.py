from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional, Tuple

import requests

try:
    import streamlit as st
except Exception:  # pragma: no cover - keeps helpers importable outside Streamlit
    st = None


DEFAULT_API_BASE_URL = "http://localhost:8000"
EXCEL_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class APIError(RuntimeError):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def get_api_base_url() -> str:
    if st is not None:
        try:
            configured_url = st.secrets.get("SMARTENTRY_API_URL") or st.secrets.get(
                "api_base_url"
            )
        except Exception:
            configured_url = None

        if configured_url:
            return str(configured_url).rstrip("/")

    return os.getenv("SMARTENTRY_API_URL", DEFAULT_API_BASE_URL).rstrip("/")


def normalize_profile(profile: Optional[str]) -> str:
    if not profile:
        return "generic_excel.json"

    return profile if profile.endswith(".json") else f"{profile}.json"


def infer_file_type(uploaded_file: Any) -> str:
    mime_type = getattr(uploaded_file, "type", "") or ""
    filename = getattr(uploaded_file, "name", "") or ""

    if mime_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return "pdf"

    return "image"


class SmartEntryAPI:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 60,
        process_timeout: int = 300,
    ) -> None:
        self.base_url = (base_url or get_api_base_url()).rstrip("/")
        self.timeout = timeout
        self.process_timeout = process_timeout

    def upload_document(self, uploaded_file: Any) -> Dict[str, Any]:
        file_bytes = uploaded_file.getvalue()
        files = {
            "file": (
                uploaded_file.name,
                file_bytes,
                uploaded_file.type or "application/octet-stream",
            )
        }
        response = self._post("/upload", files=files)
        return self._json(response)

    def process_document(
        self,
        file_id: str,
        file_path: str,
        file_type: str,
        profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "file_id": file_id,
            "file_path": file_path,
            "file_type": file_type,
            "profile": normalize_profile(profile),
        }
        response = self._post(
            "/process",
            json=payload,
            timeout=self.process_timeout,
        )
        return self._json(response)

    def save_corrections(
        self,
        file_id: str,
        mapped_rows: list[dict[str, Any]],
    ) -> Dict[str, Any]:
        payload = {
            "file_id": file_id,
            "data": {
                "mapped_data": mapped_rows,
            },
        }

        try:
            response = self._post("/memory/save", json=payload)
            return self._json(response)
        except APIError as exc:
            if exc.status_code == 405:
                try:
                    response = self._post("/memory/save/", json=payload)
                    return self._json(response)
                except APIError as slash_exc:
                    if slash_exc.status_code != 422:
                        raise
            elif exc.status_code != 422:
                raise

        # Compatibility for the current backend route signature:
        # save_document(file_id: str, state: dict)
        response = self._post(
            "/memory/save/",
            params={"file_id": file_id},
            json=payload["data"],
        )
        return self._json(response)

    def export_excel(
        self,
        file_id: str,
        file_path: str,
        file_type: str,
        profile: Optional[str] = None,
    ) -> Tuple[bytes, str]:
        payload = {
            "file_id": file_id,
            "file_path": file_path,
            "file_type": file_type,
            "profile": normalize_profile(profile),
        }
        response = self._post(
            "/process/excel",
            json=payload,
            timeout=self.process_timeout,
        )

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            body = self._json(response)
            if body.get("success") is False:
                raise APIError(
                    "Excel export failed.",
                    status_code=response.status_code,
                    details=body.get("errors") or body,
                )

        return response.content, self._filename_from_response(response)

    def _post(self, path: str, **kwargs: Any) -> requests.Response:
        timeout = kwargs.pop("timeout", self.timeout)

        try:
            response = requests.post(
                self._url(path),
                timeout=timeout,
                allow_redirects=True,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise APIError(
                f"Could not reach SmartEntry API at {self.base_url}.",
                details=str(exc),
            ) from exc

        if response.status_code >= 400:
            raise APIError(
                self._error_message(response),
                status_code=response.status_code,
                details=self._safe_json(response),
            )

        return response

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _json(response: requests.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except ValueError as exc:
            raise APIError("The API returned a non-JSON response.") from exc

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    @classmethod
    def _error_message(cls, response: requests.Response) -> str:
        body = cls._safe_json(response)
        if isinstance(body, dict):
            errors = body.get("errors") or body.get("detail")
            if isinstance(errors, list):
                return "; ".join(str(error) for error in errors)
            if errors:
                return str(errors)

        return f"SmartEntry API returned HTTP {response.status_code}."

    @staticmethod
    def _filename_from_response(response: requests.Response) -> str:
        disposition = response.headers.get("content-disposition", "")
        match = re.search(r'filename="?([^";]+)"?', disposition)
        return match.group(1) if match else "invoice.xlsx"
