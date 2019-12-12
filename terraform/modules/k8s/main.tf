resource "azurerm_resource_group" "k8s" {
  name     = "${var.name}-${var.environment}-vpc"
  location = var.region
}

resource "azurerm_kubernetes_cluster" "k8s" {
  name                = "${var.name}-${var.environment}-k8s"
  location            = azurerm_resource_group.k8s.location
  resource_group_name = azurerm_resource_group.k8s.name
  dns_prefix          = var.k8s_dns_prefix

  service_principal {
    client_id     = "f05a4457-bd5e-4c63-98e1-89aab42645d0"
    client_secret = "19b69e2c-9f55-4850-87cb-88c67a8dc811"
  }

  default_node_pool {
    name            = "default"
    vm_size         = "Standard_D1_v2"
    os_disk_size_gb = 30
    vnet_subnet_id  = var.vnet_subnet_id
    node_count      = 1
  }

  lifecycle {
    ignore_changes = [
      default_node_pool.0.node_count
    ]
  }

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}