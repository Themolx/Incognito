# PNG Converter for Nuke

### **Description**
A simple Nuke tool that creates a preconfigured Write node for PNG RGBA output with specific colorspace settings and naming convention.

### **Features**
- Automatically creates Write node configured for PNG output
- Sets RGBA channels
- Configures color_picking colorspace
- Adds "_png_sRGB" suffix to filenames
- Creates output directories automatically
- Disables hash checking for better performance

### **Installation**
1. Download the tool from: [PNG_Converter.nk](https://github.com/Themolx/Incognito/blob/main/Nuke/PNG_Converter.nk)
2. Copy the node to your Nuke toolbar or paste directly into your script

### **Usage Instructions**
1. Add PNG_Converter node to your node graph
2. Connect any node to its input
3. Click "Create PNG Write" button
4. A new Write node will be created below with all settings configured

### **Technical Details**
- The Write node will be configured with:
  ```
  channels: rgba
  file_type: png
  colorspace: color_picking
  create_directories: true
  checkHashOnRead: false
  ```
- If connected to a Read node, it will automatically use the input filename as base

### **Requirements**
- Nuke 14.0 or higher
- Standard Nuke Write node license

### **Known Issues**
- None currently reported

### **Version History**
- v1.0: Initial release

### **Author**
- Created by: Martin Tomek
- GitHub: [https://github.com/Themolx](https://github.com/Themolx)

### **Support**
For issues and feature requests, please visit:
[https://github.com/Themolx/Incognito/issues](https://github.com/Themolx/Incognito/issues)
