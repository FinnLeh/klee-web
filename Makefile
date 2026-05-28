.PHONY: up runner

up: runner
	@trap 'kill 0' INT TERM; \
	(cd backend && uv run uvicorn klee_web.main:app --port 8000 --reload) & \
	(cd frontend && npm run dev) & \
	wait

runner:
	docker build -t klee-web-runner ./runner
