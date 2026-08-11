# JWT Auth Prototype

Flask + PyMongo + PyJWT + bcrypt backend, plain React frontend, MongoDB Atlas as the DB.
Two routes to sign up / log in, one protected route (`/me`) to prove the JWT works.

## 1. MongoDB Atlas

1. Create a free-tier cluster at https://cloud.mongodb.com.
2. Database Access -> add a user with a username/password.
3. Network Access -> add your current IP (or `0.0.0.0/0` for quick local testing).
4. Connect -> "Drivers" -> copy the connection string. Add a db name, e.g. `.../authdb?...`.

## 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: paste your MONGO_URI, set a random JWT_SECRET
python app.py
```

Runs on `http://localhost:5000`. make this port to other than 5001, otherwise it raises a CORS issue.

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

## 4. Test the loop

Via the UI: Signup -> Login -> Dashboard (calls `/me` with the stored token).

Via curl:

```bash
# signup
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123"}'

# login -> copy the token from the response
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"secret123"}'

# access protected route
curl http://localhost:5000/me -H "Authorization: Bearer <token>"

# missing token -> 401
curl http://localhost:5000/me

# invalid token -> 401
curl http://localhost:5000/me -H "Authorization: Bearer garbage"

# expired token -> wait past JWT_EXPIRY_MINUTES (30 min, or lower it in app.py to test faster) -> 401
```
