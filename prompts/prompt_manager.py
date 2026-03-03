"""
Prompt Manager

Manages prompt templates with versioning and dynamic variable substitution.
"""

from typing import Any, Dict, List, Optional
import logging
from pathlib import Path
import yaml
from datetime import datetime

from core.logging_service import LoggingService


class PromptTemplate:
    """Prompt template with metadata"""
    
    def __init__(
        self,
        name: str,
        template: str,
        variables: List[str],
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.template = template
        self.variables = variables
        self.version = version
        self.description = description
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
    
    def render(self, **kwargs) -> str:
        """
        Render template with variables.
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Rendered prompt
        """
        # Check for missing variables
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        return self.template.format(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
            "version": self.version,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class PromptManager:
    """
    Manages prompt templates with:
    - Version control
    - Template loading from files
    - Variable substitution
    - Template validation
    """
    
    def __init__(
        self,
        prompts_dir: str = "prompts",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt templates
            logger: Optional custom logger
        """
        self.prompts_dir = Path(prompts_dir)
        self.logger = logger or LoggingService.get_logger("prompt_manager")
        
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}  # name -> version -> template
        
        self._load_templates()
        
        self.logger.info(f"Initialized PromptManager with {len(self.templates)} templates")
    
    def _load_templates(self) -> None:
        """Load prompt templates from files"""
        if not self.prompts_dir.exists():
            self.logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return
        
        # Load YAML template files
        for template_file in self.prompts_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r') as f:
                    data = yaml.safe_load(f)
                    
                    name = data.get("name")
                    if not name:
                        self.logger.warning(f"Template missing name: {template_file}")
                        continue
                    
                    template = PromptTemplate(
                        name=name,
                        template=data.get("template", ""),
                        variables=data.get("variables", []),
                        version=data.get("version", "1.0.0"),
                        description=data.get("description", ""),
                        metadata=data.get("metadata", {})
                    )
                    
                    if name not in self.templates:
                        self.templates[name] = {}
                    
                    self.templates[name][template.version] = template
                    self.logger.info(f"Loaded template: {name} v{template.version}")
                    
            except Exception as e:
                self.logger.error(f"Error loading template {template_file}: {str(e)}")
    
    def register_template(
        self,
        name: str,
        template: str,
        variables: List[str],
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """
        Register a new prompt template.
        
        Args:
            name: Template name
            template: Template string
            variables: List of variable names
            version: Template version
            description: Template description
            metadata: Additional metadata
            
        Returns:
            Created template
        """
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            variables=variables,
            version=version,
            description=description,
            metadata=metadata
        )
        
        if name not in self.templates:
            self.templates[name] = {}
        
        self.templates[name][version] = prompt_template
        self.logger.info(f"Registered template: {name} v{version}")
        
        return prompt_template
    
    def get_template(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """
        Get a prompt template.
        
        Args:
            name: Template name
            version: Specific version (latest if not specified)
            
        Returns:
            Prompt template or None
        """
        if name not in self.templates:
            return None
        
        versions = self.templates[name]
        
        if version:
            return versions.get(version)
        else:
            # Get latest version
            latest_version = max(versions.keys())
            return versions[latest_version]
    
    def render_template(
        self,
        name: str,
        version: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            name: Template name
            version: Specific version
            **kwargs: Variable values
            
        Returns:
            Rendered prompt
        """
        template = self.get_template(name, version)
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        return template.render(**kwargs)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            List of template information
        """
        templates_info = []
        
        for name, versions in self.templates.items():
            for version, template in versions.items():
                templates_info.append({
                    "name": name,
                    "version": version,
                    "description": template.description,
                    "variables": template.variables
                })
        
        return templates_info
    
    def save_template(
        self,
        template: PromptTemplate,
        overwrite: bool = False
    ) -> None:
        """
        Save template to file.
        
        Args:
            template: Template to save
            overwrite: Whether to overwrite existing file
        """
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.prompts_dir / f"{template.name}_v{template.version}.yaml"
        
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Template file already exists: {file_path}")
        
        data = template.to_dict()
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        self.logger.info(f"Saved template to {file_path}")
    
    def reload_templates(self) -> None:
        """Reload all templates from files"""
        self.templates = {}
        self._load_templates()
        self.logger.info("Templates reloaded")
