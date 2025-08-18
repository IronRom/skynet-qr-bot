/*
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
*/

terraform {
  backend "s3" {
    bucket         = "skynet-qr-bot-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}