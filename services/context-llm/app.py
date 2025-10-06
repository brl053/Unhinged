#!/usr/bin/env python3
"""
Context-Aware LLM Service - Flask HTTP API
Provides contextual prompt generation and project-aware text processing
"""

import os
import logging
import time
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, List, Optional
import asyncio

from context_manager import context_manager, ContextQuery, ContextType
from indexers.documentation_indexer import documentation_indexer
from indexers.codebase_indexer import codebase_indexer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service state
service_ready = False
startup_time = None

def initialize_service():
    """Initialize the context-aware LLM service"""
    global service_ready, startup_time
    
    try:
        logger.info("🔥 Initializing Context-Aware LLM Service...")
        startup_time = time.time()
        
        # Initialize context manager
        logger.info("Scanning project context...")
        context_stats = context_manager.scan_project_context(force_refresh=True)
        logger.info(f"Context scan completed: {context_stats}")
        
        # Initialize documentation indexer
        logger.info("Initializing documentation indexer...")
        # The indexer initializes automatically
        
        service_ready = True
        total_time = time.time() - startup_time
        logger.info(f"✅ Context-Aware LLM Service ready in {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        service_ready = False
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        context_stats = context_manager.get_project_context_summary()
        index_stats = documentation_indexer.get_index_stats()
        
        health_data = {
            'status': 'healthy' if service_ready else 'initializing',
            'service': 'context-aware-llm',
            'version': '1.0.0',
            'ready': service_ready,
            'startup_time': startup_time,
            'uptime': time.time() - startup_time if startup_time else 0,
            'context_stats': context_stats,
            'index_stats': index_stats,
            'capabilities': [
                'contextual-prompt-generation',
                'project-documentation-search',
                'ui-component-analysis',
                'architecture-understanding',
                'codebase-context-extraction'
            ]
        }
        
        return jsonify(health_data), 200 if service_ready else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'context-aware-llm'
        }), 500

@app.route('/generate-prompt', methods=['POST'])
def generate_contextual_prompt():
    """Generate contextual prompt for vision analysis"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        data = request.get_json()
        
        # Required parameters
        base_prompt = data.get('base_prompt', 'Analyze this image.')
        analysis_type = data.get('analysis_type', 'screenshot')
        
        # Optional parameters
        context_types = data.get('context_types', ['documentation', 'ui_components'])
        max_context_items = data.get('max_context_items', 5)
        image_metadata = data.get('image_metadata', {})
        
        # Map context types
        mapped_context_types = []
        for ctx_type in context_types:
            if ctx_type == 'documentation':
                mapped_context_types.append(ContextType.DOCUMENTATION)
            elif ctx_type == 'ui_components':
                mapped_context_types.append(ContextType.UI_COMPONENTS)
            elif ctx_type == 'api_endpoints':
                mapped_context_types.append(ContextType.API_ENDPOINTS)
            elif ctx_type == 'architecture':
                mapped_context_types.append(ContextType.ARCHITECTURE)
        
        # Generate context query based on analysis type
        if analysis_type == 'screenshot':
            query_text = "ui interface components buttons forms layout design"
        elif analysis_type == 'ui_component':
            query_text = "react component props interface design system"
        elif analysis_type == 'document':
            query_text = "documentation api architecture design"
        else:
            query_text = base_prompt
        
        # Query context
        context_query = ContextQuery(
            query=query_text,
            context_types=mapped_context_types,
            max_results=max_context_items
        )
        
        context_items = context_manager.query_context(context_query)
        
        # Build enhanced prompt
        enhanced_prompt = _build_enhanced_prompt(
            base_prompt, 
            analysis_type, 
            context_items, 
            image_metadata
        )
        
        return jsonify({
            'success': True,
            'enhanced_prompt': enhanced_prompt,
            'base_prompt': base_prompt,
            'context_items_used': len(context_items),
            'context_summary': [
                {
                    'title': item.title,
                    'type': item.type.value,
                    'relevance_score': item.relevance_score
                }
                for item in context_items
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        return jsonify({'error': f'Prompt generation failed: {str(e)}'}), 500

@app.route('/search-documentation', methods=['POST'])
def search_documentation():
    """Search project documentation"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Search documentation
        results = documentation_indexer.search_documentation(query, k=max_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Documentation search failed: {e}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/get-ui-context', methods=['POST'])
def get_ui_context():
    """Get UI-specific context for screenshot analysis"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        data = request.get_json()
        image_metadata = data.get('image_metadata', {})
        
        ui_context = context_manager.get_ui_context_for_screenshot(image_metadata)
        
        return jsonify({
            'success': True,
            'ui_context': ui_context
        }), 200
        
    except Exception as e:
        logger.error(f"UI context retrieval failed: {e}")
        return jsonify({'error': f'UI context retrieval failed: {str(e)}'}), 500

@app.route('/refresh-context', methods=['POST'])
def refresh_context():
    """Refresh project context cache"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        logger.info("Refreshing project context...")
        start_time = time.time()
        
        # Refresh context manager
        context_stats = context_manager.scan_project_context(force_refresh=True)
        
        refresh_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'refresh_time': refresh_time,
            'context_stats': context_stats,
            'message': 'Context refreshed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Context refresh failed: {e}")
        return jsonify({'error': f'Context refresh failed: {str(e)}'}), 500

@app.route('/context-stats', methods=['GET'])
def get_context_stats():
    """Get context statistics"""
    try:
        context_summary = context_manager.get_project_context_summary()
        index_stats = documentation_indexer.get_index_stats()
        
        return jsonify({
            'context_summary': context_summary,
            'index_stats': index_stats,
            'service_uptime': time.time() - startup_time if startup_time else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

def _build_enhanced_prompt(
    base_prompt: str, 
    analysis_type: str, 
    context_items: List[Any], 
    image_metadata: Dict[str, Any]
) -> str:
    """Build enhanced prompt with context"""
    
    # Start with base prompt
    enhanced_parts = [base_prompt]
    
    # Add analysis type specific guidance
    if analysis_type == 'screenshot':
        enhanced_parts.append("""
Focus on UI elements, layout, and user interface components. Pay attention to:
- Interactive elements (buttons, forms, inputs)
- Navigation and menu structures
- Visual hierarchy and design patterns
- Text content and readability
- Error states or notifications
""")
    elif analysis_type == 'ui_component':
        enhanced_parts.append("""
Analyze this UI component focusing on:
- Component type and purpose
- Design system adherence
- Interactive states and behaviors
- Accessibility considerations
- Integration with the overall interface
""")
    
    # Add project context if available
    if context_items:
        enhanced_parts.append("\nProject Context:")
        
        for item in context_items[:3]:  # Limit to top 3 most relevant
            enhanced_parts.append(f"- {item.title}: {item.content[:200]}...")
    
    # Add technical context
    enhanced_parts.append("""
Technical Context:
- Frontend: React 19 + TypeScript
- Backend: Kotlin + Ktor
- Architecture: Microservices with Clean Architecture
- Design System: Custom components with styled-components
""")
    
    return "\n".join(enhanced_parts)

if __name__ == '__main__':
    # Initialize service
    initialize_service()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=8002, debug=False)
