# Test portfolio access for manager role
Write-Host "Testing portfolio access for manager@local"

# Login
$loginBody = '{"username":"manager@local"}'
$loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$loginData = $loginResponse.Content | ConvertFrom-Json
$token = $loginData.access_token

Write-Host "Login successful, token: $($token.Substring(0,20))..."

# Test portfolio endpoint
$headers = @{
    "Authorization" = "Bearer $token"
}
$portfolioResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/data/portfolio" -Method GET -Headers $headers
$portfolioData = $portfolioResponse.Content | ConvertFrom-Json

Write-Host "Portfolio response status: $($portfolioResponse.StatusCode)"
Write-Host "Portfolio data keys: $($portfolioData.PSObject.Properties.Name -join ', ')"

if ($portfolioData.total_portfolio_value) {
    Write-Host "Portfolio value: $($portfolioData.total_portfolio_value)"
}
if ($portfolioData.allocation_percentage) {
    Write-Host "Allocation: $($portfolioData.allocation_percentage | ConvertTo-Json)"
}