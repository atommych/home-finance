variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "home-finance"
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
  sensitive   = true
}

variable "supabase_key" {
  description = "Supabase anon key"
  type        = string
  sensitive   = true
}

variable "image" {
  description = "Docker image to deploy (e.g., europe-west1-docker.pkg.dev/PROJECT/home-finance/app:latest)"
  type        = string
}
