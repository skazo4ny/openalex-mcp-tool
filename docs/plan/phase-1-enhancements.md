# Phase 1: High-Priority Enhancements

## Overview
Phase 1 focuses on implementing the most critical missing OpenAlex entities that will immediately enhance the research capabilities of the MCP server. These enhancements will provide access to Topics (replacement for Concepts), Institutions (research organizations), and Sources (publication venues).

## Timeline
Estimated completion: 2-3 weeks

## Enhancements Included

### 1. Topics API Implementation
**Priority**: High
**Entity**: Topics (replacement for deprecated Concepts)

#### API Client Updates
- Add `search_topics()` method to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py)
- Add `get_topic_by_id()` method for retrieving specific topics

#### Retriever Module
- Create `openalex_modules/openalex_topic_retriever.py`
- Implement data processing and standardization for Topic entities
- Include metrics calculation (citations per work, recent activity, etc.)

#### MCP Tools
- Add `search_openalex_topics()` function with comprehensive documentation
- Parameters: `topic_name` (str), `max_results` (int, default 5)
- Return structured topic data including field, domain, subfield hierarchy

#### Value Proposition
- Topics provide more accurate and focused research categorization
- 4,500 topics vs 65,000 deprecated concepts = better precision
- Enhanced topic hierarchy with domain → field → subfield → topic structure

### 2. Institutions API Implementation
**Priority**: High
**Entity**: Institutions (universities, research organizations)

#### API Client Updates
- Add `search_institutions()` method to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py)
- Add `get_institution_by_ror()` method for ROR ID lookups

#### Retriever Module
- Create `openalex_modules/openalex_institution_retriever.py`
- Process institution data including geographic information, associated institutions
- Calculate research metrics (publication counts, citation impact, etc.)

#### MCP Tools
- Add `search_openalex_institutions()` function with comprehensive documentation
- Parameters: `institution_name` (str), `max_results` (int, default 5), `country_code` (optional str)
- Return structured institution data including ROR ID, location, research metrics

#### Value Proposition
- Enable research network analysis and collaboration mapping
- Connect authors to their institutional affiliations
- Geographic research distribution analysis

### 3. Sources API Implementation
**Priority**: High
**Entity**: Sources (journals, conferences, repositories)

#### API Client Updates
- Add `search_sources()` method to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py)
- Add `get_source_by_issn()` method for ISSN lookups

#### Retriever Module
- Create `openalex_modules/openalex_source_retriever.py`
- Process source data including publication history, impact metrics
- Handle multiple ISSNs and source types (journal, conference, repository)

#### MCP Tools
- Add `search_openalex_sources()` function with comprehensive documentation
- Parameters: `source_name` (str), `max_results` (int, default 5), `source_type` (optional str)
- Return structured source data including ISSN, publisher, impact factors

#### Value Proposition
- Publication venue analysis and comparison
- Journal/conference reputation assessment
- Open access publishing pattern analysis

## Implementation Steps

### Week 1: API Client and Retriever Modules
1. Extend [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py) with new entity methods
2. Create `openalex_modules/openalex_topic_retriever.py`
3. Create `openalex_modules/openalex_institution_retriever.py`
4. Create `openalex_modules/openalex_source_retriever.py`
5. Implement data processing logic for each entity type

### Week 2: MCP Tool Integration
1. Add new MCP tool functions to [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py)
2. Add new MCP tool functions to [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py)
3. Update initialization code to instantiate new retrievers
4. Implement comprehensive documentation for each tool
5. Add error handling and logging

### Week 3: Testing and Documentation
1. Create unit tests for new retriever modules
2. Create integration tests for new MCP tools
3. Update API documentation in [docs/api.md](file:///Users/max/Documents/code/openalex-mcp-tool/docs/api.md)
4. Update user guide with new tool examples
5. Performance testing and optimization

## Success Criteria
- All three new entity types accessible via MCP tools
- Comprehensive documentation for new tools
- Passing unit and integration tests
- Backward compatibility maintained
- Performance within acceptable limits (< 5s response time for typical queries)

## Dependencies
- Existing OpenAlex API client infrastructure
- PyAlex library (already in requirements)
- Gradio MCP framework (already implemented)

## Risks and Mitigation
- **API rate limiting**: Implement proper caching and retry mechanisms
- **Data quality issues**: Add validation and error handling for malformed data
- **Performance concerns**: Implement pagination and result limiting
- **Backward compatibility**: Ensure new code doesn't break existing functionality

## Testing Requirements
- Unit tests for each new retriever class (80%+ coverage)
- Integration tests for each new MCP tool
- Error handling tests for edge cases
- Performance benchmarks for typical queries
- Validation of data processing accuracy

## Documentation Updates
- Update [readme.md](file:///Users/max/Documents/code/openalex-mcp-tool/readme.md) with new tool list
- Update [docs/api.md](file:///Users/max/Documents/code/openalex-mcp-tool/docs/api.md) with detailed tool specifications
- Update [docs/user-guide.md](file:///Users/max/Documents/code/openalex-mcp-tool/docs/user-guide.md) with usage examples
- Add new tools to MCP client configuration examples