from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from brd_core import (
    verify_brd,
    extract_modules,
    generate_gap_questions,
    generate_module_gap_questions,
    enrich_brd_from_answers,
)
from fsd_core import generate_fsd


app = FastAPI(title="SpecForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectMeta(BaseModel):
    name: str | None = None
    context: str | None = None
    tech_stack: str | None = None


class ApiKeys(BaseModel):
    groq: str | None = None
    groq_model: str | None = None
    openai: str | None = None
    openai_model: str | None = None


class VerifyRequest(BaseModel):
    brd_text: str
    project_meta: ProjectMeta = Field(default_factory=ProjectMeta)
    provider: str = "Auto"
    api_keys: ApiKeys = Field(default_factory=ApiKeys)
    auto_enrich: bool = True
    max_iters: int = 2


class ExtractModulesRequest(BaseModel):
    brd_text: str
    project_meta: ProjectMeta = Field(default_factory=ProjectMeta)
    provider: str = "Auto"
    api_keys: ApiKeys = Field(default_factory=ApiKeys)


class QuestionsRequest(BaseModel):
    brd_text: str
    project_meta: ProjectMeta = Field(default_factory=ProjectMeta)
    provider: str = "Auto"
    api_keys: ApiKeys = Field(default_factory=ApiKeys)
    verification_result: dict = Field(default_factory=dict)


class ModuleQuestionsRequest(QuestionsRequest):
    module: dict = Field(default_factory=dict)


class EnrichFromAnswersRequest(BaseModel):
    brd_text: str
    project_meta: ProjectMeta = Field(default_factory=ProjectMeta)
    provider: str = "Auto"
    api_keys: ApiKeys = Field(default_factory=ApiKeys)
    questions_json: str
    answers_json: str


class GenerateFsdRequest(BaseModel):
    brd_text: str
    project_meta: ProjectMeta = Field(default_factory=ProjectMeta)
    settings: dict = Field(default_factory=dict)
    api_keys: ApiKeys = Field(default_factory=ApiKeys)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/verify")
def api_verify(req: VerifyRequest):
    return verify_brd(
        req.brd_text,
        req.project_meta.model_dump(),
        req.provider,
        req.api_keys.model_dump(),
        auto_enrich=req.auto_enrich,
        max_iters=req.max_iters,
    )


@app.post("/api/modules/extract")
def api_extract_modules(req: ExtractModulesRequest):
    return extract_modules(
        req.brd_text,
        req.project_meta.model_dump(),
        req.provider,
        req.api_keys.model_dump(),
    )


@app.post("/api/questions/global")
def api_questions_global(req: QuestionsRequest):
    return generate_gap_questions(
        req.brd_text,
        req.project_meta.model_dump(),
        req.provider,
        req.api_keys.model_dump(),
        req.verification_result,
    )


@app.post("/api/questions/module")
def api_questions_module(req: ModuleQuestionsRequest):
    return generate_module_gap_questions(
        req.brd_text,
        req.project_meta.model_dump(),
        req.provider,
        req.api_keys.model_dump(),
        req.verification_result,
        req.module,
    )


@app.post("/api/enrich/from-answers")
def api_enrich_from_answers(req: EnrichFromAnswersRequest):
    return enrich_brd_from_answers(
        req.brd_text,
        req.project_meta.model_dump(),
        req.provider,
        req.api_keys.model_dump(),
        req.questions_json,
        req.answers_json,
    )


@app.post("/api/fsd/generate")
def api_generate_fsd(req: GenerateFsdRequest):
    return generate_fsd(
        req.brd_text,
        req.project_meta.model_dump(),
        req.settings,
        req.api_keys.model_dump(),
    )

