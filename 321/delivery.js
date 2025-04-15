// Combined After Effects Script
// This script:
// 1. Sets all compositions to start at frame 1001
// 2. Sets all compositions to 30 fps
// 3. Sets all compositions to 4096x4096 pixels
// 4. Fits all layers within each composition to the composition size
// 5. Renames all footage items to match their original filenames

(function() {
    // Check if a project is open
    if (app.project === null) {
        alert("Please open a project first.");
        return;
    }

    app.beginUndoGroup("Set Comps and Fit Layers");
    
    var totalComps = 0;
    var modifiedComps = 0;
    var renamedFootage = 0;
    
    // Rename all footage items to match their original filenames
    for (var i = 1; i <= app.project.numItems; i++) {
        var item = app.project.item(i);
        
        // Check if the item is a footage item with a source file
        if (item instanceof FootageItem && item.file !== null) {
            var originalFilename = item.file.displayName;
            item.name = originalFilename;
            renamedFootage++;
        }
    }
    
    // Loop through all items in the project
    for (var i = 1; i <= app.project.numItems; i++) {
        var item = app.project.item(i);
        
        // Check if the item is a composition
        if (item instanceof CompItem) {
            totalComps++;
            
            // Set the start frame to exactly 1001
            // The most reliable way to set this across AE versions
            item.displayStartFrame = 1001;
            
            // Set the frame rate to 30
            item.frameRate = 30;
            
            // Store original dimensions for reporting
            var originalWidth = item.width;
            var originalHeight = item.height;
            
            // Set composition size to 4096x4096
            item.width = 4096;
            item.height = 4096;
            
            // Process layers in the composition to fit the new size
            processComp(item);
            
            modifiedComps++;
        }
    }
    
    app.endUndoGroup();
    
    // Display a summary alert
    alert("Modified " + modifiedComps + " compositions out of " + totalComps + " total compositions.\n\n" +
          "• Start frame set to: 1001\n" +
          "• Frame rate set to: 30 fps\n" +
          "• Composition size set to: 4096x4096\n" +
          "• All layers fit to their compositions\n\n" +
          "• Renamed " + renamedFootage + " footage items to match their source filenames");
    
    // Main function to process a composition
    function processComp(comp) {
        // Get the composition dimensions
        var compWidth = comp.width;
        var compHeight = comp.height;
        
        // Loop through all layers in the composition
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            
            // Check if the layer is a nested composition
            if (layer.source instanceof CompItem) {
                // We don't process nested comps here as they'll be handled in the main loop
                // Just make sure this layer fits the current comp
            }
            
            // Skip adjustment layers, null objects, lights, and cameras
            if (layer.adjustmentLayer || 
                layer instanceof CameraLayer || 
                layer instanceof LightLayer || 
                layer.nullLayer) {
                continue;
            }
            
            // Get the layer's source dimensions
            var layerWidth, layerHeight;
            
            if (layer.source && layer.source.width && layer.source.height) {
                layerWidth = layer.source.width;
                layerHeight = layer.source.height;
            } else {
                // Skip if we can't determine dimensions
                continue;
            }
            
            // Calculate the scale factors needed to fit the layer to comp
            var scaleX = (compWidth / layerWidth) * 100;
            var scaleY = (compHeight / layerHeight) * 100;
            
            // Use the smaller scale to maintain aspect ratio
            var scaleFactor = Math.min(scaleX, scaleY);
            
            // Set the new scale
            layer.property("Scale").setValue([scaleFactor, scaleFactor, 100]);
            
            // Center the layer in the composition
            layer.property("Position").setValue([compWidth/2, compHeight/2]);
        }
    }
})();
