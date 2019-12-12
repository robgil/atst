variable "environment" {
  default = "dev"
}

variable "region" {
  default = "eastus2"

}

variable "owner" {
  default = "dev"
}

variable "name" {
  default = "cloudzero"
}

variable "virtual_network" {
  type    = string
  default = "10.1.0.0/16"
}


variable "networks" {
  type = map
  default = {
    #format
    #name         = "CIDR, route table, Security Group Name"
    public  = "10.1.1.0/24,public"  # LBs
    private = "10.1.2.0/24,private" # k8s, postgres, redis, dns, ad
  }
}

variable "route_tables" {
  description = "Route tables and their default routes"
  type        = map
  default = {
    public  = "Internet"
    private = "VnetLocal"
  }
}

variable "dns_servers" {
  type    = list
  default = ["10.1.2.4", "10.1.2.5"]
}

variable "k8s_node_size" {
  type    = string
  default = "Standard_A1_v2"
}

variable "k8s_dns_prefix" {
  type    = string
  default = "atat"
}
