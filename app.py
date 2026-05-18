import sys
import logging
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

import streamlit as st
from utils.repo_loader import load_repo, is_github_url, cleanup_cloned_repo
from utils.logger import log_error, clear_logs
from graph import app as doc_graph

st.set_page_config(page_title="Doc Generator Agent", page_icon="📄", layout="wide")

st.title("📄 Multi-Agent Documentation Generator")
st.markdown("Generate comprehensive documentation for any GitHub repo or local folder.")

input_type = st.radio("Input type", ["GitHub URL", "Local Folder"], horizontal=True)

if input_type == "GitHub URL":
    repo_input = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
else:
    repo_input = st.text_input("Local Folder Path", placeholder="C:/path/to/your/project")

if st.button("Generate Documentation", type="primary", disabled=not repo_input):
    try:
        clear_logs()
        repo_path, repo_url = load_repo(repo_input)

        initial_state = {
            "repo_path": repo_path,
            "repo_url": repo_url,
            "file_tree": "",
            "languages": [],
            "frameworks": [],
            "existing_docs": {},
            "total_lines": 0,
            "is_large_repo": False,
            "entry_points": [],
            "config_summaries": [],
            "module_summaries": [],
            "dependencies": {},
            "dev_dependencies": {},
            "dependency_summary": "",
            "final_markdown": "",
        }

        with st.spinner("Generating documentation..."):
            final_state = None
            for event in doc_graph.stream(initial_state, stream_mode="updates"):
                final_state = event

        last_node = list(final_state.keys())[0]
        markdown = final_state[last_node].get("final_markdown", "")

        if not markdown:
            st.error("No documentation was generated. Check your LLM configuration.")
        else:
            st.success("Documentation generated successfully!")

            st.download_button(
                label="Download Documentation (MD)",
                data=markdown,
                file_name="documentation.md",
                mime="text/markdown",
            )

            st.divider()
            st.markdown(markdown)

    except FileNotFoundError as e:
        log_error(e, context="file_not_found")
        st.error(f"Path not found: {e}")
    except Exception as e:
        log_error(e, context="pipeline")
        st.error(f"Error: {e}")
        st.exception(e)
    finally:
        if is_github_url(repo_input):
            cleanup_cloned_repo()
