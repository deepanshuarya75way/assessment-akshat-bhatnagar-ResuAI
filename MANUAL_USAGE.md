# Manual usage guide

This app runs in the background and exposes a small HTTP API for manual actions that need human input.

## 1. Start the app
From the project folder:

```powershell
./start_server.ps1
```

Open:

- http://localhost:8000/  -> simple status page
- http://localhost:8000/health -> health check

## 2. Register a user
Use the users API.

### Example with PowerShell
```powershell
$body = @{
  name = 'John Doe'
  email = 'john@example.com'
  phone = '9999999999'
  college = 'ABC College'
  branch = 'Computer Science'
  cgpa = 8.7
  graduation_year = 2025
  linkedin_url = 'https://linkedin.com/in/john'
  github_url = 'https://github.com/john'
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/users' -ContentType 'application/json' -Body $body
```

### Browser alternative
Open:

- http://localhost:8000/docs

Then use the Users section to create a user.

## 3. Upload a resume
You need a user id first.

### Example with PowerShell
```powershell
$path = 'C:\path\to\resume.pdf'
$headers = @{ "Content-Type" = "multipart/form-data" }
$boundary = [System.Guid]::NewGuid().ToString()

$body = [System.IO.File]::ReadAllBytes($path)

# If you prefer a simpler approach, use curl:
# curl -X POST "http://localhost:8000/resumes/upload/1" -F "file=@C:\path\to\resume.pdf"
```

### Recommended way
Use the Swagger UI:

- http://localhost:8000/docs
- Open the Resume section
- Use POST /resumes/upload/{user_id}
- Choose a PDF file

## 4. Delete a resume
Use the delete endpoint in Swagger or call it from PowerShell:

```powershell
Invoke-RestMethod -Method Delete -Uri 'http://localhost:8000/resumes/1'
```

## 5. Delete a user
Use the users delete endpoint if available in your API version, or remove the record from the database if needed.

## 6. Manual actions that need UI interaction
These are easiest through the Swagger docs:

- register a user
- upload a resume
- delete a resume
- inspect parsed resume data
- trigger a manual graph run for a specific email

## 7. Useful endpoints
- GET /health
- GET /
- GET /users
- POST /users
- GET /resumes
- POST /resumes/upload/{user_id}
- GET /resumes/parsed/{user_id}
- POST /graph/{email_id}

## 8. If you want a browser-based mini dashboard
You can open the Swagger UI at:

- http://localhost:8000/docs

That gives you a simple UI to perform manual tasks without writing code.
