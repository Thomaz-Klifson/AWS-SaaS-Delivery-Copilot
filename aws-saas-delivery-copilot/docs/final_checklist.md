# Final Checklist

- [ ] `python -m pytest` passing
- [ ] API starts with `python -m uvicorn app.main:app --reload`
- [ ] `GET /health` works
- [ ] `POST /tenants/tenant_acme/rag/ask` works
- [ ] `POST /tenants/tenant_acme/agent/run` works
- [ ] `POST /mcp/rpc` with `initialize` works
- [ ] `POST /mcp/rpc` with `tools/list` works
- [ ] `POST /mcp/rpc` with `tools/call` works
- [ ] README updated
- [ ] `.env` not committed
- [ ] S3 bucket prepared for production migration
- [ ] Bedrock provider implemented but optional
- [ ] Mock mode remains default for local runs and tests
- [ ] Demo script reviewed before interview
