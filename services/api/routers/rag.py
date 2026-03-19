"""
Knowledge Base Router - Multi-collection RAG API endpoints

Provides comprehensive knowledge management:
- Multiple knowledge bases (collections)
- Multiple file format support (TXT, PDF, DOCX, MD, HTML)
- Web search integration (Aliyun IQS)
- Webpage indexing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4
import io

from knowledge import get_kb_manager, FileParser
from knowledge.web_search import get_web_search

router = APIRouter()


# ==================== Request/Response Models ====================

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""


class KnowledgeBaseUpdate(BaseModel):
    name: str = None
    description: str = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    chunk_count: int


class DocumentIndexRequest(BaseModel):
    content: str
    title: str = ""
    source: str = "manual"
    url: str = ""


class WebIndexRequest(BaseModel):
    url: str
    kb_id: str = "default"


class WebSearchRequest(BaseModel):
    query: str
    kb_id: str = "default"
    engine_type: str = "Generic"
    time_range: str = "NoLimit"
    auto_index: bool = True
    limit: int = 10


class SearchRequest(BaseModel):
    query: str
    kb_id: str = "default"
    limit: int = 5


# ==================== Knowledge Base Management ====================

@router.post("/knowledge-bases", response_model=dict)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    kb_manager = get_kb_manager()
    kb = await kb_manager.create_knowledge_base(
        name=request.name,
        description=request.description
    )
    return {
        "success": True,
        "knowledge_base": {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "created_at": kb.created_at.isoformat(),
        }
    }


@router.get("/knowledge-bases")
async def list_knowledge_bases():
    """List all knowledge bases"""
    kb_manager = get_kb_manager()
    kbs = await kb_manager.list_knowledge_bases()

    # Get stats for each KB
    result = []
    for kb in kbs:
        stats = await kb_manager.get_stats(kb.id)
        result.append({
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "document_count": stats["total_documents"],
            "chunk_count": stats["total_chunks"],
            "status": stats["status"],
        })

    return {"knowledge_bases": result}


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """Delete a knowledge base and all its data"""
    kb_manager = get_kb_manager()
    success = await kb_manager.delete_knowledge_base(kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"success": True, "message": f"Knowledge base {kb_id} deleted"}


@router.put("/knowledge-bases/{kb_id}")
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdate):
    """Update knowledge base name and/or description"""
    kb_manager = get_kb_manager()
    kb = await kb_manager.update_knowledge_base(
        kb_id,
        name=request.name,
        description=request.description
    )
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {
        "success": True,
        "knowledge_base": {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "updated_at": kb.updated_at.isoformat(),
        }
    }


@router.get("/knowledge-bases/{kb_id}/stats")
async def get_knowledge_base_stats(kb_id: str):
    """Get knowledge base statistics"""
    kb_manager = get_kb_manager()
    stats = await kb_manager.get_stats(kb_id)
    return stats


# ==================== Document Management ====================

@router.get("/knowledge-bases/{kb_id}/documents")
async def list_documents(kb_id: str):
    """List all documents in a knowledge base"""
    kb_manager = get_kb_manager()
    documents = await kb_manager.list_documents(kb_id)
    return {"documents": documents, "total": len(documents)}


@router.post("/knowledge-bases/{kb_id}/documents/text")
async def index_text_document(
    kb_id: str,
    request: DocumentIndexRequest
):
    """Index a text document into a knowledge base"""
    from knowledge import Document

    kb_manager = get_kb_manager()
    doc = Document(
        id=str(uuid4()),
        content=request.content,
        title=request.title,
        source=request.source,
        url=request.url,
        source_type="manual",
        kb_id=kb_id,
    )

    chunk_ids = await kb_manager.add_document(doc, kb_id)

    return {
        "success": True,
        "doc_id": doc.id,
        "title": doc.title,
        "chunks": len(chunk_ids),
    }


@router.post("/knowledge-bases/{kb_id}/documents/file")
async def upload_file(
    kb_id: str,
    file: UploadFile = File(...),
    source: str = Form(""),
):
    """Upload and index a file (supports TXT, PDF, DOCX, MD, HTML)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file type support
    if not FileParser.is_supported(file.filename):
        supported = ", ".join(FileParser.SUPPORTED_EXTENSIONS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {supported}"
        )

    # Read file content
    raw = await file.read()

    if not raw:
        raise HTTPException(status_code=400, detail="File is empty")

    # Add to knowledge base
    kb_manager = get_kb_manager()
    result = await kb_manager.add_file(
        file_content=raw,
        filename=file.filename,
        kb_id=kb_id,
        source=source or file.filename,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/knowledge-bases/{kb_id}/documents/web")
async def index_webpage(kb_id: str, request: WebIndexRequest):
    """Fetch and index a webpage"""
    kb_manager = get_kb_manager()
    result = await kb_manager.add_webpage(request.url, kb_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.delete("/knowledge-bases/{kb_id}/documents/{doc_id}")
async def delete_document(kb_id: str, doc_id: str):
    """Delete a document from a knowledge base"""
    kb_manager = get_kb_manager()
    success = await kb_manager.delete_document(kb_id, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "doc_id": doc_id}


# ==================== Search ====================

@router.post("/knowledge-bases/{kb_id}/search")
async def search_knowledge_base(
    kb_id: str,
    request: SearchRequest
):
    """Search within a knowledge base"""
    kb_manager = get_kb_manager()
    results = await kb_manager.search(
        query=request.query,
        kb_id=kb_id,
        limit=request.limit
    )

    return {
        "query": request.query,
        "total": len(results),
        "results": [
            {
                "content": r.document.content,
                "title": r.document.title,
                "source": r.document.source,
                "url": r.document.url,
                "score": r.score,
                "chunk_index": r.chunk_index,
            }
            for r in results
        ]
    }


@router.get("/knowledge-bases/{kb_id}/search")
async def search_knowledge_base_get(
    kb_id: str,
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum results")
):
    """Search within a knowledge base (GET method)"""
    kb_manager = get_kb_manager()
    results = await kb_manager.search(
        query=query,
        kb_id=kb_id,
        limit=limit
    )

    return {
        "query": query,
        "total": len(results),
        "results": [
            {
                "content": r.document.content,
                "title": r.document.title,
                "source": r.document.source,
                "url": r.document.url,
                "score": r.score,
            }
            for r in results
        ]
    }


# ==================== Web Search Integration ====================

@router.post("/web-search")
async def web_search(request: WebSearchRequest):
    """
    Perform web search using Aliyun IQS

    Optionally auto-index results to knowledge base
    """
    searcher = get_web_search()

    result = await searcher.search_and_index(
        query=request.query,
        kb_id=request.kb_id,
        engine_type=request.engine_type,
        time_range=request.time_range,
        auto_index=request.auto_index
    )

    return result


@router.get("/web-search")
async def web_search_get(
    query: str = Query(..., description="Search query"),
    engine_type: str = Query("Generic", description="Engine type"),
    time_range: str = Query("NoLimit", description="Time range"),
    limit: int = Query(10, description="Maximum results")
):
    """Quick web search (GET method)"""
    searcher = get_web_search()

    result = searcher.search(
        query=query,
        engine_type=engine_type,
        time_range=time_range,
        limit=limit
    )

    return result


# ==================== Legacy Compatibility ====================

# Keep old endpoints for backward compatibility

@router.get("/documents")
async def legacy_list_documents():
    """Legacy: List documents in default knowledge base"""
    kb_manager = get_kb_manager()
    documents = await kb_manager.list_documents("default")
    return {"documents": documents, "total": len(documents)}


@router.get("/sources")
async def legacy_list_sources():
    """Legacy: List sources in default knowledge base"""
    kb_manager = get_kb_manager()
    docs = await kb_manager.list_documents("default")

    # Group by source
    source_map = {}
    for doc in docs:
        source = doc.get("source", "unknown")
        if source not in source_map:
            source_map[source] = 0
        source_map[source] += 1

    return {
        "sources": [
            {"name": name, "count": count}
            for name, count in sorted(source_map.items())
        ]
    }


@router.post("/index")
async def legacy_index_document(request: DocumentIndexRequest):
    """Legacy: Index to default knowledge base"""
    from knowledge import Document

    kb_manager = get_kb_manager()
    doc = Document(
        id=str(uuid4()),
        content=request.content,
        title=request.title,
        source=request.source,
        url=request.url,
        source_type="manual",
        kb_id="default",
    )

    chunk_ids = await kb_manager.add_document(doc, "default")

    return {
        "status": "indexed",
        "doc_id": doc.id,
        "chunks": len(chunk_ids),
        "title": doc.title,
    }


@router.post("/upload")
async def legacy_upload_file(file: UploadFile = File(...)):
    """Legacy: Upload to default knowledge base"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    raw = await file.read()

    kb_manager = get_kb_manager()
    result = await kb_manager.add_file(
        file_content=raw,
        filename=file.filename,
        kb_id="default",
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "status": "indexed",
        **result
    }


@router.delete("/documents/{doc_id}")
async def legacy_delete_document(doc_id: str):
    """Legacy: Delete from default knowledge base"""
    kb_manager = get_kb_manager()
    success = await kb_manager.delete_document("default", doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "doc_id": doc_id}


@router.get("/stats")
async def legacy_get_stats():
    """Legacy: Get default knowledge base stats"""
    kb_manager = get_kb_manager()
    return await kb_manager.get_stats("default")
