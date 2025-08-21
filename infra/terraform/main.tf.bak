provider "aws" {
}

resource "aws_ecr_repository" "skynet-qr-bot" {
    name = "skynet-qr-bot"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
}

resource "aws_s3_bucket" "skynet-qr-bot-terraform-state" {
  bucket = "skynet-qr-bot-terraform-state"
}

resource "aws_s3_bucket_versioning" "skynet-qr-bot-terraform-state" {
  bucket = aws_s3_bucket.skynet-qr-bot-terraform-state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "aws_ecs_cluster" "skynet_qr_bot" {
  name = "skynet-qr-bot-cluster"
}

# Network

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "skynet-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "skynet-public-subnet"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-central-1a"
  map_public_ip_on_launch = false

  tags = {
    Name = "skynet-private-subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "skynet-igw"
  }
}

resource "aws_eip" "nat" {
  tags = {
    Name = "skynet-nat-eip"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "skynet-nat"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "skynet-public-rt"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "skynet-private-rt"
  }
}

resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

## Rule for outbound traffic

resource "aws_security_group" "ecs_tasks" {
  name        = "skynet-ecs-tasks"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Входящий трафик закрыт (по умолчанию)
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
  }

  tags = {
    Name = "skynet-ecs-tasks"
  }
}

# Task difination for ECS

## 
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ecs_execution_secrets" {
  name = "EcsExecutionSecretsPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.bot_token.arn,
          aws_secretsmanager_secret.db_dsn.arn,
          aws_secretsmanager_secret.owner_ids.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_secrets_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_execution_secrets.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "ecsTaskRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ecs_task_secrets" {
  name = "EcsTaskSecretsPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.bot_token.arn,
          aws_secretsmanager_secret.db_dsn.arn,
          aws_secretsmanager_secret.owner_ids.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_secrets_attach" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.ecs_task_secrets.arn
}

resource "aws_secretsmanager_secret" "bot_token" {
  name = "skynet-bot-token"
}

resource "aws_secretsmanager_secret_version" "bot_token_version" {
  secret_id     = aws_secretsmanager_secret.bot_token.id
  secret_string = var.bot_token
}

resource "aws_secretsmanager_secret" "db_dsn" {
  name = "skynet-db-dsn"
}

resource "aws_secretsmanager_secret" "owner_ids" {
  name = "skynet-owner-ids"
}

resource "aws_secretsmanager_secret_version" "owner_ids_version" {
  secret_id     = aws_secretsmanager_secret.owner_ids.id
  secret_string = var.owner_ids
}

resource "aws_secretsmanager_secret_version" "db_dsn_version" {
  secret_id     = aws_secretsmanager_secret.db_dsn.id
  secret_string = var.db_dsn
}

resource "aws_cloudwatch_log_group" "skynet_qr_bot" {
  name              = "/ecs/skynet-qr-bot"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "skynet_qr_bot" {
  family                   = "skynet-qr-bot-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
  {
    name  = "skynet-qr-bot"
    image = "${aws_ecr_repository.skynet-qr-bot.repository_url}:latest"
    essential = true

    secrets = [
      { name = "BOT_TOKEN",  valueFrom = aws_secretsmanager_secret_version.bot_token_version.arn },
      { name = "DB_DSN",     valueFrom = aws_secretsmanager_secret_version.db_dsn_version.arn },
      { name = "OWNER_IDS",  valueFrom = aws_secretsmanager_secret_version.owner_ids_version.arn }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/skynet-qr-bot"
        "awslogs-region"        = "eu-central-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }
])

  execution_role_arn = aws_iam_role.ecs_task_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn
}

resource "aws_ecs_service" "skynet_qr_bot_service" {
  name            = "skynet-qr-bot-service"
  cluster         = aws_ecs_cluster.skynet_qr_bot.id
  task_definition = aws_ecs_task_definition.skynet_qr_bot.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private.id]
    security_groups = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
}
