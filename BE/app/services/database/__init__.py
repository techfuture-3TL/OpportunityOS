"""Supabase client - chỉ lưu JOB metadata, không lưu data thật."""
from __future__ import annotations

import os
from typing import Optional
from datetime import datetime

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None


def get_supabase_url() -> Optional[str]:
    return os.getenv("SUPABASE_URL")


def get_supabase_key() -> Optional[str]:
    return os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")


class SupabaseClient:
    """Supabase client - job metadata management only."""

    _instance: Optional["SupabaseClient"] = None

    def __init__(self):
        self.client: Optional[Client] = None
        if HAS_SUPABASE:
            url = get_supabase_url()
            key = get_supabase_key()
            if url and key:
                self.client = create_client(url, key)

    @classmethod
    def get_instance(cls) -> "SupabaseClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_connected(self) -> bool:
        return self.client is not None

    # =============================================================================
    # JOB MANAGEMENT - Chỉ lưu metadata của job, không lưu data crawl
    # =============================================================================

    def create_job(
        self,
        job_id: str,
        job_type: str,
        query: str,
        status: str = "pending",
        sources: list = None,
    ) -> Optional[dict]:
        """Tạo job mới - lưu metadata."""
        if not self.client:
            return {"job_id": job_id, "status": "pending"}

        try:
            data = {
                "job_id": job_id,
                "job_type": job_type,
                "query": query,
                "status": status,
                "sources": sources or [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            result = self.client.table("jobs").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[supabase] create_job error: {e}")
            return None

    def update_job_status(
        self,
        job_id: str,
        status: str,
        result: dict = None,
        error: str = None,
    ) -> bool:
        """Cập nhật trạng thái job."""
        if not self.client:
            return True

        try:
            update = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
            if result:
                update["result_summary"] = result
            if error:
                update["error"] = error

            self.client.table("jobs").update(update).eq("job_id", job_id).execute()
            return True
        except Exception as e:
            print(f"[supabase] update_job_status error: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[dict]:
        """Lấy job theo ID."""
        if not self.client:
            return None

        try:
            result = self.client.table("jobs").select("*").eq("job_id", job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[supabase] get_job error: {e}")
            return None

    def list_jobs(
        self,
        job_type: str = None,
        status: str = None,
        limit: int = 20,
    ) -> list:
        """Liệt kê jobs."""
        if not self.client:
            return []

        try:
            query = self.client.table("jobs").select("*").order("created_at", desc=True).limit(limit)
            if job_type:
                query = query.eq("job_type", job_type)
            if status:
                query = query.eq("status", status)
            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"[supabase] list_jobs error: {e}")
            return []

    def delete_job(self, job_id: str) -> bool:
        """Xóa job."""
        if not self.client:
            return True

        try:
            self.client.table("jobs").delete().eq("job_id", job_id).execute()
            return True
        except Exception as e:
            print(f"[supabase] delete_job error: {e}")
            return False


# Singleton instance
supabase = SupabaseClient.get_instance()
