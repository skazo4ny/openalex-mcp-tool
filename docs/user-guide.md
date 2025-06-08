# OpenAlex Explorer MCP Server - User Guide

## Overview

The OpenAlex Explorer MCP Server provides access to academic research data through both a user-friendly web interface and programmatic MCP (Model Context Protocol) access. This guide covers how to use both interfaces effectively.

## Table of Contents

1. [Web Interface Usage](#web-interface-usage)
2. [MCP Client Integration](#mcp-client-integration)
3. [Search Strategies](#search-strategies)
4. [Data Interpretation](#data-interpretation)
5. [Common Use Cases](#common-use-cases)
6. [Tips and Best Practices](#tips-and-best-practices)

## Web Interface Usage

### Accessing the Interface

Navigate to the deployment URL (e.g., your Hugging Face Spaces URL) to access the Gradio interface.

### Interface Components

#### 1. Paper Search Tab
- **Query Field**: Enter search terms for papers (title, abstract, keywords)
- **Date Filters**: 
  - From Date: Start of publication date range (YYYY-MM-DD)
  - To Date: End of publication date range (YYYY-MM-DD)
- **Results Count**: Number of papers to return (1-50)
- **Search Button**: Execute the search

**Example Searches:**
- `"machine learning"` - Papers about machine learning
- `"climate change adaptation"` - Environmental research
- `"neural networks deep learning"` - AI/ML papers
- `"covid-19 vaccine efficacy"` - Pandemic research

#### 2. DOI Lookup Tab
- **DOI Field**: Enter a specific DOI to retrieve publication details
- **Lookup Button**: Fetch the publication

**Example DOIs:**
- `10.1038/nature12373`
- `10.1126/science.1259855`
- `10.1016/j.cell.2020.04.011`

#### 3. Author Search Tab
- **Query Field**: Enter author name or affiliation
- **Results Count**: Number of authors to return (1-50)
- **Search Button**: Find matching authors

**Example Searches:**
- `"Geoffrey Hinton"` - Specific researcher
- `"MIT artificial intelligence"` - Authors from institution
- `"Smith J"` - Common name patterns

#### 4. Concept Search Tab
- **Query Field**: Enter academic concept or field
- **Results Count**: Number of concepts to return (1-50)
- **Search Button**: Explore concepts

**Example Searches:**
- `"machine learning"` - Core concept
- `"bioinformatics"` - Interdisciplinary field
- `"quantum computing"` - Emerging technology

### Understanding Results

#### Paper Search Results
Each paper result includes:
- **Title**: Full paper title with link
- **Authors**: List of authors with affiliations
- **Publication Year**: Year of publication
- **DOI**: Digital Object Identifier (if available)
- **Abstract**: Paper summary (if available)
- **Citation Count**: Number of times cited
- **Journal/Venue**: Publication venue

#### Author Results
Each author result includes:
- **Name**: Author's full name
- **Affiliation**: Current or most recent institution
- **Works Count**: Number of published papers
- **Citation Count**: Total citations received
- **H-index**: Research impact metric
- **Research Areas**: Primary fields of study

#### Concept Results
Each concept result includes:
- **Name**: Concept name
- **Description**: Brief explanation
- **Level**: Hierarchical level (0-5, where 0 is most general)
- **Works Count**: Number of papers associated
- **Related Concepts**: Connected academic areas

## MCP Client Integration

### Setting Up MCP Client

The server can be integrated with any MCP-compatible client. Here's how to connect:

#### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "openalex-explorer": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

**Note**: Replace `localhost:7860` with your deployment URL for production use.

#### Custom MCP Client

```python
import asyncio
from mcp import Client

async def main():
    # Connect to the server via SSE
    async with Client("sse", url="http://localhost:7860/gradio_api/mcp/sse") as client:
        # Search for papers
        result = await client.call_tool("search_openalex_papers", {
            "query": "artificial intelligence",
            "from_publication_date": "2020-01-01",
            "results_count": 5
        })
        
        print("Search Results:")
        print(result.content[0].text)

asyncio.run(main())
```

### Available MCP Tools

#### search_openalex_papers
```python
# Search for recent AI papers
await client.call_tool("search_openalex_papers", {
    "query": "artificial intelligence",
    "from_publication_date": "2023-01-01",
    "to_publication_date": "2023-12-31",
    "results_count": 10
})
```

#### get_publication_by_doi
```python
# Get specific paper details
await client.call_tool("get_publication_by_doi", {
    "doi": "10.1038/nature12373"
})
```

#### search_openalex_authors
```python
# Find AI researchers
await client.call_tool("search_openalex_authors", {
    "query": "Geoffrey Hinton",
    "results_count": 5
})
```

#### search_openalex_concepts
```python
# Explore research concepts
await client.call_tool("search_openalex_concepts", {
    "query": "machine learning",
    "results_count": 10
})
```

## Search Strategies

### Effective Query Construction

#### 1. Paper Searches

**Broad Topics:**
- Use general terms: `"climate change"`, `"machine learning"`
- Combine related terms: `"neural networks deep learning"`

**Specific Research:**
- Include methodology: `"randomized controlled trial depression"`
- Add context: `"covid-19 vaccine mrna efficacy"`

**Author-Specific:**
- Include author in query: `"Hinton neural networks"`
- Combine with institution: `"MIT computer vision"`

#### 2. Author Searches

**Full Names:**
- Use quotes for exact matches: `"Geoffrey E. Hinton"`
- Try variations: `"G. Hinton"`, `"Geoffrey Hinton"`

**Institutional Searches:**
- Include affiliation: `"Stanford University machine learning"`
- Department specific: `"MIT CSAIL artificial intelligence"`

**Research Area:**
- Combine field with common surnames: `"Smith computer science"`

#### 3. Concept Searches

**Hierarchical Exploration:**
- Start broad: `"artificial intelligence"`
- Get specific: `"transformer neural networks"`

**Interdisciplinary Areas:**
- Use compound terms: `"computational biology"`
- Explore connections: `"machine learning medicine"`

### Date Filtering Tips

- **Recent Research**: Last 2-3 years for cutting-edge work
- **Historical Analysis**: Specific decades for trend analysis
- **Comprehensive Reviews**: Wider date ranges for literature reviews
- **Emerging Fields**: Focus on very recent publications

## Data Interpretation

### Citation Metrics

- **High Citations (>1000)**: Landmark papers, foundational work
- **Medium Citations (100-1000)**: Solid contributions, good impact
- **Low Citations (<100)**: Newer papers, niche topics, or limited impact

### Author Metrics

- **H-index**: Measures both productivity and citation impact
  - 10-20: Early career researcher
  - 20-40: Established researcher
  - 40+: Senior, highly influential researcher

- **Works Count**: Indicates research productivity
- **Citation Count**: Shows overall impact

### Concept Levels

- **Level 0**: Broadest categories (e.g., "Science")
- **Level 1**: Major disciplines (e.g., "Computer Science")
- **Level 2**: Sub-disciplines (e.g., "Artificial Intelligence")
- **Level 3-5**: Increasingly specific topics

## Common Use Cases

### 1. Literature Review

```python
# Systematic search for recent papers
papers = await search_papers({
    "query": "systematic review machine learning healthcare",
    "from_publication_date": "2020-01-01",
    "results_count": 50
})
```

### 2. Expert Identification

```python
# Find leading researchers in a field
authors = await search_authors({
    "query": "deep learning computer vision",
    "results_count": 20
})
```

### 3. Research Trend Analysis

```python
# Explore emerging concepts
concepts = await search_concepts({
    "query": "large language models",
    "results_count": 15
})
```

### 4. Citation Tracking

```python
# Get detailed paper information
paper = await get_publication({
    "doi": "10.1038/nature12373"
})
```

### 5. Collaboration Discovery

Use author searches to:
- Find potential collaborators
- Identify research networks
- Explore institutional connections

## Tips and Best Practices

### Search Optimization

1. **Start Broad, Then Narrow:**
   - Begin with general terms
   - Refine based on initial results
   - Use specific terminology for precision

2. **Use Multiple Search Terms:**
   - Combine synonyms: `"AI artificial intelligence"`
   - Include variations: `"ML machine learning"`

3. **Leverage Date Filters:**
   - Use date ranges for temporal analysis
   - Focus on recent work for current state
   - Include historical work for comprehensive reviews

### Result Analysis

1. **Cross-Reference Sources:**
   - Verify important papers through multiple searches
   - Check author credentials and affiliations
   - Look for peer review and publication venue quality

2. **Consider Context:**
   - Understand citation context (positive vs. critical)
   - Consider research methodology and sample sizes
   - Evaluate relevance to your specific needs

3. **Track Trends:**
   - Monitor citation growth over time
   - Identify emerging topics and declining areas
   - Follow influential authors' recent work

### Error Handling

1. **No Results Found:**
   - Try broader search terms
   - Check spelling and terminology
   - Remove date filters temporarily

2. **Too Many Results:**
   - Add more specific terms
   - Use date filters to narrow scope
   - Reduce results count for focused analysis

3. **API Errors:**
   - Wait and retry (rate limiting)
   - Check DOI format for publication lookups
   - Verify internet connectivity

### Performance Tips

1. **Batch Searches:**
   - Group related queries
   - Use reasonable result counts (10-20 for exploration)
   - Implement delays between large requests

2. **Cache Results:**
   - Save important searches locally
   - Export results for offline analysis
   - Keep track of useful DOIs and author IDs

3. **Monitor Usage:**
   - Be mindful of API rate limits
   - Use specific searches rather than broad exploration
   - Consider local caching for repeated queries
