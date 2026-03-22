"""
XBRL Document Conversion - Web UI

A simple web interface for testing XBRL document conversion.
Provides an easy-to-use interface for uploading XBRL files and viewing results.

Usage:
    python examples/web_ui.py

Then open http://localhost:5000 in your browser.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import json
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Flask, render_template_string, request, jsonify, send_file
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask")
    sys.exit(1)

from xbrl_agent import create_agent_from_taxonomy, XBRLConversionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent.parent / 'uploads'
app.config['OUTPUT_FOLDER'] = Path(__file__).parent.parent / 'output'

# Ensure directories exist
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

# Global agent (will be initialized on first use)
agent: Optional[XBRLConversionAgent] = None

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XBRL Document Conversion - Web UI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="file"],
        input[type="text"],
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="file"]:focus,
        input[type="text"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
        }
        
        .result-section {
            margin-bottom: 20px;
        }
        
        .result-section h3 {
            color: #667eea;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .result-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .result-item strong {
            color: #333;
        }
        
        .download-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .download-btn {
            background: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .download-btn:hover {
            background: #218838;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #f5c6cb;
            margin-bottom: 20px;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #c3e6cb;
            margin-bottom: 20px;
        }
        
        .info-box {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #bee5eb;
            margin-bottom: 20px;
        }
        
        .structure-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .structure-table th,
        .structure-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .structure-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        .text-preview {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            max-height: 200px;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.6;
            margin-top: 10px;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 XBRL Document Conversion</h1>
            <p class="subtitle">Upload and convert XBRL documents to multiple formats</p>
        </div>
        
        <div class="card">
            <div class="info-box">
                <strong>ℹ️ Instructions:</strong>
                <ol style="margin-left: 20px; margin-top: 10px;">
                    <li>Configure taxonomy settings below</li>
                    <li>Upload your XBRL instance document (.xml file)</li>
                    <li>Click "Convert Document" to process</li>
                    <li>Download results in your preferred format</li>
                </ol>
            </div>
            
            <form id="conversionForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="taxonomyDir">Taxonomy Directory:</label>
                    <input type="text" id="taxonomyDir" name="taxonomyDir" 
                           value="../_data/xbrl/mlac-taxonomy" required>
                </div>
                
                <div class="form-group">
                    <label for="taxonomyPackage">Taxonomy Package (optional):</label>
                    <input type="text" id="taxonomyPackage" name="taxonomyPackage" 
                           value="../_data/xbrl/mlac-taxonomy/taxonomy_package.zip">
                </div>
                
                <div class="form-group">
                    <label for="xbrlFile">XBRL Instance Document:</label>
                    <input type="file" id="xbrlFile" name="xbrlFile" accept=".xml" required>
                </div>
                
                <div class="form-group">
                    <label for="exportFormats">Export Formats:</label>
                    <select id="exportFormats" name="exportFormats" multiple size="3">
                        <option value="markdown" selected>Markdown</option>
                        <option value="json" selected>JSON</option>
                        <option value="html">HTML</option>
                    </select>
                    <small style="color: #666;">Hold Ctrl/Cmd to select multiple</small>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">Convert Document</button>
            </form>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Converting XBRL document... This may take a moment.</p>
        </div>
        
        <div class="results" id="results">
            <div class="card">
                <div class="success">
                    ✓ Conversion completed successfully!
                </div>
                
                <div class="result-section">
                    <h3>Document Information</h3>
                    <div class="result-item">
                        <strong>Document Name:</strong> <span id="docName"></span><br>
                        <strong>Status:</strong> <span id="docStatus"></span><br>
                        <strong>Total Items:</strong> <span id="docItems"></span>
                    </div>
                </div>
                
                <div class="result-section">
                    <h3>Document Structure</h3>
                    <table class="structure-table" id="structureTable">
                        <thead>
                            <tr>
                                <th>Item Type</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody id="structureBody"></tbody>
                    </table>
                </div>
                
                <div class="result-section">
                    <h3>Sample Text Content</h3>
                    <div class="text-preview" id="textPreview"></div>
                </div>
                
                <div class="result-section">
                    <h3>Download Results</h3>
                    <div class="download-links" id="downloadLinks"></div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>XBRL Document Conversion Agent | Built with Docling & Flask</p>
        </div>
    </div>
    
    <script>
        document.getElementById('conversionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            // Show loading, hide results
            submitBtn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                // Display results
                document.getElementById('docName').textContent = data.document_name;
                document.getElementById('docStatus').textContent = data.conversion_status;
                document.getElementById('docItems').textContent = data.total_items || 'N/A';
                
                // Structure table
                const structureBody = document.getElementById('structureBody');
                structureBody.innerHTML = '';
                if (data.structure) {
                    for (const [type, count] of Object.entries(data.structure)) {
                        const row = structureBody.insertRow();
                        row.insertCell(0).textContent = type;
                        row.insertCell(1).textContent = count;
                    }
                }
                
                // Text preview
                const textPreview = document.getElementById('textPreview');
                if (data.sample_text && data.sample_text.length > 0) {
                    textPreview.innerHTML = data.sample_text
                        .map((text, i) => `<p><strong>${i + 1}.</strong> ${text}</p>`)
                        .join('');
                } else {
                    textPreview.textContent = 'No text content available';
                }
                
                // Download links
                const downloadLinks = document.getElementById('downloadLinks');
                downloadLinks.innerHTML = '';
                if (data.output_files) {
                    for (const [format, path] of Object.entries(data.output_files)) {
                        const link = document.createElement('a');
                        link.href = `/download/${encodeURIComponent(path)}`;
                        link.className = 'download-btn';
                        link.textContent = `Download ${format.toUpperCase()}`;
                        downloadLinks.appendChild(link);
                    }
                }
                
                results.style.display = 'block';
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/convert', methods=['POST'])
def convert():
    """Handle XBRL document conversion."""
    global agent
    
    try:
        # Get form data
        taxonomy_dir = request.form.get('taxonomyDir')
        taxonomy_package = request.form.get('taxonomyPackage')
        export_formats = request.form.getlist('exportFormats')
        
        # Get uploaded file
        if 'xbrlFile' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['xbrlFile']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        upload_path = app.config['UPLOAD_FOLDER'] / file.filename
        file.save(upload_path)
        
        # Create or reuse agent
        if agent is None:
            logger.info(f"Creating agent with taxonomy: {taxonomy_dir}")
            agent = create_agent_from_taxonomy(
                taxonomy_dir=Path(taxonomy_dir),
                taxonomy_package=Path(taxonomy_package) if taxonomy_package else None,
                output_dir=app.config['OUTPUT_FOLDER']
            )
        
        # Process XBRL file
        logger.info(f"Processing XBRL file: {upload_path}")
        
        # Add timestamp to output filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base_name = f"{Path(file.filename).stem}_{timestamp}"
        
        # Update agent's export formats if needed
        agent.config.export_formats = export_formats if export_formats else ["markdown", "json"]
        
        result = agent.process_xbrl_file(
            xbrl_path=upload_path,
            output_base_name=output_base_name,
            analyze=True
        )
        
        # Calculate total items
        total_items = sum(result.get('structure', {}).values())
        result['total_items'] = total_items
        
        # Convert absolute paths to relative paths for download links
        if 'output_files' in result:
            relative_files = {}
            for fmt, abs_path in result['output_files'].items():
                # Get path relative to project root
                rel_path = Path(abs_path).relative_to(Path(__file__).parent.parent)
                relative_files[fmt] = str(rel_path)
            result['output_files'] = relative_files
        
        # Clean up uploaded file
        upload_path.unlink()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download(filename):
    """Download converted file."""
    try:
        # filename is already relative to project root
        file_path = Path(__file__).parent.parent / filename
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=file_path.name)
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    """Run the web UI."""
    print("\n" + "="*60)
    print("XBRL Document Conversion - Web UI")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and navigate to: http://localhost:5002")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5002, debug=False)


if __name__ == '__main__':
    main()

# Made with Bob
