output "ecr_repository_url" {
  description = "URL of the Amazon ECR Repository"
  value       = aws_ecr_repository.api_repo.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS Cluster"
  value       = aws_ecs_cluster.ecs_cluster.name
}

output "ecs_service_name" {
  description = "Name of the ECS Service"
  value       = aws_ecs_service.ecs_service.name
}

output "ecs_security_group_id" {
  description = "ID of the Security Group assigned to the ECS task"
  value       = aws_security_group.ecs_sg.id
}
