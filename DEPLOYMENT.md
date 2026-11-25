# Deployment Information

Status: awaiting deployment and endpoint evidence for the Part 6 agent.

## Public URL

_Record the public HTTPS URL after the CP6 tests pass._

## Platform

_Record the platform and service name._

## CP6 endpoint checks

Run in Bash after substituting the actual public URL. Enter the configured API key at the prompt.

```bash
BASE='https://your-service.up.railway.app'
read -rsp 'Agent API key: ' AGENT_API_KEY
printf '\n'
curl -sS -o /dev/null -w 'GET /health → %{http_code}\n' "$BASE/health"
curl -sS -o /dev/null -w 'GET /ready → %{http_code}\n' "$BASE/ready"
curl -sS -o /dev/null -w 'POST /ask without key → %{http_code}\n' \
  -H 'Content-Type: application/json' -d '{"question":"Hello"}' "$BASE/ask"
curl -sS -o /dev/null -w 'POST /ask with key → %{http_code}\n' \
  -H 'Content-Type: application/json' -H "X-API-Key: $AGENT_API_KEY" \
  -d '{"question":"Hello"}' "$BASE/ask"
unset AGENT_API_KEY
```

| Request | Expected HTTP | Observed HTTP |
| --- | ---: | --- |
| `GET /health` | 200 | |
| `GET /ready` | 200 | |
| `POST /ask` without key | 401 | |
| `POST /ask` with key | 200 | |

## Environment variables

Record the names configured in the service dashboard. Keep secret values in the deployment platform.

- [ ] `PORT`
- [ ] `REDIS_URL`
- [ ] `AGENT_API_KEY`
- [ ] `ENVIRONMENT`
- [ ] `LOG_LEVEL`

## Screenshots

- [ ] `screenshots/dashboard.png`
- [ ] `screenshots/running.png`
- [ ] `screenshots/test.png`
