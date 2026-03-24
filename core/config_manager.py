"""
Configuration Manager

Handles loading and managing configurations from multiple sources:
- Environment variables
- YAML configuration files
- Azure Key Vault (for secrets)
"""

import os
import yaml
from typing import Any, Dict, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential  # type: ignore
from azure.keyvault.secrets import SecretClient  # type: ignore

# Load .env file at module import time to ensure all env vars are available
load_dotenv(override=True)


class ConfigManager:
    """
    Centralized configuration management with support for:
    - Environment-based configurations (dev, staging, prod)
    - Environment variables
    - Azure Key Vault for secrets
    - YAML configuration files
    """
    
    def __init__(
        self,
        config_dir: str = "configs",
        environment: Optional[str] = None,
        use_key_vault: bool = False,
        key_vault_url: Optional[str] = None
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            environment: Environment name (dev, staging, prod)
            use_key_vault: Whether to use Azure Key Vault for secrets
            key_vault_url: Azure Key Vault URL
        """
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv("ENVIRONMENT", "dev")
        self.use_key_vault = use_key_vault
        self.key_vault_url = key_vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        
        # Note: .env is loaded at module import time (see top of file)
        
        # Initialize configurations
        self.config: Dict[str, Any] = {}
        self.secrets: Dict[str, str] = {}
        
        # Setup logging
        self.logger = logging.getLogger("config_manager")
        
        # Load configurations
        self._load_configurations()
        
        # Initialize Key Vault client if enabled
        self.key_vault_client = None
        if self.use_key_vault and self.key_vault_url:
            self._init_key_vault()
    
    def _load_configurations(self) -> None:
        """Load configurations from YAML files"""
        try:
            # Load base configuration
            base_config_path = self.config_dir / "config.yaml"
            if base_config_path.exists():
                with open(base_config_path, 'r') as f:
                    base_config = yaml.safe_load(f) or {}
                    self.config.update(base_config)
                self.logger.info(f"Loaded base configuration from {base_config_path}")
            
            # Load environment-specific configuration
            env_config_path = self.config_dir / f"config.{self.environment}.yaml"
            if env_config_path.exists():
                with open(env_config_path, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                    self._deep_update(self.config, env_config)
                self.logger.info(f"Loaded {self.environment} configuration from {env_config_path}")
            
            # Override with environment variables
            self._load_from_environment()
            
            self.logger.info(f"Configuration loaded for environment: {self.environment}")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {str(e)}")
            raise
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        # Azure OpenAI
        if os.getenv("AZURE_OPENAI_ENDPOINT"):
            if "azure_openai" not in self.config:
                self.config["azure_openai"] = {}
            self.config["azure_openai"]["endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.config["azure_openai"]["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
            self.config["azure_openai"]["deployment_name"] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            self.config["azure_openai"]["api_version"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Application Insights
        if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
            if "logging" not in self.config:
                self.config["logging"] = {}
            self.config["logging"]["app_insights_connection_string"] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    def _init_key_vault(self) -> None:
        """Initialize Azure Key Vault client"""
        try:
            credential = DefaultAzureCredential()
            self.key_vault_client = SecretClient(
                vault_url=self.key_vault_url,
                credential=credential
            )
            self.logger.info(f"Connected to Azure Key Vault: {self.key_vault_url}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Key Vault: {str(e)}")
            self.key_vault_client = None
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update of nested dictionaries"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        Supports nested keys with dot notation (e.g., "azure_openai.endpoint")
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        Supports nested keys with dot notation.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from Azure Key Vault or environment variables.
        
        Args:
            secret_name: Name of the secret
            default: Default value if secret not found
            
        Returns:
            Secret value
        """
        # Check cache first
        if secret_name in self.secrets:
            return self.secrets[secret_name]
        
        # Try Key Vault
        if self.key_vault_client:
            try:
                secret = self.key_vault_client.get_secret(secret_name)
                self.secrets[secret_name] = secret.value
                return secret.value
            except Exception as e:
                self.logger.warning(f"Failed to get secret from Key Vault: {str(e)}")
        
        # Fall back to environment variable
        env_value = os.getenv(secret_name)
        if env_value:
            self.secrets[secret_name] = env_value
            return env_value
        
        return default
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def reload(self) -> None:
        """Reload configurations from files"""
        self.config = {}
        self.secrets = {}
        self._load_configurations()
        self.logger.info("Configuration reloaded")
