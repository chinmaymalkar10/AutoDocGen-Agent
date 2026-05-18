from langgraph.graph import StateGraph, END
from state import DocState
from agents.repo_analyzer import repo_analyzer
from agents.code_reader import code_reader_full, code_reader_chunked
from agents.dependency_analyzer import dependency_analyzer
from agents.doc_generator import doc_generator


def route_by_repo_size(state: DocState) -> str:
    if state.get("is_large_repo", False):
        return "code_reader_chunked"
    return "code_reader_full"


def build_graph():
    graph = StateGraph(DocState)

    graph.add_node("repo_analyzer", repo_analyzer)
    graph.add_node("code_reader_full", code_reader_full)
    graph.add_node("code_reader_chunked", code_reader_chunked)
    graph.add_node("dependency_analyzer", dependency_analyzer)
    graph.add_node("doc_generator", doc_generator)

    graph.set_entry_point("repo_analyzer")

    graph.add_conditional_edges(
        "repo_analyzer",
        route_by_repo_size,
        {
            "code_reader_full": "code_reader_full",
            "code_reader_chunked": "code_reader_chunked",
        },
    )

    graph.add_edge("code_reader_full", "dependency_analyzer")
    graph.add_edge("code_reader_chunked", "dependency_analyzer")
    graph.add_edge("dependency_analyzer", "doc_generator")
    graph.add_edge("doc_generator", END)

    return graph.compile()


app = build_graph()
