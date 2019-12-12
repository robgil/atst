data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "keyvault" {
  name     = "${var.name}-${var.environment}-rg"
  location = var.region
}

resource "random_id" "server" {
  keepers = {
    ami_id = 1
  }

  byte_length = 8
}

resource "azurerm_key_vault" "keyvault" {
  name                = "${var.name}-${var.environment}-keyvault"
  location            = azurerm_resource_group.keyvault.location
  resource_group_name = azurerm_resource_group.keyvault.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "premium"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.service_principal_object_id

    key_permissions = [
      "create",
      "get",
    ]

    secret_permissions = [
      "set",
      "get",
      "delete",
    ]
  }

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}