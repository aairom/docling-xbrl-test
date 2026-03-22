# XBRL Document Conversion

This example demonstrates how to parse XBRL (eXtensible Business Reporting Language) documents using Docling, completely offline.

XBRL is a standard XML-based format used globally by companies, regulators, and financial institutions for exchanging business and financial information in a structured, machine-readable format. It's widely adopted for regulatory filings (e.g., SEC filings in the US).

## What you'll learn

- How to configure Docling to parse XBRL documents offline
- How to provide a local taxonomy package for XBRL validation
- How to extract structured data from XBRL instance documents
- How to export XBRL content to various formats (Markdown, JSON, etc.)

The data to run this notebook has been fetched from the [SEC's Electronic Data Gathering, Analysis, and Retrieval (EDGAR)](https://www.sec.gov/search-filings) system.

## Setup

Install Docling with XBRL support:

```

/Users/ceb/git/docling-3/.venv/bin/python: No module named pip
Note: you may need to restart the kernel to use updated packages.
```

## Download Sample XBRL Data

For this example, we'll use a sample XBRL instance document and its taxonomy. In a real scenario, you would have your own XBRL files and taxonomy packages.

We'll download the test data from the Docling repository:

```

Downloading XBRL instance file...
Downloaded: xbrl_data/mlac-20251231.xml
Downloading taxonomy files...
  Downloaded: mlac-20251231.xsd
  Downloaded: mlac-20251231_cal.xml
  Downloaded: mlac-20251231_def.xml
  Downloaded: mlac-20251231_lab.xml
  Downloaded: mlac-20251231_pre.xml
Downloading taxonomy package...
  Downloaded: taxonomy_package.zip

All files downloaded successfully!
```

## Configure XBRL Backend

To parse XBRL documents offline, we need to:

1. Enable local resource fetching (for taxonomy files)
2. Disable remote resource fetching (for offline operation)
3. Provide the path to the local taxonomy directory

```

XBRL converter configured successfully!
```

💡 Because the converter must read the supporting taxonomy files, set the `enable_local_fetch` option to **True** in the XBRL backend settings.
💡 In addition to the XBRL report's own taxonomy files, you need a *taxonomy package*-a bundle containing URL remappings that enables completely offline parsing. If you prefer not to supply a taxonomy package, omit it and set `enable_remote_fetch` to **True** in the XBRL backend settings. The backend will fetch the web‑referenced files from the remote publishers and cache them locally for reuse.

## Convert XBRL Document

Now we can convert the XBRL instance document. The converter will:

- Parse the XBRL instance file
- Validate it against the local taxonomy
- Extract metadata, text blocks, and numeric facts
- Convert everything to a unified DoclingDocument representation

```

Converting XBRL document: xbrl_data/mlac-20251231.xml

Conversion successful!
Document name: mlac-20251231
Number of items: 292
```

## Inspect Document Structure

Let's examine the structure of the converted document:

```

Document structure:
  text: 267
  table: 23
  title: 1
  key_value_region: 1
```

## View Sample Content

Let's look at some of the extracted content:

```

Sample text content:

- None

- We are a special purpose acquisition company with no business operations. Since our initial public offering, our sole business activity has been identifying and evaluating suitable acquisition transac...

- We depend on digital technologies, including information systems, infrastructure and cloud applications and services, including those of third parties with which we may deal. Sophisticated and deliber...
```

## View Key-Value Pairs

XBRL numeric facts are extracted as key-value pairs:

```

Total key-value pairs extracted: 319

EntityPublicFloat -> 239160600
EntityCommonStockSharesOutstanding -> 23805000
EntityCommonStockSharesOutstanding -> 7187500
Cash -> 452680
Cash -> 1383392
OtherPrepaidExpenseCurrent -> 16840
OtherPrepaidExpenseCurrent -> 23669
PrepaidInsurance -> 87776
PrepaidInsurance -> 92500
AssetsCurrent -> 557296
```

💡 The current backend implementation flattens all key‑value pairs in an XBRL report. Future improvements will preserve the rich taxonomy of those data points.

## Export to Markdown

Export the document to Markdown format for easy reading:

```

Markdown export (first 2000 characters):

# 10-K MOUNTAIN LAKE ACQUISITION CORP. 2025-12-31

None

We are a special purpose acquisition company with no business operations. Since our initial public offering, our sole business activity has been identifying and evaluating suitable acquisition transaction candidates. Therefore, we do not consider that we face significant cybersecurity risk and have not adopted any cybersecurity risk management program or formal processes for assessing cybersecurity risk.

We depend on digital technologies, including information systems, infrastructure and cloud applications and services, including those of third parties with which we may deal. Sophisticated and deliberate attacks on, or security breaches in, our information systems or infrastructure, or the information systems or infrastructure of third parties or the cloud, could lead to corruption or misappropriation of our assets, proprietary information and sensitive or confidential data. Because of our reliance on the technologies of third parties, we also depend upon the personnel and the processes of third parties to protect against cybersecurity threats. In the event of a cybersecurity incident impacting us, the management team will report to the board of directors and provide updates on the management team's incident response plan for addressing and mitigating any risks associated with the cybersecurity incident. As an early-stage company without significant investments in data security protection, there can be no assurance that we will have sufficient resources to adequately protect against, or to investigate and remediate any vulnerability to, cyber incidents. It is possible that any of these occurrences, or a combination of them, could have adverse consequences on our business and lead to financial loss.

As of the date of this Report, we have not identified any risks from cybersecurity threats, including as a result of any previous cybersecurity incidents, that we believe have, or are likely to, materially affect 

...

Full markdown saved to: xbrl_data/output.md
```

## Export to JSON

Export the complete document structure to JSON:

```

Document exported to JSON: xbrl_data/output.json
File size: 1538.26 KB
```

## Summary

In this example, we demonstrated:

✅ How to configure Docling for offline XBRL parsing
✅ How to provide a local taxonomy for XBRL validation
✅ How to convert XBRL instance documents to DoclingDocument
✅ How to extract metadata, text blocks, and numeric facts
✅ How to export XBRL content to Markdown and JSON formats

### Key Points

- **Offline operation**: By setting `enable_remote_fetch=False`, all processing happens locally
- **Taxonomy support**: The local taxonomy directory should contain all necessary schema and linkbase files
- **Structured extraction**: XBRL numeric facts are extracted as key-value pairs with graph representation
- **Text blocks**: HTML text blocks in XBRL are converted to structured content

### Note on Future Changes

⚠️ The current implementation uses `DoclingDocument`'s `GraphData` object to represent key-value pairs. This design will change in a future release of the `docling-core` library.