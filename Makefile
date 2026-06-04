.PHONY: up runner

up: runner
	@trap 'kill 0' EXIT INT TERM; \
	(cd backend && exec uv run uvicorn klee_web.main:app --port 8000 --reload) & \
	(cd frontend && exec npm run dev) & \
	wait

runner:
	docker build -t klee-web-runner ./runner
