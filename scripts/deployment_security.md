# Pillar 4: Private Deployment & Secure Access

## 1. Private Access via Cloudflare Tunnels (Zero Trust)
To access your Hynix dashboard from your phone or external devices without exposing it to the public internet:

1. **Install Cloudflared**:
   ```powershell
   brew install cloudflared # or download windows binary
   ```
2. **Authenticate**:
   ```powershell
   cloudflared tunnel login
   ```
3. **Create Tunnel**:
   ```powershell
   cloudflared tunnel create hynix-vault
   ```
4. **Route to Next.js**:
   Configure `config.yml` to point your private domain to `http://localhost:3000`.
5. **Enable Zero Trust**:
   In the Cloudflare Dashboard, add an **Access Policy** (e.g., Email or GitHub login) so only YOU can load the page.

---

## 2. Handoff to Local Hynix (LM Studio)
Once your Hynix 1 Mini GGUF is ready and running in LM Studio:

1. **Start LM Studio Server**:
   - Enable "Local Server" on port 1234.
   - Load your `hynix-1-mini-q4_k_m.gguf`.

2. **Update `.env`**:
   Change the API endpoint in your backend:
   ```env
   # .env update
   OPENROUTER_API_KEY=lm-studio
   TEACHER_MODEL=hynix-1-mini
   OPENROUTER_BASE_URL=http://localhost:1234/v1
   ```

3. **Backend Logic Swap**:
   The backend already uses `TEACHER_MODEL` and `OPENROUTER_API_KEY` from the env. It will now automatically route through LM Studio's OpenAI-compatible API.
