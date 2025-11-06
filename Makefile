check:
	. .env.local 2>/dev/null || true; \
	pip check; \
	python -c "import numpy,pandas,sklearn,torch,transformers; print('OK:', numpy.__version__, pandas.__version__)" && \
	python -c "from web3 import Web3; from eth_account import Account; print('Web3/eth-account OK')"

clean-caches:
	rm -rf .cache/hf .cache/torch "$$HOME/.cache/huggingface" "$$HOME/.cache/torch" || true
run:
	source .venv/bin/activate && python test_pipeline.py
