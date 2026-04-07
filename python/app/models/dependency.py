"""Pydantic schemas for dependency identification — graph representation."""

from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    """A single component, service, team, or module in the dependency graph."""

    id: str = Field(..., description="Unique identifier for the node")
    name: str = Field(..., description="Human-readable name")
    type: str = Field(
        ..., description="Kind of component: service, team, module, database, etc."
    )
    description: str = Field(
        default="", description="Brief description of this component"
    )


class DependencyEdge(BaseModel):
    """A directed relationship between two nodes in the dependency graph."""

    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    relationship: str = Field(
        ...,
        description="Nature of the dependency: depends_on, blocks, consumes, produces",
    )
    description: str = Field(
        default="", description="Additional context about this dependency"
    )


class DependencyGraph(BaseModel):
    """Complete dependency graph with nodes and directed edges."""

    nodes: list[DependencyNode] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)


# ── JSON schema sent to the LLM to enforce structured output ──────────

DEPENDENCY_RESPONSE_SCHEMA: dict = {  # type: ignore[type-arg]
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "name", "type"],
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"},
                    "relationship": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["source_id", "target_id", "relationship"],
            },
        },
    },
    "required": ["nodes", "edges"],
}
