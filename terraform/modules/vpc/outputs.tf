output "subnets" {
  value = azurerm_subnet.subnet["private"].id #FIXME - output should be a map
}
