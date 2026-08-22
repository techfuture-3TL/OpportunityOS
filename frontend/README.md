# OpportunityOS frontend

React 18 + TypeScript + Vite dashboard for the Printway Product Opportunity Hub.

## Run locally

1. Start the FastAPI backend from `C:\hackathon\BE` on port `8000`.
2. In this folder, run:

   ```powershell
   npm install
   npm run dev
   ```

3. Open `http://localhost:5173`.

The API defaults to `http://localhost:8000/api/v1`. To target another backend, create `.env.local` with:

```text
VITE_API_BASE_URL=https://your-api.example/api/v1
```

## Validation

```powershell
npm run lint
npm run build
```

The app follows the full specification flow: onboarding, discovery, a 13-control decision lens, ranked opportunity cards, product brief with DeepSeek, keyword database explorer, and Printway base catalog.
