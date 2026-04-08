# Authentication

The xchange-mcp server uses **API key authentication** to protect the `/mcp` endpoint. The `/health` endpoint remains public.

## How it works

- The server holds one or more API keys in its `.env` file (`API_KEY_1`, `API_KEY_2`, etc.)
- Clients must include the key in the `x-api-key` header of every request:
  ```
  x-api-key: <api-key>
  ```
- Requests without a valid key receive `401 Unauthorized`


---

## By pass fastapi-key-auth check:

```main.py
app.add_middleware(AuthorizerMiddleware, public_paths=["/health", "/mcp"])   <--- this is literally no auth needed
```

---

## Server setup

### 1. Generate a key

SSH into the server and run:

```bash
KEY=$(openssl rand -hex 32)
echo "API_KEY_1=$KEY" >> ~/xchange-mcp/src/xchange-mcp/.env
echo "Your API key: $KEY"
```

Copy the printed key — you will give it to the user.

### 2. Restart the server

```bash
cd ~/xchange-mcp
./run_me.sh
```

### Adding more keys (optional)

Each user or client can have their own key:

```bash
echo "API_KEY_2=$(openssl rand -hex 32)" >> ~/xchange-mcp/src/xchange-mcp/.env
```

### Viewing existing keys

```bash
grep API_KEY ~/xchange-mcp/src/xchange-mcp/.env
```

---

## Client setup (Claude Code)

Run these commands on the client machine, replacing `<api-key>` with the key from the server:

```bash
claude mcp add --transport http xchange https://xchange-mcp.ezcoin.cc/mcp \
  --header "x-api-key: <api-key>"
```

Verify the connection:

```bash
claude mcp list
# xchange: https://xchange-mcp.ezcoin.cc/mcp (HTTP) - ✓ Connected
```

### Updating an existing entry

If you need to change the key or URL, remove and re-add:

```bash
claude mcp remove xchange
claude mcp add --transport http xchange https://xchange-mcp.ezcoin.cc/mcp \
  --header "x-api-key: <new-api-key>"
```

---

## Disabling authentication (local dev only)

If no `API_KEY_*` variables are set, `fastapi-key-auth` will raise a startup error. For local development without auth, set a local dev key:

```bash
echo "API_KEY_1=localdev" >> src/xchange-mcp/.env
```

And configure Claude Code accordingly:

```bash
claude mcp add --transport http xchange http://localhost:8888/mcp \
  --header "x-api-key: localdev"
```
