# Deploy to Cloud Run
# Usage: ./deploy.ps1 <PROJECT_ID>

param (
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

Write-Host "Setting project to $ProjectId..."
gcloud config set project $ProjectId

Write-Host "Enabling APIs..."
gcloud services enable run.googleapis.com firestore.googleapis.com

Write-Host "Building Container Image..."
$ImageUri = "gcr.io/$ProjectId/halflife"

gcloud builds submit --tag $ImageUri

Write-Host "Deploying to Cloud Run..."
# Deploying as a public service (allow-unauthenticated) because the App has its own Password Gate.
gcloud run deploy halflife `
    --image $ImageUri `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars APP_PASSWORD=secret, GOOGLE_CLOUD_PROJECT=$ProjectId

Write-Host "Deployment Complete!"
