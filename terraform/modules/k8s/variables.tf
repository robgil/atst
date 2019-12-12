variable "region" {
  type        = string
  description = "Region this module and resources will be created in"
}

variable "name" {
  type        = string
  description = "Unique name for the services in this module"
}

variable "environment" {
  type        = string
  description = "Environment these resources reside (prod, dev, staging, etc)"
}

variable "owner" {
  type        = string
  description = "Owner of the environment and resources created in this module"
}

variable "k8s_dns_prefix" {
  type        = string
  description = "A DNS prefix"
}

variable "k8s_node_size" {
  type        = string
  description = "The size of the instance to use in the node pools for k8s"
  default     = "Standard_A1_v2"
}

variable "vnet_subnet_id" {
  description = "Subnet to use for the default k8s pool"
  type        = string
}
