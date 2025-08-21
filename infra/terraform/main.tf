provider "aws" {
  region = "eu-central-1"
}

##########################
# SECRETS
###########################
resource "aws_secretsmanager_secret" "bot_token" {
  name = "bot_token"
}

resource "aws_secretsmanager_secret_version" "bot_token_version" {
  secret_id     = aws_secretsmanager_secret.bot_token.id
  secret_string = var.bot_token
}

resource "aws_secretsmanager_secret" "db_dsn" {
  name = "db_dsn"
}

resource "aws_secretsmanager_secret_version" "db_dsn_version" {
  secret_id     = aws_secretsmanager_secret.db_dsn.id
  secret_string = var.db_dsn
}

resource "aws_secretsmanager_secret" "owner_ids" {
  name = "owner_ids"
}

resource "aws_secretsmanager_secret_version" "owner_ids_version" {
  secret_id     = aws_secretsmanager_secret.owner_ids.id
  secret_string = var.owner_ids
}

resource "aws_secretsmanager_secret" "service_qr_url" {
  name = "service_qr_url"
}

resource "aws_secretsmanager_secret_version" "service_qr_url_version" {
  secret_id     = aws_secretsmanager_secret.service_qr_url.id
  secret_string = var.service_qr_url
}

##########################
# ECR Repositories
##########################
resource "aws_ecr_repository" "skynet_bot" {
  name                 = "skynet-bot"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "skynet_qr" {
  name                 = "skynet-qr-service"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

##########################
# VPC, Subnets, IGW
##########################
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "skynet-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = true
  tags = { Name = "skynet-public-subnet" }
}

resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = false
  tags = { Name = "skynet-private-subnet" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "skynet-igw" }
}

resource "aws_eip" "bot_eip" {
  vpc = true
}

##########################
# Route Tables
##########################
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "skynet-public-rt" }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  # Приватная подсеть пока без NAT
  tags = { Name = "skynet-private-rt" }
}

resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

##########################
# Security Groups
##########################
resource "aws_security_group" "ecs_tasks_public" {
  name   = "skynet-ecs-public"
  vpc_id = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
  }
}

resource "aws_security_group" "ecs_tasks_private" {
  name   = "skynet-ecs-private"
  vpc_id = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
  }
}

##########################
# ECS Cluster
##########################
resource "aws_ecs_cluster" "skynet" {
  name = "skynet-cluster"
}

##########################
# IAM Roles
##########################
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

##########################
# CloudWatch Logs
##########################
resource "aws_cloudwatch_log_group" "skynet" {
  name              = "/ecs/skynet"
  retention_in_days = 14
}

##########################
# ECS Task Definitions
##########################
resource "aws_ecs_task_definition" "bot" {
  family                   = "skynet-bot-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "skynet-bot"
      image     = "${aws_ecr_repository.skynet_bot.repository_url}:latest"
      essential = true

      secrets = [
        { name="BOT_TOKEN", valueFrom=aws_secretsmanager_secret_version.bot_token_version.arn },
        { name="DB_DSN", valueFrom=aws_secretsmanager_secret_version.db_dsn_version.arn },
        { name="OWNER_IDS", valueFrom=aws_secretsmanager_secret_version.owner_ids_version.arn },
        { name="SERVICE_QR_URL", valueFrom=aws_secretsmanager_secret_version.service_qr_url_version.arn }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.skynet.name
          "awslogs-region"        = "eu-central-1"
          "awslogs-stream-prefix" = "bot"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "qr" {
  family                   = "skynet-qr-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "skynet-qr-service"
      image     = "${aws_ecr_repository.skynet_qr.repository_url}:latest"
      essential = true

      secrets = [
        { name="DB_DSN", valueFrom=aws_secretsmanager_secret_version.db_dsn_version.arn },
        { name="SERVICE_QR_URL", valueFrom=aws_secretsmanager_secret_version.service_qr_url_version.arn }
      ]

      portMappings = [{ containerPort = 8001, protocol = "tcp" }]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.skynet.name
          "awslogs-region"        = "eu-central-1"
          "awslogs-stream-prefix" = "qr-service"
        }
      }
    }
  ])
}

##########################
# ECS Services
##########################
resource "aws_ecs_service" "bot" {
  name            = "skynet-bot-service"
  cluster         = aws_ecs_cluster.skynet.id
  task_definition = aws_ecs_task_definition.bot.arn
  desired_count   = 0
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public.id]
    security_groups  = [aws_security_group.ecs_tasks_public.id]
    assign_public_ip = true
  }
}

resource "aws_ecs_service" "qr" {
  name            = "skynet-qr-service"
  cluster         = aws_ecs_cluster.skynet.id
  task_definition = aws_ecs_task_definition.qr.arn
  desired_count   = 0
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private.id]
    security_groups  = [aws_security_group.ecs_tasks_private.id]
    assign_public_ip = false
  }
}

##########################
# VPC Endpoints for private access
##########################
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-central-1.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.eu-central-1.secretsmanager"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.ecs_tasks_private.id]
}

resource "aws_vpc_endpoint" "cloudwatch_logs" {
  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.eu-central-1.logs"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.ecs_tasks_private.id]
}