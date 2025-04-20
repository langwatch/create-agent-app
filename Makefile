EXAMPLE_DIRS = langgraph_functional_api_example langgraph_highlevel_api_example pydantic_ai_example

test:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "No arguments provided, running tests in default directories..."; \
		for dir in $(EXAMPLE_DIRS); do \
			echo "--- Running tests in $$dir ---"; \
			uv run pytest -s $$dir || exit 1; \
		done; \
	else \
		args="$(filter-out $@,$(MAKECMDGOALS))"; \
		uv run pytest -s $$args; \
	fi

install: ensure-uv
	uv sync --all-packages --all-extras

ensure-uv:
	@if ! command -v uv &> /dev/null; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi

%:
	@: