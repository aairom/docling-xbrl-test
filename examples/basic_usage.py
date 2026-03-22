"""
Basic XBRL Conversion Example

This script demonstrates basic usage of the XBRL Conversion Agent
to convert XBRL documents and export them to various formats.
"""

from pathlib import Path
import sys

# Add parent directory to path to import xbrl_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from xbrl_agent import create_agent_from_taxonomy, XBRLConversionConfig, XBRLConversionAgent


def example_1_basic_conversion():
    """Example 1: Basic XBRL document conversion with local taxonomy."""
    print("\n" + "="*60)
    print("Example 1: Basic XBRL Conversion")
    print("="*60)
    
    # Create agent with taxonomy configuration
    agent = create_agent_from_taxonomy(
        taxonomy_dir=Path("../_data/xbrl/mlac-taxonomy"),
        taxonomy_package=Path("../_data/xbrl/mlac-taxonomy/taxonomy_package.zip"),
        output_dir=Path("./output")
    )
    
    # Convert XBRL document
    xbrl_file = Path("../_data/xbrl/mlac-20251231.xml")
    result = agent.process_xbrl_file(xbrl_file)
    
    # Display results
    print(f"\n✓ Conversion Status: {result['conversion_status']}")
    print(f"✓ Document Name: {result['document_name']}")
    print(f"\nDocument Structure:")
    for item_type, count in result['structure'].items():
        print(f"  - {item_type}: {count}")
    
    print(f"\nOutput Files:")
    for fmt, path in result['output_files'].items():
        print(f"  - {fmt}: {path}")
    
    print(f"\nSample Text Content:")
    for i, text in enumerate(result['sample_text'][:3], 1):
        print(f"  {i}. {text[:100]}...")


def example_2_custom_configuration():
    """Example 2: Custom configuration with specific export formats."""
    print("\n" + "="*60)
    print("Example 2: Custom Configuration")
    print("="*60)
    
    # Create custom configuration
    config = XBRLConversionConfig(
        enable_local_fetch=True,
        enable_remote_fetch=False,
        taxonomy_dir=Path("../_data/xbrl/grve-taxonomy"),
        taxonomy_package=Path("../_data/xbrl/grve-taxonomy/taxonomy_package.zip"),
        output_dir=Path("./output/grve"),
        export_formats=["markdown", "json", "html"]  # Export to all formats
    )
    
    # Create agent with custom config
    agent = XBRLConversionAgent(config)
    
    # Convert document
    xbrl_file = Path("../_data/xbrl/grve_10q_htm.xml")
    result = agent.process_xbrl_file(xbrl_file, output_base_name="grve_report")
    
    print(f"\n✓ Processed: {result['input_file']}")
    print(f"✓ Exported to {len(result['output_files'])} formats")


def example_3_step_by_step():
    """Example 3: Step-by-step conversion with detailed analysis."""
    print("\n" + "="*60)
    print("Example 3: Step-by-Step Conversion")
    print("="*60)
    
    # Setup agent
    agent = create_agent_from_taxonomy(
        taxonomy_dir=Path("../_data/xbrl/mlac-taxonomy"),
        taxonomy_package=Path("../_data/xbrl/mlac-taxonomy/taxonomy_package.zip")
    )
    
    # Step 1: Convert document
    print("\nStep 1: Converting XBRL document...")
    xbrl_file = Path("../_data/xbrl/mlac-20251231.xml")
    conv_result = agent.convert_document(xbrl_file)
    document = conv_result.document
    print(f"✓ Document converted: {document.name}")
    
    # Step 2: Analyze structure
    print("\nStep 2: Analyzing document structure...")
    structure = agent.get_document_structure(document)
    print(f"✓ Found {sum(structure.values())} total items")
    
    # Step 3: Extract key-value pairs
    print("\nStep 3: Extracting numeric facts...")
    kv_pairs = agent.extract_key_value_pairs(document)
    print(f"✓ Extracted {len(kv_pairs)} key-value pairs")
    if kv_pairs:
        print(f"  Sample: {kv_pairs[0]}")
    
    # Step 4: Extract text content
    print("\nStep 4: Extracting text content...")
    texts = agent.extract_text_content(document, max_items=3)
    print(f"✓ Extracted {len(texts)} text samples")
    
    # Step 5: Export to formats
    print("\nStep 5: Exporting to multiple formats...")
    output_files = agent.export_document(document, "mlac_detailed")
    for fmt, path in output_files.items():
        print(f"✓ Exported {fmt}: {path}")


def example_4_batch_processing():
    """Example 4: Batch processing multiple XBRL files."""
    print("\n" + "="*60)
    print("Example 4: Batch Processing")
    print("="*60)
    
    # Setup agent
    agent = create_agent_from_taxonomy(
        taxonomy_dir=Path("../_data/xbrl/mlac-taxonomy"),
        taxonomy_package=Path("../_data/xbrl/mlac-taxonomy/taxonomy_package.zip"),
        output_dir=Path("./output/batch")
    )
    
    # List of XBRL files to process
    xbrl_files = [
        Path("../_data/xbrl/mlac-20251231.xml"),
        # Add more files here
    ]
    
    results = []
    for xbrl_file in xbrl_files:
        if xbrl_file.exists():
            print(f"\nProcessing: {xbrl_file.name}")
            try:
                result = agent.process_xbrl_file(xbrl_file, analyze=False)
                results.append(result)
                print(f"✓ Success: {result['document_name']}")
            except Exception as e:
                print(f"✗ Error: {e}")
    
    print(f"\n✓ Batch processing complete: {len(results)}/{len(xbrl_files)} files")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("XBRL Document Conversion - Usage Examples")
    print("="*60)
    
    try:
        # Run examples
        example_1_basic_conversion()
        example_2_custom_configuration()
        example_3_step_by_step()
        example_4_batch_processing()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except ImportError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install docling[xbrl]")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob

"""
XBRL Conversion Examples

This file contains multiple examples of using the XBRL Conversion Agent.

For a web-based UI, run:
    python examples/web_ui.py

Then open http://localhost:5000 in your browser.
"""
