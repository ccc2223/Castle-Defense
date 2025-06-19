# registry.py
"""
Component Registry for Castle Defense Game
Provides centralized access to game components without creating tight coupling
"""

# Component type constants
RESOURCE_MANAGER = "resource_manager"
WAVE_MANAGER = "wave_manager"
ANIMATION_MANAGER = "animation_manager"
CASTLE = "castle"
BUILDINGS = "buildings"
TOWERS = "towers"
ICON_MANAGER = "icon_manager"
SAVE_MANAGER = "save_manager"
STATE_MANAGER = "state_manager"

class ComponentRegistry:
    """
    Central registry for game components.
    Allows components to access only what they need without direct references
    to the entire game instance.
    """
    
    def __init__(self):
        """Initialize an empty component registry"""
        self._components = {}
    
    def register(self, component_type, component):
        """
        Register a component by type
        
        Args:
            component_type: String identifier for the component
            component: The component instance
        """
        self._components[component_type] = component
    
    def get(self, component_type):
        """
        Get a component by type
        
        Args:
            component_type: String identifier for the component
            
        Returns:
            The component instance
            
        Raises:
            KeyError: If the component is not registered
        """
        if component_type not in self._components:
            raise KeyError(f"Component {component_type} not registered")
        return self._components[component_type]
    
    def has(self, component_type):
        """
        Check if a component is registered
        
        Args:
            component_type: String identifier for the component
            
        Returns:
            True if registered, False otherwise
        """
        return component_type in self._components
    
    def unregister(self, component_type):
        """
        Remove a component from the registry
        
        Args:
            component_type: String identifier for the component
            
        Returns:
            The removed component, or None if not found
        """
        return self._components.pop(component_type, None)
