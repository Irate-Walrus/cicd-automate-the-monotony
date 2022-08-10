terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0.2"
    }
  }

  backend "azurerm" {}

  required_version = ">= 1.2.0"
}

provider "azurerm" {
  features {}
}

module "azure_region" {
  source  = "claranet/regions/azurerm"
  version = ">= 6.0.0"

  azure_region = var.resource_group_location
}

module "naming" {
  source = "Azure/naming/azurerm"
  suffix = [var.project_name, var.environment, module.azure_region.location_short]
}

locals {
  tags = {
    project     = var.project_name
    environment = var.environment
    region      = module.azure_region.location_slug
  }
}

resource "azurerm_resource_group" "rg" {
  name     = module.naming.resource_group.name
  location = var.resource_group_location
  tags     = local.tags
}

resource "azurerm_storage_account" "store" {
  name                     = module.naming.storage_account.name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.tags
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.store.name
  container_access_type = "private"
}

resource "azurerm_service_plan" "plan" {
  name                = module.naming.app_service_plan.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "S1"
  tags                = local.tags
}

resource "azurerm_linux_web_app" "api" {
  name                = module.naming.app_service.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.plan.id
  tags                = local.tags

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false
    DOCKER_REGISTRY_SERVER_URL          = var.container_registry
    DOCKER_REGISTRY_SERVER_USERNAME     = var.container_registry_user
    DOCKER_REGISTRY_SERVER_PASSWORD     = var.container_registry_password
    DB_ASYNC_CONNECTION_STR             = "sqlite+aiosqlite:///./test_todo.db"
    WEBSITES_PORT                       = 8000
  }

  identity {
    type = "SystemAssigned"
  }
  site_config {
    use_32_bit_worker = false
  }
}