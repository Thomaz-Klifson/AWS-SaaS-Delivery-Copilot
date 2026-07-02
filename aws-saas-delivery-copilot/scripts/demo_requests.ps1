$BaseUrl = if ($env:DEMO_BASE_URL) { $env:DEMO_BASE_URL } else { "http://127.0.0.1:8000" }

Write-Host "Using base URL: $BaseUrl"

Write-Host "`n1. Health"
Invoke-RestMethod -Method Get -Uri "$BaseUrl/health" | ConvertTo-Json -Depth 8

Write-Host "`n2. Tenant summary"
Invoke-RestMethod -Method Get -Uri "$BaseUrl/tenants/tenant_acme/summary" | ConvertTo-Json -Depth 8

Write-Host "`n3. RAG ask"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/tenants/tenant_acme/rag/ask" `
  -ContentType "application/json" `
  -Body '{"question":"Is customer data encrypted at rest and in transit?","top_k":3}' |
  ConvertTo-Json -Depth 10

Write-Host "`n4. Agent security questionnaire"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/tenants/tenant_acme/agent/run" `
  -ContentType "application/json" `
  -Body '{"task_type":"security_questionnaire","payload":{}}' |
  ConvertTo-Json -Depth 12

Write-Host "`n5. Agent status report"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/tenants/tenant_acme/agent/run" `
  -ContentType "application/json" `
  -Body '{"task_type":"status_report","payload":{"project_name":"ACME SaaS Delivery Copilot","progress":["RAG ingestion implemented","Agent toolkit implemented"],"blockers":["Bedrock production access pending"],"next_steps":["Add evaluation","Prepare AWS deployment plan"],"risks":["Interview scope creep"]}}' |
  ConvertTo-Json -Depth 10

Write-Host "`n6. MCP initialize"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' |
  ConvertTo-Json -Depth 10

Write-Host "`n7. MCP tools/list"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' |
  ConvertTo-Json -Depth 20

Write-Host "`n8. MCP tools/call knowledge_search"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"knowledge_search","arguments":{"tenant_id":"tenant_acme","question":"Does the platform expose APIs for integrations?","top_k":3}}}' |
  ConvertTo-Json -Depth 12

Write-Host "`n9. LLM test mock"
Invoke-RestMethod -Method Post `
  -Uri "$BaseUrl/llm/test" `
  -ContentType "application/json" `
  -Body '{"prompt":"Say hello in one sentence."}' |
  ConvertTo-Json -Depth 8
