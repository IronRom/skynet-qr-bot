variable "aws_region" {}
variable "aws_access_key" {}
variable "aws_secret_key" {}

variable "bot_token" {
  description = "Telegram bot token"
  type        = string
}

variable "owner_ids" {
  description = "Bot owner IDs"
  type        = string
}

variable "use_redis" {
  description = "Use Redis"
  type        = string
  default     = "False"
}

variable "redis_host" {
  description = "Redis host"
  type        = string
  default     = "localhost"
}

variable "service_qr_url" {
  description = "Service QR URL"
  type        = string
}

variable "db_dsn" {
  description = "Database DSN"
  type        = string
}