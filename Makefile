EXAMPLE_DIRS = dspy_example inspect_ai_example google_adk_example langgraph_functional_api_example langgraph_highlevel_api_example pydantic_ai_example

test:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Running tests in all directories..."; \
		for dir in $(EXAMPLE_DIRS); do \
			echo "-> Running $$dir tests"; \
			cd $$dir; \
			uv run pytest -s || exit 1; \
			cd ..; \
		done; \
	else \
		args="$(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Running $$args tests"; \
		cd $$args; \
		uv run pytest -s || exit 1; \
		cd ..; \
	fi

install: ensure-uv
	uv sync --all-extras
	for dir in $(EXAMPLE_DIRS); do \
		cd $$dir; \
		echo "-> Installing $$dir dependencies"; \
		uv sync --all-extras; \
		cd ..; \
	done

ensure-uv:
	@if ! command -v uv &> /dev/null; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi

%:
	@: