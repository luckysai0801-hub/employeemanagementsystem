# VIVA Questions — Employee Management System

This document contains likely viva / interview questions an investigator might ask about this project, ordered from Beginner → Intermediate → Advanced, with concise answers.

---

## Beginner (Setup, basics)

Q1: What does this project do?

A1: It's an Employee Management System that provides CRUD operations for employees, authentication for users, dashboard statistics (total/active employees, average salary, department distribution), export features (CSV/Excel/PDF), and file uploads for employee photos.

Q2: How do you run the project locally?

A2: There are separate `frontend` and `backend` folders. The backend is a FastAPI app in `backend/server.py` and uses MongoDB (connection via `MONGO_URL` in `.env`). Install backend dependencies from `backend/requirements.txt` and run with `uvicorn server:app --reload` or using provided `run.bat` / start scripts. The frontend is a React app in `frontend/`—install node modules with `npm install` and run `npm start` (or `start_frontend.bat`). There are helper batch scripts at the repo root for convenience.

Q3: Where is the main backend entry point?

A3: `backend/server.py` is the main FastAPI app and defines routes, models and startup/shutdown events.

Q4: Where is the main frontend entry point?

A4: `frontend/src/index.js` and `frontend/src/App.js` are the React entry files. Pages are under `frontend/src/pages/`.

Q5: What database does the project use?

A5: MongoDB via `motor.motor_asyncio.AsyncIOMotorClient`. Connection parameters are read from environment variables (e.g., `MONGO_URL`, `DB_NAME`).


---

## Intermediate (APIs, code structure, features)

Q6: Describe the main API endpoints for employees.

A6: Key endpoints under `/api`:
- `POST /api/employees/add` — create an employee
- `GET /api/employees/list` — list with pagination, filters and sorting
- `GET /api/employees/count` — get result count for current filters
- `GET /api/employees/{id}` — fetch single employee
- `PUT /api/employees/{id}` — update employee
- `DELETE /api/employees/{id}` — soft-delete (sets status inactive)
- `POST /api/employees/{id}/restore` — restore soft-deleted employees

Q7: How is authentication implemented?

A7: FastAPI `HTTPBearer` is used along with JWT tokens. `create_token` signs tokens using `JWT_SECRET` and tokens are verified in `get_current_user` dependency. Frontend stores token in `localStorage` and sends `Authorization: Bearer <token>`.

Q8: How are file uploads handled?

A8: There's an upload route `POST /api/upload` that accepts `UploadFile` and saves the file to a backend `uploads/` directory. The frontend uploads the selected file and receives back `filename` and `url`, which it stores in the employee's `photo` field.

Q9: How does the dashboard compute average salary and salary by department?

A9: Backend uses MongoDB aggregation pipelines:
- Average salary overall: `$group` aggregation with `$avg: "$salary"`.
- Average salary per department: group by `department` and compute `$avg` per group, returned to frontend, rounded to 2 decimals.

Q10: Where are frontend pages and styles located?

A10: Pages are in `frontend/src/pages/` (e.g., `DashboardPage.js`, `EmployeeListPage.js`, `LoginPage.js`) and styles in `frontend/src/styles/`.

Q11: How does export (CSV/Excel/PDF) work?

A11: The frontend offers export buttons that either build CSV in-browser (for page exports) or call backend export routes (`/api/export/csv`, `/api/export/excel`, `/api/export/pdf`) that stream files generated using Python libraries (`csv`, `xlsxwriter`, `reportlab`).


---

## Advanced (Design, security, scaling, testing)

Q12: How are database IDs and employee codes generated and enforced?

A12: Employee and user models use UUIDs (`uuid.uuid4()`) for `id`. Employee `emp_code` is generated in `generate_emp_code()` by counting documents and formatting `EMP{count+1}` zero-padded. This approach is simple but has concurrency caveats (race conditions) if many inserts happen at once.

Q13: What are the concurrency or race-condition risks with `generate_emp_code()` and how would you fix them?

A13: Using `count_documents` and then inserting can lead to duplicate `emp_code` in concurrent inserts. Fixes:
- Use a separate sequence counter collection and `find_one_and_update` with atomic `$inc`.
- Use a transaction (MongoDB replica set) to safely allocate codes.

Q14: How is sensitive data handled and stored (passwords, tokens)?

A14: Passwords are hashed using `bcrypt`. Tokens are JWTs signed with `JWT_SECRET`. Ensure `JWT_SECRET` is kept out of source control (via `.env`) and use HTTPS in production. The backend avoids returning password hashes in responses.

Q15: How are audit logs implemented?

A15: The backend has `create_audit_log` helper that creates `AuditLog` entries in `db.audit_logs` for actions like add/update/delete/restore. Logs store `action`, `employee_id`, `employee_name`, `user`, and `timestamp`.

Q16: What security hardening would you add before production?

A16: Key items:
- Enforce HTTPS + HSTS, use secure cookies for sessions if used.
- Rate limit auth endpoints and sensitive actions.
- Validate and sanitize file uploads (type/size) and use randomized filenames; serve uploads from a CDN or secure storage.
- Use environment specific secrets management (Azure Key Vault / AWS KMS / HashiCorp Vault).
- Add role-based access control and enforce least privilege server-side.
- Ensure CORS is locked down to production origins.
- Input validation for all user-supplied fields, including size/length checks.

Q17: How would you scale this application?

A17: For scaling:
- Backend: run multiple FastAPI workers behind a load balancer (Uvicorn/Gunicorn), put stateless app instances behind API gateway.
- Database: use MongoDB replica set with sharding for large datasets.
- Static assets: serve frontend build from CDN or S3.
- File uploads: store in cloud object storage (S3/GCP/GCS) instead of local disk, serve via CDN.
- Add caching (Redis) for expensive aggregations or frequent reads.

Q18: How is search implemented? Can it be improved?

A18: Current search uses MongoDB regex queries with `$options: "i"` on name/email/emp_code. For larger datasets, use text indexes or an external search engine (Elasticsearch/Opensearch) for performance and richer queries.

Q19: How are errors and logging handled?

A19: The backend uses Python `logging` and wraps validations in HTTPExceptions. There is top-level middleware logging requests and responses. In production, logs should be aggregated (ELK/Datadog) and structured JSON logs should be used.

Q20: How would you add automated tests?

A20: Add unit tests for helper functions and API endpoints. Use `pytest` with `httpx.AsyncClient` to test FastAPI routes. For frontend, use Jest + React Testing Library for components, and Cypress for end-to-end flows (login, add/edit employee, upload).

Q21: How would you secure file uploads against malicious files?

A21: Validate MIME type and file extension, check file signatures (magic bytes), limit file size, run virus scanning (ClamAV / third-party), save files with randomized names and store outside the webroot or on cloud storage with proper access controls. Serve resized/derived images instead of raw uploads.

Q22: Explain how the update endpoint (`PUT /employees/{id}`) works and what data it accepts.

A22: `EmployeeUpdate` Pydantic model allows partial fields (all Optional). The endpoint builds an `update_data` dict of non-null values, sets `updated_at`, and runs `db.employees.update_one({id}, { $set: update_data })`. It returns the updated document. The endpoint requires authentication.

Q23: How does the frontend handle authentication state and protected routes?

A23: Frontend stores JWT token in `localStorage` and includes it in axios requests. On app startup, `App.js` attempts to fetch `/api/auth/me` and set user state. Protected routes check the presence of user/token and navigate to `/login` if not authenticated.

Q24: How is the CSV/Excel export implemented and what character-encoding concerns exist?

A24: Backend creates CSV with Python `csv.writer` and returns bytes with UTF-8 BOM (`\ufeff`) to ensure Excel recognizes UTF-8. For Excel, `xlsxwriter` is used to produce `.xlsx`. For large exports, stream generation and paginated exports are recommended.

Q25: Describe one design decision you made and why.

A25: Using MongoDB's flexible schema with Pydantic models was chosen to speed development and allow flexible employee fields. Pydantic helps validate and serialize models for API responses. For small/medium apps, this reduces friction; for large scale strict schemas and relational constraints a SQL DB might be preferred.


---

## Expert / Deep-dive questions

Q26: How would you implement optimistic concurrency control for employee updates?

A26: Add a version field (e.g., `version` or check `updated_at`) to documents. On update, include the expected version in the query: `update_one({ id: X, version: N }, { $set: {...}, $inc: { version: 1 } })`. If `modified_count` is 0, a concurrent update happened — return 409 Conflict.

Q27: If you had to migrate employee photos to cloud storage, how would you do it with zero downtime?

A27: Implement dual-write on upload: when users upload new files, store in cloud and local (or only cloud) and return cloud URL. For existing local files, write a migration script that uploads files in batches to cloud and updates DB `photo` fields to new URLs. Serve both local and cloud URLs during migration; update frontend to prefer cloud URLs. After verification and TTL on local files, remove local copies.

Q28: How would you ensure GDPR compliance for employee data?

A28: Key steps:
- Data minimization and role-based access control.
- Provide mechanisms to delete or anonymize data on request (right to be forgotten).
- Maintain records of processing (audit logs), legal basis, and data retention policies.
- Use encryption at rest (DB-level) and in transit (HTTPS), and secure access to backups.

Q29: How would you profile and optimize a slow aggregation query in MongoDB?

A29: Use `explain()` on the aggregation pipeline to identify stages with high cost. Ensure relevant fields are indexed (e.g., department). Reduce pipeline memory by adding `$match` earlier to limit documents. Consider pre-aggregated materialized views or using an analytics DB for heavy reports.

Q30: Describe how you would add role-based access control (RBAC) so HR can edit employees but regular users cannot.

A30: Add roles to user Model (already present). Enforce server-side checks in endpoints by examining `current_user['role']`. Implement decorator or dependency that checks required roles/permissions. Optionally create a permissions mapping and use middleware for fine-grained control. Frontend should hide controls based on role but never trust client-side checks alone.


---

## Quick answers cheat-sheet (short bullets)

- Backend: `backend/server.py` (FastAPI), DB: MongoDB (motor), Auth: JWT + HTTPBearer.
- Important folders: `frontend/src/pages/`, `frontend/src/styles/`, `backend/`.
- Uploads: `POST /api/upload` → `uploads/` folder served at `/api/uploads/<filename>`.
- Employee code: `EMP{count+1}` (race conditions possible).
- Exports: `csv` via csv.writer (BOM), `xlsx` via xlsxwriter, `pdf` via reportlab.
- Tests: backend: pytest + httpx, frontend: Jest/RTL + Cypress for E2E.

---

If you want, I can:
- Add this file into the repository (I can create `VIVA_QUESTIONS.md`).
- Expand any section into more detailed talking points, slides, or sample answers for each question.

Tell me which option you prefer.
