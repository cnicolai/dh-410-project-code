# Character Network Analysis Project

This project processes text files containing the Aubrey-Maturin novels to extract character relationships and create a network visualization.

## Project Components

### 1. Person Name Recognition
The `extract-persons.py` script:
- Takes text files from individual chapters as input
- Performs named entity recognition to extract person names
- Filters out persons that appear infrequently in the canon
- Outputs a list of persons in JSON format

### 2. Person Name Encoding
The `encode-persons.py` script:
- Takes text files from individual chapters as input
- Uses a list of person names and XML tags from `persons.json`, created in step 1
- Adds TEI-compliant XML tags around character names
- Combines all chapters into a single XML document with proper TEI structure for books and chapters

### 3. Network Building
The `build_network.py` script:
- Processes the XML corpus created in step 2
- Uses a sliding window approach to detect character co-occurrences 
- Creates a network where:
  - Nodes represent characters
  - Edges represent co-occurrences within the specified window size
- Exports the network in GEXF format for visualization in Gephi
